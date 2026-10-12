"""
COSC 611 Big Data Analytics - Midterm, Question 2
Hypothesis testing on Apache Spark with real datasets (from R's `datasets` package,
CSV copies from the Rdatasets archive, in data/):

  * Chi-square test of independence -> UCBAdmissions (UC Berkeley graduate
    admissions, Fall 1973; Bickel, Hammel & O'Connell 1975), pyspark.ml.stat.ChiSquareTest
  * Student's t-test                 -> sleep (Cushny & Peebles 1905, the data
    "Student" used in his 1908 paper). Spark has no t-test class, so the statistic
    is computed from distributed aggregates; the p-value comes from scipy.stats.t
  * F-test for equality of variances -> ToothGrowth (Crampton 1947), OJ vs VC
  * One-way ANOVA F-test             -> PlantGrowth (Dobson 1983),
    org.apache.spark.ml.stat.ANOVATest (Scala class called through the JVM, as
    PySpark has no Python wrapper for it)

Every Spark result is cross-checked against scipy.stats.

Run from the cosc611-midterm folder:  spark-submit code/q2_hypothesis_tests.py
"""
import os

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.stat import ChiSquareTest
from scipy import stats

ALPHA = 0.05
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
spark = (SparkSession.builder.appName("Q2-HypothesisTesting")
         .master("local[*]").getOrCreate())
spark.sparkContext.setLogLevel("ERROR")


def load(name):
    return spark.read.csv(os.path.join(DATA, name + ".csv"), header=True,
                          inferSchema=True).drop("rownames")


def decide(p):
    return "REJECT H0" if p < ALPHA else "FAIL TO REJECT H0"


# ===========================================================================
# 1. CHI-SQUARE TEST OF INDEPENDENCE - UCBAdmissions
#    H0: admission outcome is independent of gender.  H1: they are associated.
# ===========================================================================
print("=" * 72)
print("1. CHI-SQUARE TEST OF INDEPENDENCE  (UCBAdmissions: gender vs admission)")
print("=" * 72)
ucb = load("UCBAdmissions")
print("Raw data (frequency per Admit x Gender x Dept):")
ucb.orderBy("Dept", "Gender", "Admit").show(24)

table = (ucb.groupBy("Gender").pivot("Admit", ["Admitted", "Rejected"])
         .agg(F.sum("Freq")).orderBy("Gender"))
print("Observed 2x2 table, summed over the six departments:")
table.show()

N = ucb.agg(F.sum("Freq")).first()[0]
cell = ucb.groupBy("Gender", "Admit").agg(F.sum("Freq").alias("O"))
rtot = cell.groupBy("Gender").agg(F.sum("O").alias("rt"))
ctot = cell.groupBy("Admit").agg(F.sum("O").alias("ct"))
chi = (cell.join(rtot, "Gender").join(ctot, "Admit")
       .withColumn("E", F.col("rt") * F.col("ct") / N)
       .withColumn("contrib", (F.col("O") - F.col("E")) ** 2 / F.col("E")))
print(f"N = {N}. Expected counts E = row total x column total / N and (O-E)^2/E:")
chi.select("Gender", "Admit", "O", "rt", "ct", F.round("E", 3).alias("E"),
           F.round("contrib", 4).alias("contrib")).orderBy("Gender", "Admit").show()
chi_stat = chi.agg(F.sum("contrib")).first()[0]
print(f"Manual chi-square statistic = {chi_stat:.4f}, df = (2-1)(2-1) = 1")

# Spark MLlib ChiSquareTest needs one row per applicant: expand the frequencies
people = (ucb.withColumn("i", F.explode(F.sequence(F.lit(1), F.col("Freq"))))
          .select(F.when(F.col("Admit") == "Admitted", 1.0).otherwise(0.0).alias("label"),
                  F.when(F.col("Gender") == "Male", 1.0).otherwise(0.0).alias("male"),
                  "Dept"))
print(f"Expanded to {people.count()} applicant rows for ChiSquareTest")
vec = VectorAssembler(inputCols=["male"], outputCol="features").transform(people)
r = ChiSquareTest.test(vec, "features", "label").head()
print(f"Spark ChiSquareTest: statistic = {r.statistics[0]:.4f}, "
      f"df = {r.degreesOfFreedom[0]}, p-value = {r.pValues[0]:.3e}")
obs = [[x.Admitted, x.Rejected] for x in table.collect()]
sc_chi = stats.chi2_contingency(obs, correction=False)
print(f"scipy check:          statistic = {sc_chi[0]:.4f}, p-value = {sc_chi[1]:.3e}")
print(f"Critical value chi2(0.05, 1) = {stats.chi2.ppf(0.95, 1):.4f}")
print("Decision:", decide(r.pValues[0]))
rates = (ucb.groupBy("Gender").agg(
    (F.sum(F.when(F.col("Admit") == "Admitted", F.col("Freq"))) / F.sum("Freq"))
    .alias("admit_rate")).orderBy("Gender"))
print("Admission rate by gender (overall):")
rates.show()

# Same test inside each department (Simpson's paradox)
print("Same test within each department (Spark ChiSquareTest per Dept):")
print(f"  {'Dept':4s} {'male rate':>9s} {'female rate':>11s} {'chi2':>9s} {'p-value':>10s}")
for d in sorted(x.Dept for x in ucb.select("Dept").distinct().collect()):
    sub = vec.where(F.col("Dept") == d)
    rd = ChiSquareTest.test(sub, "features", "label").head()
    mr = sub.where("male = 1").agg(F.mean("label")).first()[0]
    fr = sub.where("male = 0").agg(F.mean("label")).first()[0]
    print(f"  {d:4s} {mr:9.3f} {fr:11.3f} {rd.statistics[0]:9.3f} {rd.pValues[0]:10.4f}"
          f"  {decide(rd.pValues[0])}")

# ===========================================================================
# 2. STUDENT'S t-TEST - sleep data
#    Extra hours of sleep for 10 patients under drug 1 and drug 2.
#    H0: mu_1 = mu_2.  H1: mu_1 != mu_2 (two-tailed).
# ===========================================================================
print()
print("=" * 72)
print("2. STUDENT'S t-TEST  (sleep: extra hours of sleep, drug 1 vs drug 2)")
print("=" * 72)
sleep = load("sleep")
sleep.groupBy("ID").pivot("group", [1, 2]).agg(F.first("extra")) \
    .withColumnRenamed("1", "drug1").withColumnRenamed("2", "drug2") \
    .withColumn("diff", F.round(F.col("drug1") - F.col("drug2"), 2)).orderBy("ID").show()

summ = (sleep.groupBy("group")
        .agg(F.count("extra").alias("n"), F.mean("extra").alias("mean"),
             F.var_samp("extra").alias("var"), F.stddev_samp("extra").alias("sd"))
        .orderBy("group"))
summ.show()
s1, s2 = summ.collect()
n1, n2 = s1.n, s2.n

print("(a) Independent two-sample t-test (pooled / equal variances):")
sp2 = ((n1 - 1) * s1["var"] + (n2 - 1) * s2["var"]) / (n1 + n2 - 2)
se = (sp2 * (1 / n1 + 1 / n2)) ** 0.5
t = (s1["mean"] - s2["mean"]) / se
dof = n1 + n2 - 2
p_t = 2 * stats.t.sf(abs(t), dof)
print(f"  pooled variance sp^2 = {sp2:.4f}, standard error = {se:.4f}")
print(f"  Spark-computed t = {t:.4f}, df = {dof}, two-tailed p-value = {p_t:.5f}")
g1 = [x.extra for x in sleep.where("group = 1").orderBy("ID").collect()]
g2 = [x.extra for x in sleep.where("group = 2").orderBy("ID").collect()]
sc_t = stats.ttest_ind(g1, g2, equal_var=True)
print(f"  scipy check:      t = {sc_t.statistic:.4f}, p-value = {sc_t.pvalue:.5f}")
print(f"  Critical value t(0.025, {dof}) = {stats.t.ppf(0.975, dof):.4f}")
print("  Decision:", decide(p_t))

print("(b) Paired t-test (the same 10 patients took both drugs - the correct design):")
d = (sleep.groupBy("ID").pivot("group", [1, 2]).agg(F.first("extra"))
     .select((F.col("1") - F.col("2")).alias("d")))
ds = d.agg(F.count("d").alias("n"), F.mean("d").alias("m"), F.stddev_samp("d").alias("s")).first()
tp = ds.m / (ds.s / ds.n ** 0.5)
pp = 2 * stats.t.sf(abs(tp), ds.n - 1)
print(f"  mean difference = {ds.m:.4f}, sd of differences = {ds.s:.4f}")
print(f"  Spark-computed t = {tp:.4f}, df = {ds.n - 1}, two-tailed p-value = {pp:.6f}")
sc_p = stats.ttest_rel(g1, g2)
print(f"  scipy check:      t = {sc_p.statistic:.4f}, p-value = {sc_p.pvalue:.6f}")
print(f"  Critical value t(0.025, {ds.n - 1}) = {stats.t.ppf(0.975, ds.n - 1):.4f}")
print("  Decision:", decide(pp))

# ===========================================================================
# 3a. F-TEST FOR EQUALITY OF TWO VARIANCES - ToothGrowth
#     Odontoblast length of 60 guinea pigs; vitamin C given as orange juice (OJ)
#     or ascorbic acid (VC).  H0: sigma_OJ^2 = sigma_VC^2.  H1: they differ.
# ===========================================================================
print()
print("=" * 72)
print("3a. F-TEST FOR EQUAL VARIANCES  (ToothGrowth: tooth length, OJ vs VC)")
print("=" * 72)
tooth = load("ToothGrowth")
tooth.show(5)
v = (tooth.groupBy("supp")
     .agg(F.count("len").alias("n"), F.mean("len").alias("mean"),
          F.var_samp("len").alias("var")).orderBy("supp"))
v.show()
oj, vc = v.collect()
Fstat = oj["var"] / vc["var"]
d1, d2 = oj.n - 1, vc.n - 1
p_f = 2 * min(stats.f.sf(Fstat, d1, d2), stats.f.cdf(Fstat, d1, d2))
print(f"F = s_OJ^2 / s_VC^2 = {oj['var']:.4f} / {vc['var']:.4f} = {Fstat:.4f}, "
      f"df = ({d1}, {d2}), two-tailed p-value = {p_f:.4f}")
print(f"Critical values F(0.025; {d1}, {d2}) = {stats.f.ppf(0.025, d1, d2):.4f} and "
      f"F(0.975; {d1}, {d2}) = {stats.f.ppf(0.975, d1, d2):.4f}")
print("Decision:", decide(p_f))

# ===========================================================================
# 3b. ONE-WAY ANOVA F-TEST - PlantGrowth
#     Dried weight of plants: control and two treatments, 10 plants each.
#     H0: mu_ctrl = mu_trt1 = mu_trt2.  H1: at least one mean differs.
# ===========================================================================
print()
print("=" * 72)
print("3b. ONE-WAY ANOVA F-TEST  (PlantGrowth: dried plant weight by group)")
print("=" * 72)
plant = load("PlantGrowth")
plant.groupBy("group").agg(F.collect_list("weight").alias("weights")) \
    .orderBy("group").show(truncate=False)
gstats = plant.groupBy("group").agg(F.count("*").alias("n"), F.mean("weight").alias("m"),
                                    F.var_samp("weight").alias("var"))
gstats.orderBy("group").show()

grand = plant.agg(F.mean("weight")).first()[0]
ssb = gstats.agg(F.sum(F.col("n") * (F.col("m") - grand) ** 2)).first()[0]
ssw = (plant.join(gstats, "group")
       .agg(F.sum((F.col("weight") - F.col("m")) ** 2)).first()[0])
k, n = gstats.count(), plant.count()
msb, msw = ssb / (k - 1), ssw / (n - k)
print(f"grand mean = {grand:.4f}")
print(f"SSB = {ssb:.4f}, SSW = {ssw:.4f}")
print(f"MSB = SSB/(k-1) = {msb:.4f}, MSW = SSW/(N-k) = {msw:.4f}")
print(f"Manual F = MSB/MSW = {msb / msw:.4f}, df = ({k - 1}, {n - k})")

label = {"ctrl": 0.0, "trt1": 1.0, "trt2": 2.0}
anova_df = VectorAssembler(inputCols=["weight"], outputCol="features").transform(
    plant.withColumn("label", F.create_map(*[F.lit(x) for kv in label.items() for x in kv])
                     [F.col("group")]))
jdf = spark._jvm.org.apache.spark.ml.stat.ANOVATest.test(anova_df._jdf, "features", "label")
ar = DataFrame(jdf, spark).head()
print(f"Spark ANOVATest: F = {ar.fValues[0]:.4f}, df = ({k - 1}, {n - k}), "
      f"p-value = {ar.pValues[0]:.5f}")
groups = [[x.weight for x in plant.where(F.col("group") == g).collect()] for g in label]
sc_f = stats.f_oneway(*groups)
print(f"scipy check:     F = {sc_f.statistic:.4f}, p-value = {sc_f.pvalue:.5f}")
print(f"Critical value F(0.05; {k - 1}, {n - k}) = {stats.f.ppf(0.95, k - 1, n - k):.4f}")
print("Decision:", decide(ar.pValues[0]))

spark.stop()
