"""
COSC 611 Big Data Analytics - Midterm, Question 3
Unsupervised learning (clustering) on Apache Spark:
  1. K-Means                    -> pyspark.ml.clustering.KMeans
  2. Bisecting K-Means          -> pyspark.ml.clustering.BisectingKMeans
     (divisive hierarchical clustering)
  3. Gaussian Mixture Model     -> pyspark.ml.clustering.GaussianMixture
     (soft / probabilistic clustering via Expectation-Maximisation)

Example data: 15 mall customers described by
  annual income (k$) and spending score (1-100).

Run:  spark-submit q3_clustering.py      (or: python3 q3_clustering.py)
"""
import math

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.clustering import KMeans, BisectingKMeans, GaussianMixture
from pyspark.ml.evaluation import ClusteringEvaluator

spark = (SparkSession.builder.appName("Q3-Clustering")
         .master("local[*]").getOrCreate())
spark.sparkContext.setLogLevel("ERROR")

data = [
    (1, 15, 39), (2, 16, 81), (3, 17, 6), (4, 18, 77), (5, 19, 40),
    (6, 60, 50), (7, 62, 55), (8, 63, 48), (9, 65, 52), (10, 64, 45),
    (11, 100, 90), (12, 103, 85), (13, 98, 88), (14, 101, 15), (15, 99, 20),
]
df = spark.createDataFrame(data, ["id", "income", "spending"])
df = VectorAssembler(inputCols=["income", "spending"],
                     outputCol="features").transform(df)
print("=== Input data: customers (income k$, spending score) ===")
df.show(truncate=False)

evaluator = ClusteringEvaluator(featuresCol="features", metricName="silhouette")
K = 5

# ---------------------------------------------------------------------------
# Hand computation: one iteration of K-Means on a tiny subset (shown in report)
# ---------------------------------------------------------------------------
print("=== Hand-traced K-Means (k=2) on points P1..P4, first iteration ===")
pts = {"P1": (15, 39), "P2": (19, 40), "P3": (60, 50), "P4": (64, 45)}
cents = {"C1": pts["P1"], "C2": pts["P3"]}       # initial centroids
assign = {}
for p, (x, y) in pts.items():
    d = {c: math.dist((x, y), cxy) for c, cxy in cents.items()}
    assign[p] = min(d, key=d.get)
    print(f"  {p}{(x, y)}: d(C1)={d['C1']:.2f}  d(C2)={d['C2']:.2f}  -> {assign[p]}")
for c in cents:
    members = [pts[p] for p in pts if assign[p] == c]
    new = tuple(sum(v) / len(members) for v in zip(*members))
    print(f"  new {c} = mean of {members} = {new}")

# ---------------------------------------------------------------------------
# Elbow method: choose k for K-Means using WSSSE and silhouette
# ---------------------------------------------------------------------------
print("\n=== Choosing k (elbow + silhouette) ===")
for k in range(2, 7):
    m = KMeans(k=k, seed=1).fit(df)
    print(f"  k={k}: WSSSE = {m.summary.trainingCost:10.2f}   "
          f"silhouette = {evaluator.evaluate(m.transform(df)):.4f}")

# ---------------------------------------------------------------------------
# 1. K-MEANS
# ---------------------------------------------------------------------------
print(f"\n=== 1. K-Means (k={K}) ===")
km = KMeans(k=K, seed=1, maxIter=20).fit(df)
km_pred = km.transform(df)
for i, c in enumerate(km.clusterCenters()):
    print(f"  centroid {i}: income={c[0]:.2f}, spending={c[1]:.2f}")
print(f"  WSSSE = {km.summary.trainingCost:.2f}, "
      f"silhouette = {evaluator.evaluate(km_pred):.4f}, "
      f"cluster sizes = {km.summary.clusterSizes}")

# ---------------------------------------------------------------------------
# 2. BISECTING K-MEANS (hierarchical, divisive)
# ---------------------------------------------------------------------------
print(f"\n=== 2. Bisecting K-Means (k={K}) ===")
bkm = BisectingKMeans(k=K, seed=1).fit(df)
bkm_pred = bkm.transform(df)
for i, c in enumerate(bkm.clusterCenters()):
    print(f"  centroid {i}: income={c[0]:.2f}, spending={c[1]:.2f}")
print(f"  SSE = {bkm.summary.trainingCost:.2f}, "
      f"silhouette = {evaluator.evaluate(bkm_pred):.4f}, "
      f"cluster sizes = {bkm.summary.clusterSizes}")

# ---------------------------------------------------------------------------
# 3. GAUSSIAN MIXTURE MODEL (soft clustering)
# ---------------------------------------------------------------------------
print(f"\n=== 3. Gaussian Mixture Model (k={K}) ===")
gmm = GaussianMixture(k=K, seed=7, maxIter=200, tol=1e-6).fit(df)
gmm_pred = gmm.transform(df)
print("  mixture weights:", [round(w, 4) for w in gmm.weights])
for i, row in enumerate(gmm.gaussiansDF.collect()):
    print(f"  component {i}: mean = [{row['mean'][0]:.2f}, {row['mean'][1]:.2f}]")
print(f"  log-likelihood = {gmm.summary.logLikelihood:.4f}, "
      f"silhouette = {evaluator.evaluate(gmm_pred):.4f}, "
      f"cluster sizes = {gmm.summary.clusterSizes}")
print("  soft membership probabilities (first 6 customers):")
for r in gmm_pred.select("id", "probability").limit(6).collect():
    print(f"    customer {r.id:2d}: " + ", ".join(f"{p:.3f}" for p in r.probability))

# ---------------------------------------------------------------------------
# Side-by-side assignment of every customer
# ---------------------------------------------------------------------------
print("\n=== Cluster assignment by algorithm ===")
side = (km_pred.select("id", "income", "spending", F.col("prediction").alias("kmeans"))
        .join(bkm_pred.select("id", F.col("prediction").alias("bisecting")), "id")
        .join(gmm_pred.select("id", F.col("prediction").alias("gmm")), "id")
        .orderBy("id"))
side.show(truncate=False)

spark.stop()
