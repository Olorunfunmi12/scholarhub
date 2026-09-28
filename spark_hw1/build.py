from reportlab.lib.pagesizes import letter
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Preformatted, Table, TableStyle, PageBreak, KeepTogether)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon
import math

body = ParagraphStyle('b', fontName='Times-Roman', fontSize=12, leading=17, spaceAfter=8, alignment=0)
h1 = ParagraphStyle('h1', fontName='Times-Bold', fontSize=14, leading=18, spaceBefore=12, spaceAfter=8)
h2 = ParagraphStyle('h2', fontName='Times-Bold', fontSize=12, leading=16, spaceBefore=10, spaceAfter=4)
center = ParagraphStyle('c', fontName='Times-Roman', fontSize=12, alignment=1, leading=17)
titlest = ParagraphStyle('t', fontName='Times-Bold', fontSize=14, alignment=1, leading=18, spaceAfter=4)
cap = ParagraphStyle('cap', fontName='Times-Roman', fontSize=10.5, alignment=1, spaceAfter=10)
num = ParagraphStyle('n', parent=body, leftIndent=18, bulletIndent=0, spaceAfter=4, bulletFontName='Times-Roman', bulletFontSize=12)
mono = ParagraphStyle('m', fontName='Courier', fontSize=8.5, leading=10.5)

def P(t): return Paragraph(t, body)
def N(items): return [Paragraph(t, num, bulletText=f'{i}.') for i, t in enumerate(items, 1)]
def C(t):
    tb = Table([[Preformatted(t.strip('\n'), mono)]], colWidths=[6.5*inch])
    tb.setStyle(TableStyle([('BOX', (0,0), (-1,-1), 0.5, colors.black),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F2F2F2')),
        ('LEFTPADDING', (0,0), (-1,-1), 6), ('TOPPADDING', (0,0), (-1,-1), 5), ('BOTTOMPADDING', (0,0), (-1,-1), 5)]))
    tb.spaceBefore = 2; tb.spaceAfter = 10
    return tb
def cf(t): return f'<font face="Courier">{t}</font>'
rd = lambda f: open(f).read()

def simple_table(rows, widths):
    t = Table(rows, colWidths=widths)
    t.setStyle(TableStyle([('FONT', (0,0), (-1,-1), 'Times-Roman', 11), ('FONT', (0,0), (-1,0), 'Times-Bold', 11),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black), ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E6E6E6')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
    return t

def arch():
    d = Drawing(460, 150)
    def box(x, y, w, h, label, sub):
        d.add(Rect(x, y, w, h, fillColor=colors.white, strokeColor=colors.black, strokeWidth=1))
        d.add(String(x+w/2, y+h-15, label, textAnchor='middle', fontName='Times-Bold', fontSize=10))
        for i, s in enumerate(sub):
            d.add(String(x+w/2, y+h-29-11*i, s, textAnchor='middle', fontName='Times-Roman', fontSize=9))
    def arrow(x1, y1, x2, y2):
        d.add(Line(x1, y1, x2, y2, strokeColor=colors.black, strokeWidth=1))
        a = math.atan2(y2-y1, x2-x1); L = 6
        d.add(Polygon([x2, y2, x2-L*math.cos(a-0.4), y2-L*math.sin(a-0.4), x2-L*math.cos(a+0.4), y2-L*math.sin(a+0.4)],
                      fillColor=colors.black, strokeWidth=0))
    box(5, 45, 120, 60, 'Driver Program', ['SparkSession', '(plans the job)'])
    box(170, 45, 120, 60, 'Cluster Manager', ['local[*], Standalone,', 'YARN or Kubernetes'])
    box(335, 90, 120, 50, 'Executor', ['runs tasks'])
    box(335, 5, 120, 50, 'Executor', ['runs tasks'])
    arrow(125, 75, 170, 75); arrow(290, 85, 335, 112); arrow(290, 65, 335, 30)
    return d

s = []
s += [Paragraph('Morgan State University', center),
      Paragraph('Department of Computer Science', center),
      Paragraph('COSC 611 Big Data Analytics', center), Spacer(1, 8),
      Paragraph('HW Assignment 1: Apache Spark', titlest),
      Paragraph('Name: Olorunfunmi Shobowale', center),
      Paragraph('Date: September 28, 2026', center), Spacer(1, 16)]

# ---------------- Part 1 ----------------
s += [Paragraph('Part 1: Implementing Apache Spark and an Example Problem (40 points)', h1)]
s += [Paragraph('1.1 Background', h2),
 P('Apache Spark is an open source engine for processing large amounts of data across many machines. The main reason it '
   'became popular is that it keeps intermediate results in memory instead of writing them to disk between every step, '
   'which is what Hadoop MapReduce does. This makes Spark much faster for jobs that pass over the same data many times, '
   'like machine learning or interactive queries (Zaharia et al., 2016).'),
 P('A Spark program has a driver, which is the main program I write. The driver breaks the work into tasks and sends '
   'them to executors through a cluster manager. On a real cluster the executors run on different machines, but in local '
   'mode, which is what I used, everything runs on one computer and the executors are just threads. The nice part is '
   'that the same code works in both cases (Apache Software Foundation, 2026a).'),
 arch(), Paragraph('Figure 1. Basic parts of a Spark application. Redrawn from the Spark "Cluster Mode Overview" '
                   'page (Apache Software Foundation, 2026b).', cap)]

s += [Paragraph('1.2 My computing environment', h2),
 P('Table 1 shows the machine and software versions I used for this assignment.'),
 KeepTogether([simple_table([['Component', 'Version / setting'],
    ['Operating system', 'Ubuntu 24.04.4 LTS (64-bit Linux)'],
    ['Hardware', 'Intel Xeon @ 2.10 GHz, 4 CPU cores, 16 GB RAM'],
    ['Java (JDK)', 'OpenJDK 21.0.10'],
    ['Python', '3.11.15 (in a virtual environment)'],
    ['Apache Spark / PySpark', '4.2.0, installed with pip'],
    ['Deployment mode', 'Local mode, master = local[*]']], [2.0*inch, 4.2*inch]),
 Spacer(1, 4), Paragraph('Table 1. Environment used for this assignment.', cap)])]

s += [Paragraph('1.3 How I installed Spark', h2),
 P('Java was already installed on the machine, so I only had to check the version. Spark 4 needs Java 17 or 21, and I had 21. '
   'After that I made a virtual environment for Python and installed PySpark into it with pip. The PySpark package from pip '
   'already contains the whole Spark engine, so I did not need to download Spark separately for local mode. These are the '
   'commands I ran:'),
 C('''
$ java -version
openjdk version "21.0.10" 2026-01-20

$ python3 -m venv .venv
$ source .venv/bin/activate
(.venv)$ pip install --upgrade pip setuptools wheel
(.venv)$ pip install pyspark
(.venv)$ python -c "import pyspark; print(pyspark.__version__)"
4.2.0
'''),
 P('The install itself went through without errors. The problem I ran into came the first time I ran a Spark program. '
   'Before printing any results, Spark printed a few warnings, and one of them was this:'),
 C('''
WARN Utils: Your hostname, vm, resolves to a loopback address: 127.0.0.1;
            using 192.0.2.2 instead (on interface eth0)
WARN Utils: Set SPARK_LOCAL_IP if you need to bind to another address
'''),
 P('This happens because the machine name points to 127.0.0.1, so Spark is not sure which network address to use and '
   'picks one on its own. In local mode the program still ran fine, but on a real cluster the wrong address can stop the '
   'executors from reaching the driver. The warning itself tells you the fix, which is to set the ' + cf('SPARK_LOCAL_IP') +
   ' environment variable. I ran the program again with it set and the warning was gone:'),
 C('(.venv)$ export SPARK_LOCAL_IP=127.0.0.1\n(.venv)$ python part1_wordcount.py'),
 P('There was also a warning that says "Unable to load native-hadoop library for your platform". This one is normal in '
   'local mode. Spark just uses its built in Java code instead, so I left it alone. To keep the output readable I also '
   'set the log level to ERROR inside my scripts with ' + cf('setLogLevel("ERROR")') + '.')]

s += [Paragraph('1.4 Example problem: word count', h2),
 P('To test the installation I used the word count problem. The idea is simple. Given a text file, count how many times '
   'each word shows up and list the most common ones. It is used a lot as a first Spark program because it uses the same '
   'map, shuffle and reduce steps that bigger jobs use. My input file ' + cf('data.txt') + ' has five sentences about Spark.'),
 P('Code (' + cf('part1_wordcount.py') + '):'),
 C(rd('part1_wordcount.py')),
 P('Here is what each part does. ' + cf('textFile') + ' reads the file into an RDD where each element is one line. ' +
   cf('flatMap') + ' splits every line into words and puts them all in one list. ' + cf('map') + ' turns each word into '
   'a pair like ("spark", 1). ' + cf('reduceByKey') + ' adds up the numbers for each word, and this is the step where Spark '
   'has to move data between partitions (a shuffle). Last, ' + cf('sortBy') + ' puts the words in order from most to least '
   'common. One thing I found interesting is that none of this actually runs until ' + cf('count()') + ' or ' +
   cf('take()') + ' is called. Spark waits and builds a plan first, which is called lazy evaluation.'),
 P('Output:'),
 C('(.venv)$ python part1_wordcount.py\n' + rd('out1.txt')),
 P('The output shows that Spark is working. It started in local mode, it used all 4 cores (default parallelism is 4), '
   'it read all 5 lines, and the counts are correct. I checked "spark" by hand and it does appear 6 times in the file.')]

# ---------------- Part 2 ----------------
s += [PageBreak(), Paragraph('Part 2: Tutorial on Setting Up Spark and Running Basic Operations (50 points)', h1),
 P('This part is a step by step guide for someone starting from a normal computer with nothing installed. I wrote the '
   'commands for Linux and macOS and added notes where Windows is different.')]

s += [Paragraph('Step 1: Check the system requirements', h2),
 P('You need a 64-bit computer with at least 4 GB of RAM, but 8 GB or more is better. You also need about 1 GB of free '
   'disk space. Spark runs on Java, and Spark 4 works with Java 17 or Java 21 (Apache Software Foundation, 2026a). If you '
   'want to write Spark programs in Python, you also need Python 3.10 or newer.')]

s += [Paragraph('Step 2: Install Java', h2),
 C('''
# Ubuntu / Debian
$ sudo apt update
$ sudo apt install -y openjdk-21-jdk

# macOS with Homebrew
$ brew install openjdk@21

# Windows: download and install Eclipse Temurin JDK 21 from adoptium.net

# Check it on any system
$ java -version
'''),
 P('If Spark later says it cannot find Java, set the ' + cf('JAVA_HOME') + ' variable to the folder where the JDK is '
   'installed. On Linux that looks like ' + cf('export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64') + '. On Windows it '
   'is set under System Properties, Environment Variables.')]

s += [Paragraph('Step 3: Set up Python and a virtual environment', h2),
 P('I recommend a virtual environment so that Spark and its packages stay separate from everything else on the computer.'),
 C('''
$ python3 --version              # should be 3.10 or newer
$ python3 -m venv .venv          # Windows: python -m venv .venv
$ source .venv/bin/activate      # Windows: .venv\\Scripts\\activate
(.venv)$ pip install --upgrade pip setuptools wheel
''')]

s += [Paragraph('Step 4: Install Apache Spark', h2),
 P('There are two ways to do this. The first way is the one I used. You install PySpark with pip, and it comes with the '
   'full Spark engine, which is enough for running Spark on one computer (Apache Software Foundation, 2026c).'),
 C('(.venv)$ pip install pyspark'),
 P('The second way is to download the full Spark package from spark.apache.org/downloads, unzip it, and add it to your '
   'PATH. This also gives you ' + cf('spark-shell') + ' for Scala and ' + cf('spark-submit') + ' for sending jobs to a cluster.'),
 C('''
$ tar -xzf spark-4.x.x-bin-hadoop3.tgz
$ export SPARK_HOME=~/spark-4.x.x-bin-hadoop3
$ export PATH=$SPARK_HOME/bin:$PATH
'''),
 P('Windows users need one extra thing. Spark on Windows needs a file called ' + cf('winutils.exe') + '. Put it in ' +
   cf('C:\\hadoop\\bin') + ' and set ' + cf('HADOOP_HOME=C:\\hadoop') + '. If you skip this, saving files from Spark will '
   'fail with an error about HADOOP_HOME not being set.')]

s += [Paragraph('Step 5: Check that Spark works', h2),
 C('''
(.venv)$ python -c "import pyspark; print(pyspark.__version__)"
4.2.0
(.venv)$ pyspark        # opens the Spark shell, type exit() to leave
'''),
 P('If the version number prints and the shell opens with the Spark logo, the setup is done. As I mentioned in Part 1, '
   'if you see the loopback address warning, set ' + cf('SPARK_LOCAL_IP=127.0.0.1') + '.')]

s += [Paragraph('Step 6: Make some sample data', h2),
 P('I made two small CSV files so the results would be easy to check by hand. ' + cf('sales.csv') + ' has 10 orders and ' +
   cf('regions.csv') + ' has the manager for each region.'),
 C('sales.csv\n' + rd('sales.csv') + '\nregions.csv\n' + rd('regions.csv'))]

s += [Paragraph('Step 7: Run basic Spark operations', h2),
 P('The script below, ' + cf('part2_operations.py') + ', does seven basic operations. The first one uses RDDs, which is '
   'the older low level API, and the rest use DataFrames and Spark SQL, which is what most people use now. I ran it with ' +
   cf('python part2_operations.py') + ' and the output of each operation is shown after the code.'),
 C(rd('part2_operations.py'))]

sections = rd('out2.txt').split('=== ')[1:]
expl = [
 ('Operation 1: RDD map, filter and reduce',
  cf('parallelize') + ' takes a normal Python list of the numbers 1 to 10 and spreads it out as an RDD. ' + cf('map') +
  ' squares each number and ' + cf('filter') + ' keeps only the even squares. These two are transformations, so they do '
  'not run right away. ' + cf('collect') + ' and ' + cf('reduce') + ' are actions and they make Spark do the work. I checked '
  'the sum by hand: 1 + 4 + 9 + ... + 100 = 385, which matches.'),
 ('Operation 2: Load a CSV file into a DataFrame',
  'Because I used ' + cf('inferSchema=True') + ', Spark looked at the data and figured out the column types by itself '
  '(integer, string and double). ' + cf('printSchema') + ' shows the types and ' + cf('show(5)') + ' prints the first 5 rows.'),
 ('Operation 3: Add a column and filter rows',
  cf('withColumn') + ' makes a new column called revenue, which is quantity times unit_price. Then ' + cf('select') +
  ' keeps only three columns and ' + cf('filter') + ' keeps orders with revenue over $1,500. Six of the ten orders passed.'),
 ('Operation 4: Group by and aggregate',
  cf('groupBy') + ' with ' + cf('agg') + ' gives the total revenue and number of orders for each region. West is first '
  'with $6,190 from 3 orders. Checking by hand: 3050 + 1880 + 1260 = 6190.'),
 ('Operation 5: Join two DataFrames',
  'This joins the sales data with the regions file on the region column, so each order now shows its manager. It works '
  'the same way as an inner join in SQL.'),
 ('Operation 6: Spark SQL query',
  cf('createOrReplaceTempView') + ' registers the DataFrame as a table called sales, so I can query it with normal SQL. '
  'This query finds total units sold and average price for each product. Behind the scenes Spark turns SQL and '
  'DataFrame code into the same kind of plan (Apache Software Foundation, 2026d).'),
 ('Operation 7: Save to Parquet and read it back',
  'The last step saves the data as Parquet, which is a compressed column based file format that is common in big data. '
  'Then it reads the file back to make sure nothing was lost, and all 10 rows came back. When I looked in the output '
  'folder, Spark had written a folder instead of one file. Inside it were the data file and an empty file called ' +
  cf('_SUCCESS') + ' that shows the write finished.'),
]
for (hd, ex), sec in zip(expl, sections):
    out_txt = sec.split('===', 1)[1].strip('\n') if '===' in sec else sec
    s += [KeepTogether([Paragraph(hd, h2), P(ex), C(out_txt)])]

s += [Paragraph('Step 8: Watch the job and shut down', h2),
 P('While a Spark program is running you can open http://localhost:4040 in a browser. This is the Spark web UI, and it '
   'shows the jobs, stages and tasks, how long each one took, and how much memory is being used. It is the main place to '
   'look when a program is slow. At the end of every program you should call ' + cf('spark.stop()') + ' so that Spark '
   'gives back the memory and CPU it was using.')]

s += [KeepTogether([Paragraph('Summary of the operations', h2),
 simple_table([['#', 'Operation', 'API', 'Methods used'],
    ['1', 'Map, filter and reduce', 'RDD', 'parallelize, map, filter, reduce'],
    ['2', 'Load CSV data', 'DataFrame', 'read.csv, printSchema, show'],
    ['3', 'New column and filter', 'DataFrame', 'withColumn, select, filter'],
    ['4', 'Group and aggregate', 'DataFrame', 'groupBy, agg, sum, count'],
    ['5', 'Join', 'DataFrame', 'join'],
    ['6', 'SQL query', 'Spark SQL', 'createOrReplaceTempView, sql'],
    ['7', 'Save and reload', 'I/O', 'write.parquet, read.parquet']],
   [0.35*inch, 1.9*inch, 1.0*inch, 2.95*inch]),
 Spacer(1, 4), Paragraph('Table 2. The seven operations in the tutorial.', cap)])]

# ---------------- Part 3 ----------------
s += [PageBreak(), Paragraph('Part 3: Challenges and Limitations of Apache Spark (10 points)', h1),
 P('Getting Spark to run on one machine was not very hard, but while doing this assignment and reading about it I '
   'noticed several problems that would matter more on a real project.')]
s += N([
 'Spark needs a lot of memory. Its speed comes from keeping data in RAM, so RAM becomes the main cost. If the data '
 'does not fit in memory, Spark has to spill to disk, which makes it slow, or the job fails with an out of memory error. '
 'Picking the right memory and partition settings takes practice (Karau &amp; Warren, 2017).',
 'Versions have to match. Spark depends on the right versions of Java, Python or Scala, and the Hadoop libraries. Spark 4 '
 'does not run on Java 8 or 11 anymore. On Windows there is the extra winutils.exe and HADOOP_HOME step, which a lot of '
 'beginners get stuck on.',
 'Networking can cause problems. I saw this myself with the loopback address warning in Part 1. On one computer it '
 'was only a warning, but on a cluster the driver and executors must be able to reach each other, so the network has '
 'to be set up correctly.',
 'Errors are hard to track down. Because of lazy evaluation, a mistake in one line might not show up until an action '
 'runs much later. The error messages from PySpark also mix Python and Java stack traces, which makes them long and '
 'confusing.',
 'Shuffles are expensive. Operations like groupBy, join and reduceByKey have to move data between machines over the '
 'network. On big data this is often the slowest part of the job. If one key has much more data than the others '
 '(data skew), one task ends up doing most of the work.',
 'It is not the best choice for everything. For small data, Spark takes a few seconds just to start, so plain Python '
 'with pandas is often faster. For streaming, Spark works in small batches by default, so the delay is higher than '
 'tools built for handling one record at a time, like Apache Flink.',
 'Spark does not store data. It only does the processing, so it has to be used together with something like HDFS, '
 'Amazon S3 or a database. That means more systems to install, pay for and secure.',
 'Python UDFs are slow. When you write your own Python function and use it on a DataFrame, the data has to go back '
 'and forth between Java and Python. The built in Spark functions are much faster, so you have to learn to use them '
 'instead.',
 'Clusters cost money and need skills. Running Spark in production, on your own servers or on a cloud service like '
 'Databricks, Amazon EMR or Google Dataproc, can be expensive. The team also needs to know about distributed systems, '
 'tuning and security, since things like authentication and encryption are not turned on by default.'])
s += [Spacer(1, 4),
 P('Overall, Spark was easy to set up in local mode and it handled both the RDD and the DataFrame and SQL examples '
   'correctly. Most of its real difficulties show up at a larger scale, with memory, shuffles, tuning and running a '
   'cluster. Knowing these limits helps in deciding when Spark is worth using and when a simpler tool is good enough.')]

# ---------------- References ----------------
s += [PageBreak(), Paragraph('References', h1)]
refs = [
 'Apache Software Foundation. (2026a). <i>Apache Spark documentation: Overview</i>. https://spark.apache.org/docs/latest/',
 'Apache Software Foundation. (2026b). <i>Cluster mode overview</i>. https://spark.apache.org/docs/latest/cluster-overview.html',
 'Apache Software Foundation. (2026c). <i>PySpark installation</i>. https://spark.apache.org/docs/latest/api/python/getting_started/install.html',
 'Apache Software Foundation. (2026d). <i>Spark SQL, DataFrames and Datasets guide</i>. https://spark.apache.org/docs/latest/sql-programming-guide.html',
 'Karau, H., &amp; Warren, R. (2017). <i>High performance Spark: Best practices for scaling and optimizing Apache Spark</i>. O\'Reilly Media.',
 'Zaharia, M., Xin, R. S., Wendell, P., Das, T., Armbrust, M., Dave, A., Meng, X., Rosen, J., Venkataraman, S., Franklin, M. J., '
 'Ghodsi, A., Gonzalez, J., Shenker, S., &amp; Stoica, I. (2016). Apache Spark: A unified engine for big data processing. '
 '<i>Communications of the ACM, 59</i>(11), 56-65. https://doi.org/10.1145/2934664',
]
refst = ParagraphStyle('r', parent=body, leftIndent=24, firstLineIndent=-24)
s += [Paragraph(r, refst) for r in refs]

def footer(c, d):
    c.saveState(); c.setFont('Times-Roman', 10)
    c.drawString(inch, 0.55*inch, 'Olorunfunmi Shobowale, COSC 611 HW1')
    c.drawRightString(letter[0]-inch, 0.55*inch, str(d.page)); c.restoreState()

doc = SimpleDocTemplate('Shobowale_COSC611_HW1.pdf', pagesize=letter, leftMargin=inch, rightMargin=inch,
                        topMargin=inch, bottomMargin=0.9*inch, title='COSC 611 HW1 Apache Spark', author='Olorunfunmi Shobowale')
doc.build(s, onFirstPage=footer, onLaterPages=footer)
