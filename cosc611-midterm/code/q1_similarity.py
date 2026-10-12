"""
COSC 611 Big Data Analytics - Midterm, Question 1
Similarity measures computed with Apache Spark (PySpark).

Dataset: MovieLens "latest-small" ratings (F. M. Harper & J. A. Konstan, GroupLens,
University of Minnesota), as distributed in the R package dslabs ("movielens"):
100,004 ratings (0.5-5 stars) by 671 users on 9,066 movies.  File: data/movielens.csv.gz

Part A (hand-checkable): the 6 most-rated movies and the first 5 users (by userId)
          who rated at least 4 of them; 0 = "not rated".
Part B (at scale):       cosine nearest neighbours of one user over ALL 671 users,
          and Jaccard similarity of movie GENRE sets with MinHash LSH over ALL movies.

Run from the cosc611-midterm folder:  spark-submit code/q1_similarity.py
"""
import math
import os

from pyspark.sql import SparkSession, Row
from pyspark.sql import functions as F
from pyspark.ml.linalg import Vectors, SparseVector, VectorUDT
from pyspark.ml.feature import MinHashLSH, Normalizer, CountVectorizer
from pyspark.ml.stat import Correlation

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
spark = (SparkSession.builder.appName("Q1-Similarity")
         .master("local[*]").getOrCreate())
spark.sparkContext.setLogLevel("ERROR")

ratings = (spark.read.csv(os.path.join(DATA, "movielens.csv.gz"),
                          header=True, inferSchema=True)
           .select("userId", "movieId", "title", "genres", "rating"))
ratings.cache()
print("=== MovieLens ratings ===")
print(f"ratings = {ratings.count()}, users = {ratings.select('userId').distinct().count()}, "
      f"movies = {ratings.select('movieId').distinct().count()}")
ratings.show(5, truncate=False)

# ---------------------------------------------------------------------------
# PART A - small user x movie matrix taken from the real data
# ---------------------------------------------------------------------------
top = (ratings.groupBy("movieId", "title").count()
       .orderBy(F.desc("count"), "movieId").limit(6).collect())
top_ids = [r.movieId for r in top]
titles = [r.title for r in top]
print("=== The 6 most-rated movies ===")
for r in top:
    print(f"  {r.title:40s} rated by {r['count']} users")

sub = ratings.where(F.col("movieId").isin(top_ids))
users = [r.userId for r in sub.groupBy("userId").count()
         .where(F.col("count") >= 4).orderBy("userId").limit(5).collect()]
cells = {(r.userId, r.movieId): r.rating
         for r in sub.where(F.col("userId").isin(users)).collect()}
matrix = {u: [cells.get((u, m), 0.0) for m in top_ids] for u in users}

df = spark.createDataFrame(
    [Row(user=f"user{u}", features=Vectors.dense(v)) for u, v in matrix.items()])
print("=== Part A input: first 5 users who rated >= 4 of these movies (0 = not rated) ===")
print("columns:", titles)
df.show(truncate=False)

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


cols = ["euclidean", "euclid_sim", "manhattan", "cosine", "pearson", "jaccard"]
result = (pairs
          .withColumn("euclidean", euclidean("x", "y"))
          .withColumn("euclid_sim", 1 / (1 + F.col("euclidean")))
          .withColumn("manhattan", manhattan("x", "y"))
          .withColumn("cosine", cosine("x", "y"))
          .withColumn("pearson", pearson("x", "y"))
          .withColumn("jaccard", jaccard("x", "y"))
          .select("u1", "u2", *[F.round(c, 4).alias(c) for c in cols]))
result.cache()
print("=== Pairwise similarity / distance between users ===")
result.orderBy("u1", "u2").show(truncate=False)

target = f"user{users[-1]}"
print(f"=== Most similar user to {target} under each measure ===")
mine = result.where((F.col("u1") == target) | (F.col("u2") == target))
for c, best in [("euclidean", "min"), ("manhattan", "min"), ("cosine", "max"),
                ("pearson", "max"), ("jaccard", "max")]:
    row = mine.orderBy(F.col(c).asc() if best == "min" else F.col(c).desc(),
                       "u1", "u2").first()
    other = row.u2 if row.u1 == target else row.u1
    print(f"  {c:10s}: {other}  ({c} = {row[c]})")

# Cosine the Spark-native way: L2-normalise, then the dot product is the cosine
norm = Normalizer(inputCol="features", outputCol="unit", p=2.0).transform(df)
n1, n2 = norm.alias("n1"), norm.alias("n2")
dot = F.udf(lambda x, y: float(x.dot(y)), "double")
print("=== Cosine similarity via Normalizer + dot product (same values) ===")
(n1.crossJoin(n2).where(F.col("n1.user") < F.col("n2.user"))
 .select(F.col("n1.user").alias("u1"), F.col("n2.user").alias("u2"),
         F.round(dot("n1.unit", "n2.unit"), 4).alias("cosine"))
 .orderBy(F.desc("cosine")).show(truncate=False))

# Pearson matrix with MLlib Correlation.corr (correlates columns -> one column per user)
mdf = spark.createDataFrame(
    [(Vectors.dense([matrix[u][m] for u in users]),) for m in range(len(top_ids))], ["v"])
corr = Correlation.corr(mdf, "v", "pearson").head()[0].toArray()
names = [f"user{u}" for u in users]
print("=== Pearson correlation matrix between users (Correlation.corr) ===")
print("          " + "".join(f"{n:>8s}" for n in names))
for i, n in enumerate(names):
    print(f"{n:>9s} " + "".join(f"{corr[i][j]:8.3f}" for j in range(len(names))))

# ---------------------------------------------------------------------------
# PART B1 - cosine nearest neighbours of one user over ALL 671 users
# ---------------------------------------------------------------------------
n_movies = ratings.agg(F.max("movieId")).first()[0] + 1
vec = F.udf(lambda ids, rs: SparseVector(n_movies, sorted(zip(ids, rs))), VectorUDT())
uv = (ratings.groupBy("userId")
      .agg(F.collect_list("movieId").alias("ids"), F.collect_list("rating").alias("rs"))
      .select("userId", vec("ids", "rs").alias("features")))
unit = Normalizer(inputCol="features", outputCol="unit").transform(uv).select("userId", "unit")
me = unit.where(F.col("userId") == users[-1]).first().unit
bc = spark.sparkContext.broadcast(me)
cos_me = F.udf(lambda v: float(v.dot(bc.value)), "double")
print(f"=== Part B1: 5 nearest neighbours of user {users[-1]} among all users (cosine) ===")
(unit.where(F.col("userId") != users[-1])
 .select("userId", F.round(cos_me("unit"), 4).alias("cosine"))
 .orderBy(F.desc("cosine"), "userId").show(5))

# ---------------------------------------------------------------------------
# PART B2 - Jaccard similarity of genre sets, exact and with MinHash LSH
# ---------------------------------------------------------------------------
movies = (ratings.select("movieId", "title", "genres").distinct()
          .where(F.col("genres") != "(no genres listed)")
          .withColumn("genre_list", F.split("genres", r"\|")))
cvm = CountVectorizer(inputCol="genre_list", outputCol="g", binary=True).fit(movies)
movies = cvm.transform(movies).cache()
print(f"=== Part B2: genre sets of {movies.count()} movies, "
      f"{len(cvm.vocabulary)} distinct genres ===")
pick = ["Toy Story", "Jurassic Park", "Matrix, The", "Forrest Gump", "Pulp Fiction"]
sm = movies.where(F.col("title").isin(pick))
sm.select("title", "genres").orderBy("title").show(truncate=False)
x1, x2 = sm.alias("x1"), sm.alias("x2")
print("Exact Jaccard similarity of genre sets:")
(x1.crossJoin(x2).where(F.col("x1.title") < F.col("x2.title"))
 .select(F.col("x1.title").alias("movie1"), F.col("x2.title").alias("movie2"),
         F.round(F.size(F.array_intersect("x1.genre_list", "x2.genre_list")) /
                 F.size(F.array_union("x1.genre_list", "x2.genre_list")), 4)
         .alias("jaccard"))
 .orderBy(F.desc("jaccard"), "movie1").show(truncate=False))

mh = MinHashLSH(inputCol="g", outputCol="hashes", numHashTables=20, seed=42).fit(movies)
key = movies.where(F.col("title") == "Matrix, The").first().g
print("MinHash LSH approxNearestNeighbors of 'Matrix, The' over all movies "
      "(distCol = Jaccard distance = 1 - Jaccard):")
(mh.approxNearestNeighbors(movies, key, 6, distCol="jaccard_dist")
 .select("title", "genres", F.round("jaccard_dist", 4).alias("jaccard_dist"))
 .show(truncate=False))
join = mh.approxSimilarityJoin(movies, movies, 0.2, distCol="d") \
    .where(F.col("datasetA.movieId") < F.col("datasetB.movieId"))
print(f"approxSimilarityJoin: {join.count()} movie pairs with Jaccard >= 0.8 found "
      f"without comparing all {movies.count() * (movies.count() - 1) // 2:,} pairs")
# Exact check: brute-force over the 900-odd DISTINCT genre sets (weighted by how
# many movies share each set) gives the true number of pairs with Jaccard >= 0.8
gs = movies.groupBy("genres").agg(F.count("*").alias("n"), F.first("genre_list").alias("gl"))
ga, gb = gs.alias("ga"), gs.alias("gb")
exact = (ga.crossJoin(gb).where(F.col("ga.genres") <= F.col("gb.genres"))
         .where(F.size(F.array_intersect("ga.gl", "gb.gl")) /
                F.size(F.array_union("ga.gl", "gb.gl")) >= 0.8)
         .select(F.when(F.col("ga.genres") == F.col("gb.genres"),
                        F.col("ga.n") * (F.col("ga.n") - 1) / 2)
                 .otherwise(F.col("ga.n") * F.col("gb.n")).alias("p"))
         .agg(F.sum("p")).first()[0])
same = gs.agg(F.sum(F.col("n") * (F.col("n") - 1) / 2)).first()[0]
print(f"exact brute-force count = {int(exact):,} pairs "
      f"(of which {int(same):,} have identical genre sets) -> LSH recall = "
      f"{join.count() / exact:.4f}")

spark.stop()
