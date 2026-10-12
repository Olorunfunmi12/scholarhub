"""
COSC 611 Big Data Analytics - Midterm, Question 2
Hypothesis testing on Apache Spark: Chi-square test, Student's t-test, F-test.

  * Chi-square test of independence -> pyspark.ml.stat.ChiSquareTest
    (+ a manual contingency-table computation with DataFrame aggregations)
  * Student's two-sample t-test       -> Spark has no built-in t-test, so the
    test statistic is computed from distributed aggregates (count/mean/var);
    the p-value comes from the t distribution (scipy)
  * F-test for equality of variances  -> computed from Spark aggregates
  * One-way ANOVA F-test              -> org.apache.spark.ml.stat.ANOVATest
    (Scala class; PySpark has no Python wrapper, so it is called via the JVM)

Every Spark result is cross-checked against scipy.stats.

Run:  spark-submit q2_hypothesis_tests.py      (or: python3 q2_hypothesis_tests.py)
"""
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.ml.linalg import Vectors
from pyspark.ml.stat import ChiSquareTest
from pyspark.sql import DataFrame
from scipy import stats

ALPHA = 0.05
spark = (SparkSession.builder.appName("Q2-HypothesisTesting")
         .master("local[*]").getOrCreate())
spark.sparkContext.setLogLevel("ERROR")


def decide(p):
    return "REJECT H0" if p < ALPHA else "FAIL TO REJECT H0"


# ===========================================================================
# 1. CHI-SQUARE TEST OF INDEPENDENCE
#    Is the device a customer uses independent of whether they buy?
#    H0: device and purchase are independent.  H1: they are associated.
# ===========================================================================
print("=" * 72)
print("1. CHI-SQUARE TEST OF INDEPENDENCE  (device vs purchase)")
print("=" * 72)
# Observed counts (expanded into one row per customer = 200 rows)
observed = {("Mobile", "Yes"): 30, ("Mobile", "No"): 70,
            ("Desktop", "Yes"): 45, ("Desktop", "No"): 55}
rows = [(d, p) for (d, p), n in observed.items() for _ in range(n)]
cust = spark.createDataFrame(rows, ["device", "purchase"])

table = cust.crosstab("device", "purchase")
print("Observed contingency table (DataFrame.crosstab):")
table.show()

# Manual computation with aggregations: expected = row_total*col_total/N
N = cust.count()
cell = cust.groupBy("device", "purchase").count()
rtot = cust.groupBy("device").agg(F.count("*").alias("rt"))
ctot = cust.groupBy("purchase").agg(F.count("*").alias("ct"))
chi = (cell.join(rtot, "device").join(ctot, "purchase")
       .withColumn("expected", F.col("rt") * F.col("ct") / N)
       .withColumn("contrib", (F.col("count") - F.col("expected")) ** 2 / F.col("expected")))
print("Expected counts and (O-E)^2/E contributions:")
chi.orderBy("device", "purchase").show()
chi_stat = chi.agg(F.sum("contrib")).first()[0]
print(f"Manual chi-square statistic = {chi_stat:.4f}, df = (2-1)(2-1) = 1")

# Spark MLlib ChiSquareTest needs numeric label + feature vector
enc = cust.select(
    F.when(F.col("purchase") == "Yes", 1.0).otherwise(0.0).alias("label"),
    F.when(F.col("device") == "Mobile", 1.0).otherwise(0.0).alias("is_mobile"))
from pyspark.ml.feature import VectorAssembler
enc = VectorAssembler(inputCols=["is_mobile"], outputCol="features").transform(enc)
r = ChiSquareTest.test(enc, "features", "label").head()
print(f"Spark ChiSquareTest: statistic = {r.statistics[0]:.4f}, "
      f"df = {r.degreesOfFreedom[0]}, p-value = {r.pValues[0]:.4f}")
sc_chi = stats.chi2_contingency([[30, 70], [45, 55]], correction=False)
print(f"scipy check:          statistic = {sc_chi[0]:.4f}, p-value = {sc_chi[1]:.4f}")
print(f"Critical value chi2(0.05, 1) = {stats.chi2.ppf(0.95, 1):.4f}")
print("Decision:", decide(r.pValues[0]))

# ===========================================================================
# 2. STUDENT'S TWO-SAMPLE t-TEST (equal variances)
#    Do students taught with Method A score differently from Method B?
#    H0: mu_A = mu_B.  H1: mu_A != mu_B (two-tailed).
# ===========================================================================
print()
print("=" * 72)
print("2. STUDENT'S TWO-SAMPLE t-TEST  (exam scores, Method A vs Method B)")
print("=" * 72)
A = [78, 82, 85, 88, 75, 80, 84, 86, 79, 83]
B = [72, 75, 78, 70, 74, 77, 73, 76, 71, 74]
scores = spark.createDataFrame([("A", float(x)) for x in A] +
                               [("B", float(x)) for x in B], ["method", "score"])
summ = (scores.groupBy("method")
        .agg(F.count("score").alias("n"), F.mean("score").alias("mean"),
             F.var_samp("score").alias("var"), F.stddev_samp("score").alias("sd"))
        .orderBy("method"))
summ.show()
sa, sb = summ.collect()
n1, n2 = sa.n, sb.n
sp2 = ((n1 - 1) * sa["var"] + (n2 - 1) * sb["var"]) / (n1 + n2 - 2)
se = (sp2 * (1 / n1 + 1 / n2)) ** 0.5
t = (sa["mean"] - sb["mean"]) / se
dof = n1 + n2 - 2
p_t = 2 * stats.t.sf(abs(t), dof)
print(f"pooled variance sp^2 = {sp2:.4f}, standard error = {se:.4f}")
print(f"Spark-computed t = {t:.4f}, df = {dof}, two-tailed p-value = {p_t:.6f}")
sc_t = stats.ttest_ind(A, B, equal_var=True)
print(f"scipy check:      t = {sc_t.statistic:.4f}, p-value = {sc_t.pvalue:.6f}")
print(f"Critical value t(0.025, {dof}) = {stats.t.ppf(0.975, dof):.4f}")
print("Decision:", decide(p_t))

# Paired / one-sample variant: has the mean of Method A changed from 75?
t1 = (sa["mean"] - 75) / (sa.sd / n1 ** 0.5)
p1 = 2 * stats.t.sf(abs(t1), n1 - 1)
print(f"One-sample t-test (H0: mu_A = 75): t = {t1:.4f}, df = {n1-1}, p = {p1:.6f}"
      f"  -> {decide(p1)}")

# ===========================================================================
# 3a. F-TEST FOR EQUALITY OF TWO VARIANCES
#     Is machine X's fill volume more variable than machine Y's?
#     H0: sigma_X^2 = sigma_Y^2.  H1: sigma_X^2 != sigma_Y^2.
# ===========================================================================
print()
print("=" * 72)
print("3a. F-TEST FOR EQUAL VARIANCES  (fill volume, machine X vs Y)")
print("=" * 72)
X = [502, 498, 510, 495, 505, 490, 512, 497, 508, 493]
Y = [500, 501, 499, 502, 498, 500, 501, 499, 503, 497]
fill = spark.createDataFrame([("X", float(v)) for v in X] +
                             [("Y", float(v)) for v in Y], ["machine", "ml"])
v = (fill.groupBy("machine")
     .agg(F.count("ml").alias("n"), F.mean("ml").alias("mean"),
          F.var_samp("ml").alias("var")).orderBy("machine"))
v.show()
vx, vy = v.collect()
Fstat = vx["var"] / vy["var"]                 # larger variance on top
d1, d2 = vx.n - 1, vy.n - 1
p_f = 2 * min(stats.f.sf(Fstat, d1, d2), stats.f.cdf(Fstat, d1, d2))
print(f"F = s_X^2 / s_Y^2 = {vx['var']:.4f} / {vy['var']:.4f} = {Fstat:.4f}, "
      f"df = ({d1}, {d2}), two-tailed p-value = {p_f:.6f}")
print(f"Critical value F(0.025; {d1}, {d2}) upper = {stats.f.ppf(0.975, d1, d2):.4f}")
print("Decision:", decide(p_f))

# ===========================================================================
# 3b. ONE-WAY ANOVA F-TEST (compares 3+ group means using a ratio of variances)
#     Does fertiliser type affect crop yield?
#     H0: mu_1 = mu_2 = mu_3.  H1: at least one mean differs.
# ===========================================================================
print()
print("=" * 72)
print("3b. ONE-WAY ANOVA F-TEST  (crop yield by fertiliser)")
print("=" * 72)
groups = {1: [20, 22, 19, 24, 25], 2: [28, 30, 27, 26, 29], 3: [18, 20, 22, 19, 21]}
crop = spark.createDataFrame([(float(g), float(y)) for g, ys in groups.items()
                              for y in ys], ["fertiliser", "yield"])
crop.groupBy("fertiliser").agg(F.count("*").alias("n"),
                               F.mean("yield").alias("mean")).orderBy("fertiliser").show()

# Manual ANOVA table from aggregates
grand = crop.agg(F.mean("yield")).first()[0]
gstats = crop.groupBy("fertiliser").agg(F.count("*").alias("n"),
                                        F.mean("yield").alias("m"))
ssb = gstats.agg(F.sum(F.col("n") * (F.col("m") - grand) ** 2)).first()[0]
ssw = (crop.join(gstats, "fertiliser")
       .agg(F.sum((F.col("yield") - F.col("m")) ** 2)).first()[0])
k, n = gstats.count(), crop.count()
msb, msw = ssb / (k - 1), ssw / (n - k)
print(f"grand mean = {grand:.4f}")
print(f"SSB = {ssb:.4f}, SSW = {ssw:.4f}")
print(f"MSB = SSB/(k-1) = {msb:.4f}, MSW = SSW/(N-k) = {msw:.4f}")
print(f"Manual F = MSB/MSW = {msb/msw:.4f}, df = ({k-1}, {n-k})")

# Spark ANOVATest: categorical label vs continuous feature
anova_df = VectorAssembler(inputCols=["yield"], outputCol="features") \
    .transform(crop).withColumnRenamed("fertiliser", "label")
jdf = spark._jvm.org.apache.spark.ml.stat.ANOVATest.test(
    anova_df._jdf, "features", "label")
ar = DataFrame(jdf, spark).head()
print(f"Spark ANOVATest: F = {ar.fValues[0]:.4f}, df = ({k-1}, {n-k}), "
      f"p-value = {ar.pValues[0]:.6f}")
sc_f = stats.f_oneway(*groups.values())
print(f"scipy check:     F = {sc_f.statistic:.4f}, p-value = {sc_f.pvalue:.6f}")
print(f"Critical value F(0.05; {k-1}, {n-k}) = {stats.f.ppf(0.95, k-1, n-k):.4f}")
print("Decision:", decide(ar.pValues[0]))

spark.stop()
