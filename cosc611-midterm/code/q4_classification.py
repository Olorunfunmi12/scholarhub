"""
COSC 611 Big Data Analytics - Midterm, Question 4
Classification on Apache Spark:
  1. Naive Bayes                   -> pyspark.ml.classification.NaiveBayes
  2. Support Vector Machine (SVM)  -> pyspark.ml.classification.LinearSVC
  3. Random Forest                 -> pyspark.ml.classification.RandomForestClassifier

Part A: tiny categorical "Play Tennis" data -> Naive Bayes computed by hand
        with DataFrame aggregations, then with Spark's multinomial NaiveBayes.
Part B: synthetic email-spam data (3 numeric features, 400 emails) -> all three
        classifiers trained on 70% and evaluated on the same 30% test split.

Run:  spark-submit q4_classification.py      (or: python3 q4_classification.py)
"""
import random

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.ml import Pipeline
from pyspark.ml.feature import StringIndexer, OneHotEncoder, VectorAssembler, StandardScaler
from pyspark.ml.classification import NaiveBayes, LinearSVC, RandomForestClassifier
from pyspark.ml.evaluation import (MulticlassClassificationEvaluator,
                                   BinaryClassificationEvaluator)

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

# ===========================================================================
# PART B - Compare Naive Bayes, SVM and Random Forest on spam data
# ===========================================================================
print()
print("=" * 72)
print("PART B: Spam detection - Naive Bayes vs SVM vs Random Forest")
print("=" * 72)
random.seed(611)
rows = []
for _ in range(200):   # ham (label 0)
    rows.append((random.gauss(2, 1.5), random.gauss(1, 1.0),
                 random.gauss(0.10, 0.08), 0.0))
for _ in range(200):   # spam (label 1)
    rows.append((random.gauss(6, 2.0), random.gauss(4, 1.5),
                 random.gauss(0.35, 0.12), 1.0))
# features: number of links, count of words like "free"/"win", fraction of CAPS
emails = spark.createDataFrame(
    [(max(0.0, a), max(0.0, b), min(1.0, max(0.0, c)), y) for a, b, c, y in rows],
    ["links", "spam_words", "caps_ratio", "label"])
print("Sample of the data (400 emails, 200 spam / 200 ham):")
emails.show(5)
emails.groupBy("label").agg(*[F.round(F.mean(c), 3).alias("mean_" + c)
                              for c in ["links", "spam_words", "caps_ratio"]]).show()

emails = VectorAssembler(inputCols=["links", "spam_words", "caps_ratio"],
                         outputCol="features").transform(emails)
train, test = emails.randomSplit([0.7, 0.3], seed=42)
train.cache()
print(f"train rows = {train.count()}, test rows = {test.count()}")

scaler = StandardScaler(inputCol="features", outputCol="scaled",
                        withMean=True, withStd=True)
models = {
    "Naive Bayes (Gaussian)": Pipeline(stages=[
        NaiveBayes(featuresCol="features", modelType="gaussian")]),
    "Linear SVM (LinearSVC)": Pipeline(stages=[
        scaler, LinearSVC(featuresCol="scaled", maxIter=100, regParam=0.01)]),
    "Random Forest (100 trees)": Pipeline(stages=[
        RandomForestClassifier(featuresCol="features", numTrees=100,
                               maxDepth=5, seed=42)]),
}
acc = MulticlassClassificationEvaluator(metricName="accuracy")
f1 = MulticlassClassificationEvaluator(metricName="f1")
prec = MulticlassClassificationEvaluator(metricName="precisionByLabel", metricLabel=1.0)
rec = MulticlassClassificationEvaluator(metricName="recallByLabel", metricLabel=1.0)
auc = BinaryClassificationEvaluator(rawPredictionCol="rawPrediction",
                                    metricName="areaUnderROC")

fitted = {}
print(f"\n{'Model':28s}{'Accuracy':>10s}{'F1':>8s}{'Prec':>8s}{'Recall':>8s}{'AUC':>8s}")
for name, pipe in models.items():
    m = pipe.fit(train)
    fitted[name] = m
    pr = m.transform(test)
    print(f"{name:28s}{acc.evaluate(pr):10.4f}{f1.evaluate(pr):8.4f}"
          f"{prec.evaluate(pr):8.4f}{rec.evaluate(pr):8.4f}{auc.evaluate(pr):8.4f}")

for name, m in fitted.items():
    pr = m.transform(test)
    print(f"\nConfusion matrix - {name} (rows = actual, cols = predicted):")
    pr.groupBy("label").pivot("prediction", [0.0, 1.0]).count().fillna(0) \
      .orderBy("label").show()

# Model internals
nbm = fitted["Naive Bayes (Gaussian)"].stages[-1]
print("Naive Bayes - class log-priors:", [round(x, 4) for x in nbm.pi])
print("Naive Bayes - per-class feature means (theta):")
print(nbm.theta)
print("Naive Bayes - per-class feature variances (sigma):")
print(nbm.sigma)
svm = fitted["Linear SVM (LinearSVC)"].stages[-1]
print("\nSVM hyperplane on standardised features: w =",
      [round(x, 4) for x in svm.coefficients], " b =", round(svm.intercept, 4))
rf = fitted["Random Forest (100 trees)"].stages[-1]
print("\nRandom Forest feature importances:",
      dict(zip(["links", "spam_words", "caps_ratio"],
               [round(x, 4) for x in rf.featureImportances.toArray()])))

new_emails = spark.createDataFrame([
    (1.0, 0.0, 0.05, 0.0),   # looks like normal mail
    (8.0, 6.0, 0.50, 1.0),   # looks like spam
    (4.0, 2.5, 0.22, 1.0),   # borderline
], ["links", "spam_words", "caps_ratio", "label"])
new_emails = VectorAssembler(inputCols=["links", "spam_words", "caps_ratio"],
                             outputCol="features").transform(new_emails)
print("\nPredictions for three new emails (1 = spam):")
out = new_emails.select("links", "spam_words", "caps_ratio")
for name, m in fitted.items():
    short = name.split(" (")[0].replace(" ", "_")
    out = out.join(m.transform(new_emails)
                   .select("links", "spam_words", "caps_ratio",
                           F.col("prediction").alias(short)),
                   ["links", "spam_words", "caps_ratio"])
out.show()

spark.stop()
