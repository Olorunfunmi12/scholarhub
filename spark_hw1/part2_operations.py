from pyspark.sql import SparkSession, functions as F
spark = SparkSession.builder.appName("COSC611-BasicOps").master("local[*]").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

print("=== Op 1: Create an RDD and apply map / filter / reduce ===")
rdd = spark.sparkContext.parallelize(range(1, 11))
squares = rdd.map(lambda x: x * x)
evens = squares.filter(lambda x: x % 2 == 0)
print("squares:", squares.collect())
print("even squares:", evens.collect())
print("sum of squares:", squares.reduce(lambda a, b: a + b))

print("\n=== Op 2: Load a CSV file into a DataFrame ===")
df = spark.read.csv("sales.csv", header=True, inferSchema=True)
df.printSchema()
df.show(5)

print("=== Op 3: Select, add a column, and filter ===")
df2 = df.withColumn("revenue", F.col("quantity") * F.col("unit_price"))
df2.select("order_id", "product", "revenue").filter(F.col("revenue") > 1500).show()

print("=== Op 4: Group by and aggregate ===")
(df2.groupBy("region")
    .agg(F.sum("revenue").alias("total_revenue"), F.count("*").alias("orders"))
    .orderBy(F.desc("total_revenue"))
    .show())

print("=== Op 5: Join two DataFrames ===")
regions = spark.read.csv("regions.csv", header=True, inferSchema=True)
(df2.join(regions, on="region", how="inner")
    .select("order_id", "region", "manager", "revenue")
    .orderBy("order_id")
    .show())

print("=== Op 6: Spark SQL query ===")
df2.createOrReplaceTempView("sales")
spark.sql("""
    SELECT product, SUM(quantity) AS units, ROUND(AVG(unit_price),2) AS avg_price
    FROM sales GROUP BY product ORDER BY units DESC
""").show()

print("=== Op 7: Write results to disk (Parquet) and read back ===")
df2.write.mode("overwrite").parquet("output/sales_parquet")
back = spark.read.parquet("output/sales_parquet")
print("rows read back from Parquet:", back.count())
spark.stop()
