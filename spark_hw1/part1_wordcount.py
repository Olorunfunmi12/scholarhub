from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("COSC611-WordCount").master("local[*]").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")
print("Spark version:", spark.version)
print("Master:", spark.sparkContext.master)
print("Default parallelism:", spark.sparkContext.defaultParallelism)

lines = spark.sparkContext.textFile("data.txt")
counts = (lines.flatMap(lambda line: line.lower().split())
               .map(lambda word: (word, 1))
               .reduceByKey(lambda a, b: a + b)
               .sortBy(lambda kv: -kv[1]))
print("Total lines:", lines.count())
print("Top 8 words:")
for word, n in counts.take(8):
    print(f"  {word:<12}{n}")
spark.stop()
