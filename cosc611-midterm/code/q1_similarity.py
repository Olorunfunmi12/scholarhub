"""
COSC 611 Big Data Analytics - Midterm, Question 1
Similarity measures computed with Apache Spark (PySpark).

Example data: five users rating five movies on a 0-5 scale (0 = not rated).
We compute, for every pair of users:
  * Euclidean distance and the similarity derived from it, 1 / (1 + d)
  * Manhattan (L1) distance
  * Cosine similarity
  * Pearson correlation
  * Jaccard similarity on the *sets* of movies each user watched
    (exact, then approximated at scale with MinHash LSH)

Run:  spark-submit q1_similarity.py      (or: python3 q1_similarity.py)
"""
import math
from itertools import combinations

from pyspark.sql import SparkSession, Row
from pyspark.sql import functions as F
from pyspark.ml.linalg import Vectors, VectorUDT
from pyspark.ml.feature import MinHashLSH, Normalizer
from pyspark.ml.stat import Correlation

spark = (SparkSession.builder.appName("Q1-Similarity")
         .master("local[*]").getOrCreate())
spark.sparkContext.setLogLevel("ERROR")

MOVIES = ["Inception", "Titanic", "Avatar", "Matrix", "Frozen"]
ratings = {
    "Alice": [5, 3, 0, 4, 1],
    "Bob":   [4, 0, 0, 5, 1],
    "Carol": [1, 5, 4, 0, 5],
    "Dave":  [5, 4, 1, 4, 0],
    "Eve":   [0, 5, 5, 1, 4],
}

df = spark.createDataFrame(
    [Row(user=u, features=Vectors.dense(r)) for u, r in ratings.items()])
print("=== Input data: user x movie rating matrix ===")
print("columns:", MOVIES)
df.show(truncate=False)

# ---------------------------------------------------------------------------
# 1. Pairwise similarities with a self cross-join (every pair once)
# ---------------------------------------------------------------------------
a, b = df.alias("a"), df.alias("b")
pairs = a.crossJoin(b).where(F.col("a.user") < F.col("b.user")).select(
    F.col("a.user").alias("u1"), F.col("b.user").alias("u2"),
    F.col("a.features").alias("x"), F.col("b.features").alias("y"))


@F.udf("double")
def euclidean(x, y):
    return float(math.sqrt(Vectors.squared_distance(x, y)))


@F.udf("double")
def manhattan(x, y):
    return float(sum(abs(p - q) for p, q in zip(x, y)))


@F.udf("double")
def cosine(x, y):
    return float(x.dot(y) / (x.norm(2) * y.norm(2)))


@F.udf("double")
def pearson(x, y):
    mx, my = sum(x) / len(x), sum(y) / len(y)
    num = sum((p - mx) * (q - my) for p, q in zip(x, y))
    den = math.sqrt(sum((p - mx) ** 2 for p in x)) * \
        math.sqrt(sum((q - my) ** 2 for q in y))
    return float(num / den)


@F.udf("double")
def jaccard(x, y):
    s1 = {i for i, v in enumerate(x) if v > 0}
    s2 = {i for i, v in enumerate(y) if v > 0}
    return float(len(s1 & s2) / len(s1 | s2))


result = (pairs
          .withColumn("euclidean", euclidean("x", "y"))
          .withColumn("euclid_sim", 1 / (1 + F.col("euclidean")))
          .withColumn("manhattan", manhattan("x", "y"))
          .withColumn("cosine", cosine("x", "y"))
          .withColumn("pearson", pearson("x", "y"))
          .withColumn("jaccard", jaccard("x", "y"))
          .drop("x", "y"))
cols = ["euclidean", "euclid_sim", "manhattan", "cosine", "pearson", "jaccard"]
result = result.select("u1", "u2", *[F.round(c, 4).alias(c) for c in cols])
print("=== Pairwise similarity / distance between users ===")
result.orderBy("u1", "u2").show(truncate=False)

print("=== Most similar user to Alice under each measure ===")
alice = result.where((F.col("u1") == "Alice") | (F.col("u2") == "Alice"))
for c, best in [("euclidean", "min"), ("manhattan", "min"), ("cosine", "max"),
                ("pearson", "max"), ("jaccard", "max")]:
    row = alice.orderBy(F.col(c).asc() if best == "min" else F.col(c).desc()).first()
    other = row.u2 if row.u1 == "Alice" else row.u1
    print(f"  {c:10s}: {other}  ({c} = {row[c]})")

# ---------------------------------------------------------------------------
# 2. Cosine similarity the "Spark-native" way: L2-normalise then dot product
# ---------------------------------------------------------------------------
norm = Normalizer(inputCol="features", outputCol="unit", p=2.0).transform(df)
n1, n2 = norm.alias("n1"), norm.alias("n2")
dot = F.udf(lambda x, y: float(x.dot(y)), "double")
cos_native = (n1.crossJoin(n2).where(F.col("n1.user") < F.col("n2.user"))
              .select(F.col("n1.user").alias("u1"), F.col("n2.user").alias("u2"),
                      F.round(dot("n1.unit", "n2.unit"), 4).alias("cosine")))
print("=== Cosine similarity via Normalizer + dot product (same values) ===")
cos_native.orderBy(F.desc("cosine")).show(truncate=False)

# ---------------------------------------------------------------------------
# 3. Pearson correlation matrix with Spark MLlib's Correlation.corr
#    (correlates columns, so we transpose: one row per movie, one column per user)
# ---------------------------------------------------------------------------
users = list(ratings)
movie_rows = [(Vectors.dense([ratings[u][m] for u in users]),)
              for m in range(len(MOVIES))]
mdf = spark.createDataFrame(movie_rows, ["v"])
corr = Correlation.corr(mdf, "v", "pearson").head()[0].toArray()
print("=== Pearson correlation matrix between users (Correlation.corr) ===")
print("         " + "".join(f"{u:>8s}" for u in users))
for i, u in enumerate(users):
    print(f"{u:>8s} " + "".join(f"{corr[i][j]:8.3f}" for j in range(len(users))))

# ---------------------------------------------------------------------------
# 4. Jaccard similarity at scale: MinHash LSH on the "watched" sets
#    approxSimilarityJoin returns Jaccard *distance* = 1 - Jaccard similarity
# ---------------------------------------------------------------------------
watched = spark.createDataFrame(
    [Row(user=u, set=Vectors.sparse(len(MOVIES),
                                    [(i, 1.0) for i, v in enumerate(r) if v > 0]))
     for u, r in ratings.items()])
mh = MinHashLSH(inputCol="set", outputCol="hashes", numHashTables=50, seed=42)
model = mh.fit(watched)
approx = (model.approxSimilarityJoin(watched, watched, threshold=1.0,
                                     distCol="jaccard_dist")
          .where(F.col("datasetA.user") < F.col("datasetB.user"))
          .select(F.col("datasetA.user").alias("u1"),
                  F.col("datasetB.user").alias("u2"),
                  F.round(1 - F.col("jaccard_dist"), 4).alias("approx_jaccard")))
print("=== Approximate Jaccard similarity with MinHash LSH (50 hash tables) ===")
(approx.join(result.select("u1", "u2", "jaccard"), ["u1", "u2"])
 .orderBy("u1", "u2").show(truncate=False))

# ---------------------------------------------------------------------------
# 5. Text example: Jaccard and cosine on documents (bag of words)
# ---------------------------------------------------------------------------
from pyspark.ml.feature import Tokenizer, CountVectorizer

docs = spark.createDataFrame([
    (0, "big data analytics with spark"),
    (1, "spark makes big data processing fast"),
    (2, "the cat sat on the mat"),
], ["id", "text"])
tok = Tokenizer(inputCol="text", outputCol="words").transform(docs)
cv = CountVectorizer(inputCol="words", outputCol="tf").fit(tok).transform(tok)
d1, d2 = cv.alias("d1"), cv.alias("d2")
doc_sim = (d1.crossJoin(d2).where(F.col("d1.id") < F.col("d2.id"))
           .select(F.col("d1.id").alias("doc1"), F.col("d2.id").alias("doc2"),
                   F.round(cosine("d1.tf", "d2.tf"), 4).alias("cosine"),
                   F.round(F.size(F.array_intersect("d1.words", "d2.words")) /
                           F.size(F.array_union("d1.words", "d2.words")), 4)
                   .alias("jaccard")))
print("=== Document similarity (bag-of-words) ===")
docs.show(truncate=False)
doc_sim.show(truncate=False)

spark.stop()
