"""
COSC 611 Big Data Analytics - Midterm, Question 3
Unsupervised learning (clustering) on Apache Spark with real datasets:

  1. K-Means                    -> pyspark.ml.clustering.KMeans
  2. Bisecting K-Means          -> pyspark.ml.clustering.BisectingKMeans
     (divisive hierarchical clustering)
  3. Gaussian Mixture Model     -> pyspark.ml.clustering.GaussianMixture
     (soft / probabilistic clustering via Expectation-Maximisation)

Datasets (R `datasets` package, CSV copies from the Rdatasets archive, in data/):
  * iris     - Anderson (1935) / Fisher (1936): 150 flowers, 4 measurements (cm),
               3 species. The species label is NOT used for clustering; it is only
               used afterwards to check how well each algorithm recovered it.
  * faithful - Old Faithful geyser, Yellowstone (Azzalini & Bowman 1990): 272
               eruptions, duration (min) and waiting time to next eruption (min).

Run from the cosc611-midterm folder:  spark-submit code/q3_clustering.py
"""
import math
import os

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.clustering import KMeans, BisectingKMeans, GaussianMixture
from pyspark.ml.evaluation import ClusteringEvaluator

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
spark = (SparkSession.builder.appName("Q3-Clustering")
         .master("local[*]").getOrCreate())
spark.sparkContext.setLogLevel("ERROR")

FEATS = ["Sepal_Length", "Sepal_Width", "Petal_Length", "Petal_Width"]
iris = (spark.read.csv(os.path.join(DATA, "iris.csv"), header=True, inferSchema=True)
        .withColumnRenamed("rownames", "id"))
for c in FEATS:
    iris = iris.withColumnRenamed(c.replace("_", "."), c)
df = VectorAssembler(inputCols=FEATS, outputCol="features").transform(iris).cache()
print("=== Iris data: 150 flowers, 4 features (species kept aside for evaluation) ===")
df.select("id", *FEATS, "Species").show(5)
df.groupBy("Species").agg(*[F.round(F.mean(c), 3).alias(c) for c in FEATS]) \
    .orderBy("Species").show()

evaluator = ClusteringEvaluator(featuresCol="features", metricName="silhouette")


def vs_species(pred, name):
    """Cross-tabulate clusters against the true species and report purity."""
    ct = pred.groupBy("prediction").pivot("Species").count().fillna(0).orderBy("prediction")
    print(f"  {name}: clusters (rows) vs true species (columns)")
    ct.show()
    rows = ct.collect()
    purity = sum(max(r[s] for r in [row] for s in ct.columns[1:]) for row in rows) / 150
    print(f"  purity = {purity:.4f} "
          f"({int(round(purity * 150))} of 150 flowers in their cluster's majority species)")


# ---------------------------------------------------------------------------
# Hand computation: one K-Means iteration on four real flowers (petal features)
# ---------------------------------------------------------------------------
print("=== Hand-traced K-Means (k=2) on four iris flowers, petal length & width ===")
pick = [1, 44, 51, 78]         # two setosa, two versicolor (row numbers in iris)
pts = {f"flower{r.id}": (r.Petal_Length, r.Petal_Width)
       for r in iris.where(F.col("id").isin(pick)).orderBy("id").collect()}
names = list(pts)
cents = {"C1": pts[names[0]], "C2": pts[names[2]]}   # initial centroids
assign = {}
for p, xy in pts.items():
    d = {c: math.dist(xy, cxy) for c, cxy in cents.items()}
    assign[p] = min(d, key=d.get)
    print(f"  {p}{xy}: d(C1)={d['C1']:.4f}  d(C2)={d['C2']:.4f}  -> {assign[p]}")
for c in cents:
    members = [pts[p] for p in pts if assign[p] == c]
    new = tuple(round(sum(v) / len(members), 4) for v in zip(*members))
    print(f"  new {c} = mean of {members} = {new}")

# ---------------------------------------------------------------------------
# Choosing k: elbow (WSSSE) and silhouette
# ---------------------------------------------------------------------------
print("\n=== Choosing k for K-Means (elbow + silhouette) ===")
for k in range(2, 7):
    m = KMeans(k=k, seed=1).fit(df)
    print(f"  k={k}: WSSSE = {m.summary.trainingCost:8.3f}   "
          f"silhouette = {evaluator.evaluate(m.transform(df)):.4f}")
K = 3   # three species are known to exist; k=2 merges versicolor+virginica

# ---------------------------------------------------------------------------
# 1. K-MEANS
# ---------------------------------------------------------------------------
print(f"\n=== 1. K-Means (k={K}) ===")
km = KMeans(k=K, seed=1, maxIter=50).fit(df)
km_pred = km.transform(df)
for i, c in enumerate(km.clusterCenters()):
    print(f"  centroid {i}: " + ", ".join(f"{n}={v:.3f}" for n, v in zip(FEATS, c)))
print(f"  WSSSE = {km.summary.trainingCost:.3f}, silhouette = "
      f"{evaluator.evaluate(km_pred):.4f}, sizes = {km.summary.clusterSizes}, "
      f"iterations = {km.summary.numIter}")
vs_species(km_pred, "K-Means")

# ---------------------------------------------------------------------------
# 2. BISECTING K-MEANS (hierarchical, divisive)
# ---------------------------------------------------------------------------
print(f"=== 2. Bisecting K-Means (k={K}) ===")
print("  how the hierarchy unfolds (cluster centres, sizes):")
for kk in [2, 3]:
    mk = BisectingKMeans(k=kk, seed=1).fit(df)
    print(f"    k={kk}: " + "; ".join(
        "(" + ", ".join(f"{v:.2f}" for v in c) + f") n={n}"
        for c, n in zip(mk.clusterCenters(), mk.summary.clusterSizes)))
bkm = BisectingKMeans(k=K, seed=1).fit(df)
bkm_pred = bkm.transform(df)
for i, c in enumerate(bkm.clusterCenters()):
    print(f"  centroid {i}: " + ", ".join(f"{n}={v:.3f}" for n, v in zip(FEATS, c)))
print(f"  SSE = {bkm.summary.trainingCost:.3f}, silhouette = "
      f"{evaluator.evaluate(bkm_pred):.4f}, sizes = {bkm.summary.clusterSizes}")
vs_species(bkm_pred, "Bisecting K-Means")

# ---------------------------------------------------------------------------
# 3. GAUSSIAN MIXTURE MODEL (soft clustering)
# ---------------------------------------------------------------------------
print(f"=== 3. Gaussian Mixture Model (k={K}) ===")
print("  EM converges to a local optimum, so try several random initialisations:")
best = None
for s in range(1, 11):
    g = GaussianMixture(k=K, seed=s, maxIter=200, tol=1e-6).fit(df)
    ll = g.summary.logLikelihood
    collapsed = min(g.weights) < 0.10
    print(f"    seed {s:2d}: log-likelihood = {ll:9.4f}, sizes = {g.summary.clusterSizes}"
          + ("   <- rejected: a component holds < 10% of the data" if collapsed else ""))
    if not collapsed and (best is None or ll > best[1]):
        best = (s, ll, g)
seed, _, gmm = best
print(f"  keeping the highest-likelihood fit whose components each hold >= 10% (seed {seed})")
gmm_pred = gmm.transform(df)
print("  mixture weights:", [round(w, 4) for w in gmm.weights])
for i, row in enumerate(gmm.gaussiansDF.collect()):
    print(f"  component {i}: mean = [" + ", ".join(f"{v:.3f}" for v in row["mean"]) + "]")
print(f"  log-likelihood = {gmm.summary.logLikelihood:.4f}, silhouette = "
      f"{evaluator.evaluate(gmm_pred):.4f}, sizes = {gmm.summary.clusterSizes}")
vs_species(gmm_pred, "Gaussian Mixture")
print("  flowers with the most uncertain membership (max probability < 0.95):")
(gmm_pred.withColumn("p", F.udf(lambda v: [round(float(x), 3) for x in v],
                                "array<double>")("probability"))
 .where(F.array_max("p") < 0.95)
 .select("id", *FEATS, "Species", "p").orderBy("id").show(truncate=False))

# ---------------------------------------------------------------------------
# GMM soft membership on Old Faithful eruption durations (1-D, hand-checkable)
# ---------------------------------------------------------------------------
print("=== Old Faithful: GMM (k=2) on eruption duration ===")
geyser = spark.read.csv(os.path.join(DATA, "faithful.csv"), header=True, inferSchema=True)
gdf = VectorAssembler(inputCols=["eruptions"], outputCol="features").transform(geyser)
gdf.select("eruptions", "waiting").describe().show()
g2 = GaussianMixture(k=2, seed=1, maxIter=500, tol=1e-8).fit(gdf)
for i, row in enumerate(g2.gaussiansDF.collect()):
    print(f"  component {i}: mean = {row['mean'][0]:.4f} min, variance = "
          f"{row['cov'].toArray()[0][0]:.4f}, weight = {g2.weights[i]:.4f}")
probe = VectorAssembler(inputCols=["eruptions"], outputCol="features").transform(
    spark.createDataFrame([(x,) for x in [1.8, 2.8, 3.0, 3.2, 4.5]], ["eruptions"]))
for r in g2.transform(probe).collect():
    print(f"  eruption {r.eruptions:.1f} min: P(component 0) = {r.probability[0]:.4f}, "
          f"P(component 1) = {r.probability[1]:.4f}")
# The E-step by hand for x = 2.8: responsibility = pi_j N(x|mu_j,var_j) / sum
x = 2.8
terms = []
for i, row in enumerate(g2.gaussiansDF.collect()):
    mu, var = row["mean"][0], row["cov"].toArray()[0][0]
    dens = math.exp(-(x - mu) ** 2 / (2 * var)) / math.sqrt(2 * math.pi * var)
    terms.append(g2.weights[i] * dens)
    print(f"  E-step x={x}: pi_{i} * N(x | {mu:.4f}, {var:.4f}) = {g2.weights[i]:.4f} * "
          f"{dens:.6f} = {terms[-1]:.6f}")
print(f"  responsibility of component 0 = {terms[0]:.6f} / {sum(terms):.6f} = "
      f"{terms[0] / sum(terms):.4f}")
print(f"  eruptions between 2.5 and 3.5 min in the data: "
      f"{geyser.where('eruptions > 2.5 and eruptions < 3.5').count()} of {geyser.count()}")

spark.stop()
