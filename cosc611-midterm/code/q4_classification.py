"""
COSC 611 Big Data Analytics - Midterm, Question 4
Classification on Apache Spark:
  1. Naive Bayes                   -> pyspark.ml.classification.NaiveBayes
  2. Support Vector Machine (SVM)  -> pyspark.ml.classification.LinearSVC
  3. Random Forest                 -> pyspark.ml.classification.RandomForestClassifier

Datasets (all real, published data):
  * Play Tennis - the 14-day weather table of Quinlan (1986) as printed in
    Mitchell, "Machine Learning" (1997), Table 3.2 (Wind column omitted).
  * iris        - Anderson (1935) / Fisher (1936), data/iris.csv.
  * spam7       - 4,601 real e-mails from the UCI Spambase collection (Hopkins,
    Reeber, Forman & Suermondt, Hewlett-Packard Labs, 1999), as the 6-feature
    subset in the R package DAAG (Maindonald & Braun), data/spam7.csv.

Part A: Play Tennis -> Naive Bayes and Gini splits by hand, then Spark NaiveBayes
        and a small RandomForest; LinearSVC on two iris species (hand-checked).
Part B: spam7 -> all three classifiers trained on 70% and evaluated on the same 30%.

Run from the cosc611-midterm folder:  spark-submit code/q4_classification.py
"""
import math
import os

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.ml import Pipeline
from pyspark.ml.feature import StringIndexer, OneHotEncoder, VectorAssembler, StandardScaler
from pyspark.ml.classification import NaiveBayes, LinearSVC, RandomForestClassifier
from pyspark.ml.evaluation import (MulticlassClassificationEvaluator,
                                   BinaryClassificationEvaluator)

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
spark = (SparkSession.builder.appName("Q4-Classification")
         .master("local[*]").getOrCreate())
spark.sparkContext.setLogLevel("ERROR")

# ===========================================================================
# PART A - Naive Bayes by hand on categorical data
# ===========================================================================
print("=" * 72)
print("PART A: Naive Bayes on the 'Play Tennis' data")
print("=" * 72)
tennis = spark.createDataFrame([
    ("Sunny", "Hot", "High", "No"), ("Sunny", "Hot", "High", "No"),
    ("Overcast", "Hot", "High", "Yes"), ("Rain", "Mild", "High", "Yes"),
    ("Rain", "Cool", "Normal", "Yes"), ("Rain", "Cool", "Normal", "No"),
    ("Overcast", "Cool", "Normal", "Yes"), ("Sunny", "Mild", "High", "No"),
    ("Sunny", "Cool", "Normal", "Yes"), ("Rain", "Mild", "Normal", "Yes"),
    ("Sunny", "Mild", "Normal", "Yes"), ("Overcast", "Mild", "High", "Yes"),
    ("Overcast", "Hot", "Normal", "Yes"), ("Rain", "Mild", "High", "No"),
], ["outlook", "temp", "humidity", "play"])
tennis.show()

query = {"outlook": "Sunny", "temp": "Cool", "humidity": "High"}
print("Classify new day:", query)
N = tennis.count()
priors = {r.play: r["count"] / N for r in tennis.groupBy("play").count().collect()}
class_n = {r.play: r["count"] for r in tennis.groupBy("play").count().collect()}
scores = {}
for c in ["Yes", "No"]:
    score = priors[c]
    terms = [f"P({c})={class_n[c]}/{N}"]
    for feat, val in query.items():
        cnt = tennis.where((F.col("play") == c) & (F.col(feat) == val)).count()
        score *= cnt / class_n[c]
        terms.append(f"P({feat}={val}|{c})={cnt}/{class_n[c]}")
    scores[c] = score
    print(f"  {c:3s}: " + " x ".join(terms) + f" = {score:.5f}")
tot = sum(scores.values())
for c in scores:
    print(f"  posterior P({c}|x) = {scores[c]/tot:.4f}")
print("  => prediction:", max(scores, key=scores.get))

# Same thing with Spark's NaiveBayes (one-hot features, Laplace smoothing = 1)
idx = [StringIndexer(inputCol=c, outputCol=c + "_i") for c in ["outlook", "temp", "humidity"]]
ohe = OneHotEncoder(inputCols=["outlook_i", "temp_i", "humidity_i"],
                    outputCols=["outlook_v", "temp_v", "humidity_v"], dropLast=False)
asm = VectorAssembler(inputCols=["outlook_v", "temp_v", "humidity_v"], outputCol="features")
lbl = StringIndexer(inputCol="play", outputCol="label")
nb_pipe = Pipeline(stages=idx + [ohe, asm, lbl,
                                 NaiveBayes(modelType="multinomial", smoothing=1.0)])
nb_model = nb_pipe.fit(tennis)
new_day = spark.createDataFrame([("Sunny", "Cool", "High", "No")],
                                ["outlook", "temp", "humidity", "play"])
labels = nb_model.stages[-2].labels
p = nb_model.transform(new_day).select("probability", "prediction").first()
print(f"  Spark NaiveBayes (Laplace smoothing): P({labels[0]})={p.probability[0]:.4f}, "
      f"P({labels[1]})={p.probability[1]:.4f} -> {labels[int(p.prediction)]}")

# --- Random Forest on the same data: Gini of candidate root splits by hand,
#     then a 7-tree forest and the vote of each tree for the new day
print("\nRandom Forest building block - Gini impurity of each candidate root split:")


def gini(counts):
    n = sum(counts)
    return 1 - sum((c / n) ** 2 for c in counts)


root = [r["count"] for r in tennis.groupBy("play").count().collect()]
g_root = gini(root)
print(f"  Gini(root) = {g_root:.4f}")
for feat in ["outlook", "temp", "humidity"]:
    parts = (tennis.groupBy(feat).pivot("play", ["Yes", "No"]).count()
             .fillna(0).collect())
    w = sum((r.Yes + r.No) / N * gini([r.Yes, r.No]) for r in parts)
    detail = ", ".join(f"{r[feat]}({r.Yes}Y/{r.No}N)" for r in parts)
    print(f"  split on {feat:8s}: {detail}  weighted Gini = {w:.4f}, "
          f"gain = {g_root - w:.4f}")

rf_pipe = Pipeline(stages=idx + [ohe, asm, lbl,
                                 RandomForestClassifier(numTrees=7, maxDepth=3,
                                                        seed=11)])
rf_model = rf_pipe.fit(tennis)
feat_day = rf_model.transform(new_day)
forest = rf_model.stages[-1]
votes = [labels[int(t.predict(feat_day.first().features))] for t in forest.trees]
print(f"  votes of the {len(votes)} trees for {query}: {votes}")
rp = feat_day.first()
print(f"  forest probability: P({labels[0]})={rp.probability[0]:.3f}, "
      f"P({labels[1]})={rp.probability[1]:.3f} -> {labels[int(rp.prediction)]}")

# --- SVM on real data: iris setosa vs versicolor, petal length and width
print("\nLinear SVM on iris: setosa (label 0) vs versicolor (label 1), petal features")
iris = (spark.read.csv(os.path.join(DATA, "iris.csv"), header=True, inferSchema=True)
        .withColumnRenamed("rownames", "id")
        .withColumnRenamed("Petal.Length", "petal_len")
        .withColumnRenamed("Petal.Width", "petal_wid")
        .where(F.col("Species").isin("setosa", "versicolor"))
        .withColumn("label", F.when(F.col("Species") == "versicolor", 1.0).otherwise(0.0)))
two = VectorAssembler(inputCols=["petal_len", "petal_wid"], outputCol="features").transform(iris)
two.groupBy("Species").agg(F.min("petal_len"), F.max("petal_len"),
                           F.min("petal_wid"), F.max("petal_wid")).orderBy("Species").show()
svc = LinearSVC(regParam=0.001, maxIter=1000, standardization=False).fit(two)
w1, w2 = (float(v) for v in svc.coefficients)
b = float(svc.intercept)
print(f"  Spark LinearSVC hyperplane: {w1:.4f}*petal_len + {w2:.4f}*petal_wid + ({b:.4f}) = 0")
print(f"  margin width 2/||w|| = {2 / (w1 ** 2 + w2 ** 2) ** 0.5:.4f} cm")
scored = svc.transform(two).withColumn("score", F.udf(lambda v: float(v[1]), "double")("rawPrediction"))
print("  the flowers closest to the boundary (smallest |w.x + b|, i.e. the support vectors):")
(scored.withColumn("abs_score", F.abs("score")).orderBy("abs_score")
 .select("id", "Species", "petal_len", "petal_wid", F.round("score", 4).alias("w.x+b"),
         "prediction").show(4))
for fid in [1, 51]:
    r = scored.where(F.col("id") == fid).first()
    print(f"  hand check flower {fid} ({r.Species}): {w1:.4f}*{r.petal_len} + "
          f"{w2:.4f}*{r.petal_wid} + ({b:.4f}) = {w1 * r.petal_len + w2 * r.petal_wid + b:.4f}"
          f" -> class {'versicolor' if w1 * r.petal_len + w2 * r.petal_wid + b > 0 else 'setosa'}")
acc_two = scored.where(F.col("label") == F.col("prediction")).count() / scored.count()
print(f"  training accuracy = {acc_two:.4f} (the two species are linearly separable)")

# ===========================================================================
# PART B - Compare Naive Bayes, SVM and Random Forest on real spam e-mail
# ===========================================================================
print()
print("=" * 72)
print("PART B: Spam detection (spam7) - Naive Bayes vs SVM vs Random Forest")
print("=" * 72)
FEATS = ["crl_tot", "dollar", "bang", "money", "n000", "make"]
emails = (spark.read.csv(os.path.join(DATA, "spam7.csv"), header=True, inferSchema=True)
          .drop("rownames").withColumnRenamed("crl.tot", "crl_tot")
          .withColumn("label", F.when(F.col("yesno") == "y", 1.0).otherwise(0.0)))
print("features: crl_tot = total length of runs of CAPITAL letters; dollar, bang, money,")
print("n000, make = % of characters that are '$' / '!' and % of words 'money' / '000' / 'make'")
emails.show(5)
print(f"{emails.count()} e-mails; class balance:")
emails.groupBy("label").count().orderBy("label").show()
emails.groupBy("label").agg(*[F.round(F.mean(c), 3).alias(c) for c in FEATS]) \
    .orderBy("label").show()

# Gaussian NB assumes each feature is normal within a class; these counts and
# percentages are heavily right-skewed, so we also try NB on log(1 + x)
for c in FEATS:
    emails = emails.withColumn("log_" + c, F.log1p(c))
emails = VectorAssembler(inputCols=FEATS, outputCol="features").transform(emails)
emails = VectorAssembler(inputCols=["log_" + c for c in FEATS],
                         outputCol="logfeatures").transform(emails)
emails = emails.withColumn("eid", F.monotonically_increasing_id())
train, test = emails.randomSplit([0.7, 0.3], seed=42)
train.cache()
print(f"train rows = {train.count()}, test rows = {test.count()}")

scaler = StandardScaler(inputCol="features", outputCol="scaled",
                        withMean=True, withStd=True)
models = {
    "Naive Bayes (Gaussian)": Pipeline(stages=[
        NaiveBayes(featuresCol="features", modelType="gaussian")]),
    "Naive Bayes (log1p feats)": Pipeline(stages=[
        NaiveBayes(featuresCol="logfeatures", modelType="gaussian")]),
    "Linear SVM (LinearSVC)": Pipeline(stages=[
        scaler, LinearSVC(featuresCol="scaled", maxIter=200, regParam=0.01)]),
    "Random Forest (100 trees)": Pipeline(stages=[
        RandomForestClassifier(featuresCol="features", numTrees=100,
                               maxDepth=8, seed=42)]),
}
acc = MulticlassClassificationEvaluator(metricName="accuracy")
f1 = MulticlassClassificationEvaluator(metricName="f1")
prec = MulticlassClassificationEvaluator(metricName="precisionByLabel", metricLabel=1.0)
rec = MulticlassClassificationEvaluator(metricName="recallByLabel", metricLabel=1.0)
# ROC-AUC needs a score that ranks e-mails by "spamminess": the class-1 probability
# for NB and RF, the signed margin w.x + b (rawPrediction) for the SVM, which has
# no probability output. (NB's rawPrediction holds log-likelihoods, not a score.)
auc_prob = BinaryClassificationEvaluator(rawPredictionCol="probability",
                                         metricName="areaUnderROC")
auc_raw = BinaryClassificationEvaluator(rawPredictionCol="rawPrediction",
                                        metricName="areaUnderROC")

fitted = {}
print(f"\n{'Model':28s}{'Accuracy':>10s}{'F1':>8s}{'Prec':>8s}{'Recall':>8s}{'AUC':>8s}")
for name, pipe in models.items():
    m = pipe.fit(train)
    fitted[name] = m
    pr = m.transform(test)
    print(f"{name:28s}{acc.evaluate(pr):10.4f}{f1.evaluate(pr):8.4f}"
          f"{prec.evaluate(pr):8.4f}{rec.evaluate(pr):8.4f}"
          f"{(auc_raw if 'SVM' in name else auc_prob).evaluate(pr):8.4f}")

for name, m in fitted.items():
    pr = m.transform(test)
    print(f"\nConfusion matrix - {name} (rows = actual, cols = predicted):")
    pr.groupBy("label").pivot("prediction", [0.0, 1.0]).count().fillna(0) \
      .orderBy("label").show()

nbm = fitted["Naive Bayes (Gaussian)"].stages[-1]
print("Naive Bayes - class priors:", [round(math.exp(float(x)), 4) for x in nbm.pi])
print("Naive Bayes - per-class feature means (rows = ham, spam; cols =", FEATS, "):")
print(nbm.theta)
svm = fitted["Linear SVM (LinearSVC)"].stages[-1]
print("\nSVM hyperplane on standardised features:",
      dict(zip(FEATS, [round(float(x), 4) for x in svm.coefficients])),
      " b =", round(float(svm.intercept), 4))
rf = fitted["Random Forest (100 trees)"].stages[-1]
print("\nRandom Forest feature importances:",
      dict(zip(FEATS, [round(float(x), 4) for x in rf.featureImportances.toArray()])))

print("\nPredictions for the first 3 test e-mails that the models disagree on, "
      "and 2 they agree on:")
both = None
for name, m in fitted.items():
    if "log1p" in name:
        continue
    short = name.split(" (")[0].replace(" ", "_")
    p = m.transform(test).select("eid", *FEATS, "label", F.col("prediction").alias(short))
    both = p if both is None else both.join(p.select("eid", short), "eid")
dis = both.where((F.col("Naive_Bayes") != F.col("Linear_SVM")) |
                 (F.col("Linear_SVM") != F.col("Random_Forest")))
agree = both.join(dis.select("eid"), "eid", "left_anti")
dis.orderBy("eid").limit(3).union(agree.orderBy("eid").limit(2)).drop("eid").show()
print(f"models disagree on {dis.count()} of {test.count()} test e-mails")

spark.stop()
