"""
COSC 611 Big Data Analytics - Midterm, Question 3
Unsupervised learning (clustering) on Apache Spark:
  1. K-Means                    -> pyspark.ml.clustering.KMeans
  2. Bisecting K-Means          -> pyspark.ml.clustering.BisectingKMeans
     (divisive hierarchical clustering)
  3. Gaussian Mixture Model     -> pyspark.ml.clustering.GaussianMixture
     (soft / probabilistic clustering via Expectation-Maximisation)

Example data: 25 mall customers described by
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
    # low income, low spending
    (1, 15, 39), (2, 17, 35), (3, 19, 40), (4, 21, 33), (5, 23, 38),
    # low income, high spending
    (6, 16, 81), (7, 18, 77), (8, 20, 85), (9, 22, 79), (10, 24, 83),
    # middle income, middle spending
    (11, 60, 50), (12, 62, 55), (13, 63, 48), (14, 65, 52), (15, 64, 45),
    # high income, high spending
    (16, 100, 90), (17, 103, 85), (18, 98, 88), (19, 105, 92), (20, 97, 86),
    # high income, low spending
    (21, 101, 15), (22, 99, 20), (23, 104, 12), (24, 96, 18), (25, 102, 22),
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
print("  how the hierarchy unfolds (cluster centres and sizes for k = 2, 3, 4):")
for kk in [2, 3, 4]:
    mk = BisectingKMeans(k=kk, seed=1).fit(df)
    print(f"    k={kk}: " + ", ".join(
        f"({c[0]:.1f}, {c[1]:.1f}) n={n}"
        for c, n in zip(mk.clusterCenters(), mk.summary.clusterSizes)))
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
gmm = GaussianMixture(k=K, seed=2, maxIter=200, tol=1e-6).fit(df)
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
# The five customer groups are far apart, so every membership above is ~1.0.
# Soft clustering matters when clusters OVERLAP: two overlapping groups of
# customers by age (1-D) - points in the overlap get split probabilities.
ages = [22, 24, 25, 26, 27, 28, 29, 30, 31, 33, 35,
        36, 38, 40, 41, 42, 43, 44, 45, 46, 48, 50]
age_df = VectorAssembler(inputCols=["age"], outputCol="features").transform(
    spark.createDataFrame([(float(x),) for x in ages], ["age"]))
g2 = GaussianMixture(k=2, seed=2, maxIter=200, tol=1e-6).fit(age_df)
print("  overlapping 1-D example (ages), GMM k=2:")
for i, row in enumerate(g2.gaussiansDF.collect()):
    print(f"    component {i}: mean = {row['mean'][0]:.2f}, "
          f"variance = {row['cov'].toArray()[0][0]:.2f}, weight = {g2.weights[i]:.3f}")
probe = VectorAssembler(inputCols=["age"], outputCol="features").transform(
    spark.createDataFrame([(25.0,), (33.0,), (35.0,), (37.0,), (47.0,)], ["age"]))
for r in g2.transform(probe).collect():
    print(f"    age {r.age:4.0f}: P(component 0) = {r.probability[0]:.3f}, "
          f"P(component 1) = {r.probability[1]:.3f}")

# ---------------------------------------------------------------------------
# Side-by-side assignment of every customer
# ---------------------------------------------------------------------------
print("\n=== Cluster assignment by algorithm ===")
side = (km_pred.select("id", "income", "spending", F.col("prediction").alias("kmeans"))
        .join(bkm_pred.select("id", F.col("prediction").alias("bisecting")), "id")
        .join(gmm_pred.select("id", F.col("prediction").alias("gmm")), "id")
        .orderBy("id"))
side.show(30, truncate=False)

spark.stop()
