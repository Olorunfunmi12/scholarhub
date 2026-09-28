from reportlab.lib.pagesizes import letter
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Preformatted, Table, TableStyle, PageBreak, KeepTogether)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon

ss = getSampleStyleSheet()
body = ParagraphStyle('b', parent=ss['BodyText'], fontName='Times-Roman', fontSize=11.5, leading=15, spaceAfter=6, alignment=4)
h1 = ParagraphStyle('h1', parent=ss['Heading1'], fontName='Times-Bold', fontSize=15, spaceBefore=10, spaceAfter=6, textColor=colors.HexColor('#1F3A5F'))
h2 = ParagraphStyle('h2', parent=ss['Heading2'], fontName='Times-Bold', fontSize=12.5, spaceBefore=8, spaceAfter=4, textColor=colors.HexColor('#1F3A5F'))
title = ParagraphStyle('t', fontName='Times-Bold', fontSize=16, alignment=1, leading=20, spaceAfter=4)
center = ParagraphStyle('c', fontName='Times-Roman', fontSize=12, alignment=1, leading=16)
bullet = ParagraphStyle('bl', parent=body, leftIndent=16, bulletIndent=4, spaceAfter=3)
code = ParagraphStyle('code', fontName='Courier', fontSize=8.3, leading=10.2, backColor=colors.HexColor('#F3F5F8'),
                      borderColor=colors.HexColor('#C9D1DC'), borderWidth=0.6, borderPadding=5, leftIndent=5, rightIndent=5, spaceBefore=4, spaceAfter=10)
out = ParagraphStyle('out', parent=code, backColor=colors.HexColor('#111827'), textColor=colors.HexColor('#E5E7EB'), borderColor=colors.HexColor('#111827'))
cap = ParagraphStyle('cap', fontName='Times-Italic', fontSize=10, alignment=1, spaceAfter=10)

def P(t): return Paragraph(t, body)
def B(items): return [Paragraph(i, bullet, bulletText='•') for i in items]
def _box(t, st, bg, bd):
    tb = Table([[Preformatted(t.strip('\n'), st)]], colWidths=[6.7*inch])
    tb.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),colors.HexColor(bg)),('BOX',(0,0),(-1,-1),0.6,colors.HexColor(bd)),
        ('LEFTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
    tb.spaceBefore=4; tb.spaceAfter=10
    return tb
codeP = ParagraphStyle('cp', fontName='Courier', fontSize=8.3, leading=10.2)
outP = ParagraphStyle('op', fontName='Courier', fontSize=8.3, leading=10.2, textColor=colors.HexColor('#E5E7EB'))
def C(t): return _box(t, codeP, '#F3F5F8', '#C9D1DC')
def O(t): return _box(t, outP, '#1E293B', '#1E293B')
rd = lambda f: open(f).read()

def arch():
    d = Drawing(460, 175)
    def box(x,y,w,h,label,sub,fill):
        d.add(Rect(x,y,w,h,fillColor=colors.HexColor(fill),strokeColor=colors.HexColor('#1F3A5F'),strokeWidth=1,rx=6,ry=6))
        d.add(String(x+w/2,y+h-16,label,textAnchor='middle',fontName='Helvetica-Bold',fontSize=10))
        for i,s in enumerate(sub): d.add(String(x+w/2,y+h-30-11*i,s,textAnchor='middle',fontName='Helvetica',fontSize=8))
    def arrow(x1,y1,x2,y2):
        d.add(Line(x1,y1,x2,y2,strokeColor=colors.HexColor('#1F3A5F'),strokeWidth=1.2))
        import math
        a=math.atan2(y2-y1,x2-x1); L=7
        d.add(Polygon([x2,y2,x2-L*math.cos(a-0.4),y2-L*math.sin(a-0.4),x2-L*math.cos(a+0.4),y2-L*math.sin(a+0.4)],fillColor=colors.HexColor('#1F3A5F'),strokeWidth=0))
    box(5,60,120,70,'Driver Program',['SparkSession /','SparkContext','(builds the DAG)'],'#DCE8F5')
    box(170,60,120,70,'Cluster Manager',['Standalone, YARN,','Kubernetes, or','local[*]'],'#FCE8C8')
    box(335,110,120,55,'Executor 1',['cache + tasks'],'#D8F0DC')
    box(335,10,120,55,'Executor 2',['cache + tasks'],'#D8F0DC')
    arrow(125,95,170,95); arrow(290,105,335,135); arrow(290,85,335,40)
    d.add(Line(65,60,65,0+37,strokeColor=colors.grey,strokeDashArray=[3,3]))
    d.add(Line(65,37,335,37,strokeColor=colors.grey,strokeDashArray=[3,3]))
    d.add(String(200,26,'driver sends tasks directly to executors',textAnchor='middle',fontName='Helvetica-Oblique',fontSize=7.5,fillColor=colors.grey))
    return d

s = []
s += [Paragraph('Department of Computer Science, Morgan State University', center),
      Paragraph('COSC 611 – Big Data Analytics', center), Spacer(1,6),
      Paragraph('HW Assignment 1: Implementing Apache Spark', title),
      Paragraph('<b>Name:</b> Olorunfunmi Shobowale', center),
      Paragraph('<b>Date:</b> September 28, 2026', center), Spacer(1,14)]

# ---------- Part 1 ----------
s += [Paragraph('Part 1 – Implementing Apache Spark and a Worked Example [40 pts]', h1)]
s += [Paragraph('1.1 What Apache Spark is', h2),
 P('Apache Spark is an open-source, distributed engine for processing large datasets. Its main idea is to keep intermediate '
   'data in memory instead of writing it to disk after every step, which is what made Hadoop MapReduce slow for iterative '
   'jobs such as machine learning and interactive queries (Zaharia et al., 2016). A Spark application is run by a <i>driver</i> '
   'program that splits the work into tasks and hands them to <i>executors</i> through a <i>cluster manager</i>. The same code '
   'can run on one laptop (local mode) or on a cluster of hundreds of machines (Apache Software Foundation, 2026a).'),
 arch(), Paragraph('Figure 1. Simplified Spark runtime architecture (adapted from the Spark Cluster Mode Overview, Apache Software Foundation, 2026b).', cap)]

s += [Paragraph('1.2 My computing environment', h2)]
t = Table([['Component','Version / setting'],
           ['Operating system','Ubuntu 24.04.4 LTS (64-bit Linux)'],
           ['Hardware','Intel Xeon @ 2.10 GHz, 4 CPU cores, 16 GB RAM'],
           ['Java (JDK)','OpenJDK 21.0.10'],
           ['Python','3.11.15 (in a virtual environment)'],
           ['Apache Spark / PySpark','4.2.0, installed from PyPI'],
           ['Deployment mode','Local mode, master = local[*] (uses all cores)']],
          colWidths=[2.0*inch,4.2*inch])
t.setStyle(TableStyle([('FONT',(0,0),(-1,-1),'Times-Roman',10.5),('FONT',(0,0),(-1,0),'Times-Bold',10.5),
    ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1F3A5F')),('TEXTCOLOR',(0,0),(-1,0),colors.white),
    ('GRID',(0,0),(-1,-1),0.5,colors.HexColor('#9AA5B4')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F3F5F8')]),
    ('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
s += [t, Spacer(1,6), Paragraph('Table 1. Environment used for the implementation.', cap)]

s += [Paragraph('1.3 Implementation steps', h2),
 P('I installed Spark in local mode, which is the standard way to develop and test Spark programs on a single machine. '
   'The commands I used were:'),
 C('''
# 1. Confirm Java is present (Spark 4.x needs Java 17 or 21)
$ java -version
openjdk version "21.0.10" 2026-01-20

# 2. Create an isolated Python environment
$ python3 -m venv ~/spark-env
$ source ~/spark-env/bin/activate
(spark-env)$ pip install --upgrade pip setuptools wheel

# 3. Install Spark (the pyspark package ships the full Spark runtime + jars)
(spark-env)$ pip install pyspark
(spark-env)$ python -c "import pyspark; print(pyspark.__version__)"
4.2.0
'''),
 P('<b>Problem I hit during installation:</b> installing <font face="Courier">pyspark</font> directly into the system '
   'Python failed with <i>"Failed building wheel for pyspark"</i> because the operating system\'s bundled '
   '<font face="Courier">setuptools</font>/<font face="Courier">wheel</font> packages were too old and could not be upgraded '
   '(Ubuntu marks them as system-managed). <b>Solution:</b> I created a Python virtual environment, upgraded '
   '<font face="Courier">pip</font>, <font face="Courier">setuptools</font> and <font face="Courier">wheel</font> inside it, '
   'and the installation then completed successfully. This is also a good habit in general because it keeps Spark\'s '
   'dependencies separate from the rest of the system.')]

s += [Paragraph('1.4 Example problem and solution: Word Count', h2),
 P('<b>Problem.</b> Given a text file, count how many times each word appears and list the most frequent words. Word count '
   'is the classic "hello world" of big-data processing because it uses the core map → shuffle → reduce pattern that '
   'larger jobs are built on. My input file <font face="Courier">data.txt</font> contains five sentences about Spark.'),
 P('<b>Solution (PySpark code, <font face="Courier">part1_wordcount.py</font>):</b>'),
 C(rd('part1_wordcount.py')),
 P('<b>How it works.</b> <font face="Courier">textFile</font> loads the file as an RDD of lines. '
   '<font face="Courier">flatMap</font> breaks each line into words, <font face="Courier">map</font> turns each word into a '
   '(word, 1) pair, <font face="Courier">reduceByKey</font> adds up the 1s for each word (this is where Spark shuffles data '
   'between partitions), and <font face="Courier">sortBy</font> orders the result. Nothing actually runs until '
   '<font face="Courier">count()</font> or <font face="Courier">take()</font> is called, because Spark transformations are '
   '<i>lazy</i>.'),
 P('<b>Command and actual output:</b>'),
 O('(spark-env)$ python part1_wordcount.py\n' + rd('out1.txt')),
 P('The output confirms Spark is correctly installed: the session started in local mode, used all four CPU cores '
   '(default parallelism = 4), read the file, and returned the correct counts ("spark" appears 6 times).')]

# ---------- Part 2 ----------
s += [PageBreak(), Paragraph('Part 2 – Tutorial: Preparing the Platform, Installing Spark, and Running Basic Operations [50 pts]', h1),
 P('This tutorial walks a beginner from a clean computer to running Spark programs. Steps are shown for Linux/macOS, with '
   'notes for Windows where the steps differ.')]

s += [Paragraph('Step 1 – Check system requirements', h2)] + B([
 '<b>Memory:</b> at least 4 GB RAM (8 GB or more is more comfortable).',
 '<b>Java:</b> Spark runs on the Java Virtual Machine. Spark 4.x supports Java 17 and 21 (Apache Software Foundation, 2026a).',
 '<b>Python:</b> a recent Python 3 release (3.10 or newer) if you want to use PySpark.',
 '<b>Disk:</b> about 1 GB free for Spark, Java and sample data.'])

s += [Paragraph('Step 2 – Install Java', h2),
 C('''
# Ubuntu / Debian
$ sudo apt update && sudo apt install -y openjdk-21-jdk
# macOS (Homebrew)
$ brew install openjdk@21
# Windows: download and install "Eclipse Temurin JDK 21" from adoptium.net

# Verify on any OS
$ java -version
'''),
 P('Set <font face="Courier">JAVA_HOME</font> to the JDK folder if Spark later complains that it cannot find Java, e.g. '
   '<font face="Courier">export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64</font> on Linux, or in '
   '<i>System Properties → Environment Variables</i> on Windows.')]

s += [Paragraph('Step 3 – Install Python and create a virtual environment', h2),
 C('''
$ python3 --version                 # confirm Python 3.10+
$ python3 -m venv ~/spark-env       # Windows: python -m venv %USERPROFILE%\\spark-env
$ source ~/spark-env/bin/activate   # Windows: %USERPROFILE%\\spark-env\\Scripts\\activate
(spark-env)$ pip install --upgrade pip setuptools wheel
''')]

s += [Paragraph('Step 4 – Install Apache Spark', h2),
 P('<b>Option A (simplest, used in this assignment):</b> install PySpark from PyPI. The package includes the complete Spark '
   'engine, so no separate download is needed for local work.'),
 C('(spark-env)$ pip install pyspark'),
 P('<b>Option B (full distribution):</b> download a pre-built package from spark.apache.org/downloads, extract it, and add it '
   'to your PATH. This option also gives you <font face="Courier">spark-shell</font> (Scala) and '
   '<font face="Courier">spark-submit</font> for cluster jobs.'),
 C('''
$ tar -xzf spark-4.x.x-bin-hadoop3.tgz
$ export SPARK_HOME=~/spark-4.x.x-bin-hadoop3
$ export PATH=$SPARK_HOME/bin:$PATH
'''),
 P('<b>Windows note:</b> Spark on Windows also needs <font face="Courier">winutils.exe</font> (Hadoop helper binaries). Put it in '
   '<font face="Courier">C:\\hadoop\\bin</font> and set <font face="Courier">HADOOP_HOME=C:\\hadoop</font>. Without it, writing '
   'files fails with a "HADOOP_HOME is unset" error.')]

s += [Paragraph('Step 5 – Verify the installation', h2),
 C('''
(spark-env)$ python -c "import pyspark; print(pyspark.__version__)"
4.2.0
(spark-env)$ pyspark          # opens the interactive shell; type exit() to quit
'''),
 P('If the version prints and the shell shows the Spark banner, the platform is ready. The warning '
   '<i>"Unable to load native-hadoop library"</i> is normal in local mode and can be ignored.')]

s += [Paragraph('Step 6 – Prepare sample data', h2),
 P('I created two small CSV files so every operation can be checked by hand:'),
 C('sales.csv\n' + rd('sales.csv') + '\nregions.csv\n' + rd('regions.csv'))]

s += [Paragraph('Step 7 – Run basic Spark operations', h2),
 P('The script <font face="Courier">part2_operations.py</font> below performs seven basic operations, covering both of Spark\'s '
   'main APIs: the low-level RDD API and the higher-level DataFrame/SQL API. Every result shown was produced by actually running '
   'the script with <font face="Courier">python part2_operations.py</font>.'),
 C(rd('part2_operations.py'))]

outtxt = rd('out2.txt')
sections = outtxt.split('=== ')[1:]
expl = [
 ('Operation 1 – RDD transformations and actions', '<font face="Courier">parallelize</font> distributes a Python list across partitions. '
  '<font face="Courier">map</font> and <font face="Courier">filter</font> are <i>transformations</i> (lazy); '
  '<font face="Courier">collect</font> and <font face="Courier">reduce</font> are <i>actions</i> that trigger computation. '
  'Check: 1^2 + 2^2 + ... + 10^2 = 385, which matches.'),
 ('Operation 2 – Reading a CSV into a DataFrame', 'With <font face="Courier">inferSchema=True</font>, Spark scans the file and assigns '
  'proper types (integer, string, double). <font face="Courier">printSchema</font> and <font face="Courier">show</font> let you inspect the data.'),
 ('Operation 3 – Creating a column and filtering', '<font face="Courier">withColumn</font> derives a new revenue column '
  '(quantity × unit_price), <font face="Courier">select</font> keeps only chosen columns, and <font face="Courier">filter</font> '
  'keeps orders above $1,500. Six of the ten orders qualify.'),
 ('Operation 4 – Grouping and aggregation', '<font face="Courier">groupBy</font> + <font face="Courier">agg</font> computes '
  'total revenue and order count per region. West leads with $6,190 from 3 orders (3050 + 1880 + 1260 = 6190).'),
 ('Operation 5 – Joining two DataFrames', 'An inner join on the <font face="Courier">region</font> key attaches each '
  'region\'s manager to every order, just like a SQL JOIN.'),
 ('Operation 6 – Querying with Spark SQL', '<font face="Courier">createOrReplaceTempView</font> registers the DataFrame as a table, '
  'so ordinary SQL can be used. Spark\'s Catalyst optimizer turns the SQL and the DataFrame code into the same execution plan.'),
 ('Operation 7 – Writing and reading Parquet', 'Results are saved in Parquet, a compressed columnar format used widely in big-data '
  'systems, then read back to confirm all 10 rows were stored. Spark writes a folder containing part-files and a '
  '<font face="Courier">_SUCCESS</font> marker.'),
]
for (hd, ex), sec in zip(expl, sections):
    body_out = sec.split('===',1)[1].strip('\n') if '===' in sec else sec
    s += [KeepTogether([Paragraph(hd, h2), P(ex), O(body_out)])]

s += [Paragraph('Step 8 – Monitor jobs and shut down', h2),
 P('While a Spark application is running, the <b>Spark Web UI</b> at <font face="Courier">http://localhost:4040</font> shows every '
   'job, stage, task, and cached dataset, which is the main tool for understanding performance. Always call '
   '<font face="Courier">spark.stop()</font> at the end of a program to release memory and CPU.'),
 ]
t2 = Table([['#','Operation','API','Key methods'],
 ['1','RDD transformations/actions','RDD','parallelize, map, filter, reduce'],
 ['2','Load CSV data','DataFrame','read.csv, printSchema, show'],
 ['3','Derive column & filter','DataFrame','withColumn, select, filter'],
 ['4','Group & aggregate','DataFrame','groupBy, agg, sum, count'],
 ['5','Join datasets','DataFrame','join'],
 ['6','SQL query','Spark SQL','createOrReplaceTempView, sql'],
 ['7','Save & reload','I/O','write.parquet, read.parquet']], colWidths=[0.3*inch,1.9*inch,0.95*inch,3.05*inch])
t2.setStyle(t.getStyle() if hasattr(t,'getStyle') else None)
t2.setStyle(TableStyle([('FONT',(0,0),(-1,-1),'Times-Roman',10),('FONT',(0,0),(-1,0),'Times-Bold',10),
    ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1F3A5F')),('TEXTCOLOR',(0,0),(-1,0),colors.white),
    ('GRID',(0,0),(-1,-1),0.5,colors.HexColor('#9AA5B4')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F3F5F8')])]))
s += [KeepTogether([Paragraph('Summary of operations demonstrated', h2), t2])]

# ---------- Part 3 ----------
s += [PageBreak(), Paragraph('Part 3 – Challenges and Limitations of Implementing Apache Spark [10 pts]', h1),
 P('Although Spark is powerful, my own setup and further reading showed several practical challenges:')]
s += B([
 '<b>Heavy dependence on memory.</b> Spark is fast because it keeps data in RAM, but that makes RAM the main cost and the main '
 'point of failure. If partitions do not fit in executor memory, Spark spills to disk (losing its speed advantage) or fails '
 'with out-of-memory errors. Sizing executor memory, cores and partitions correctly takes experience (Karau &amp; Warren, 2017).',
 '<b>Installation and version compatibility.</b> Spark depends on matching versions of Java, Python/Scala, and Hadoop libraries. '
 'I experienced this directly: the install failed until I isolated it in a virtual environment. On Windows, the extra '
 '<font face="Courier">winutils.exe</font> and <font face="Courier">HADOOP_HOME</font> step is a common stumbling block, and '
 'Spark 4 no longer runs on Java 8 or 11.',
 '<b>Difficult tuning and debugging.</b> Because execution is lazy and distributed, an error in one line may only appear when '
 'an action runs much later, and stack traces mix Python and Java (JVM) messages. Performance problems such as data skew '
 '(one partition much larger than the others) or excessive shuffles require reading the Spark UI to diagnose.',
 '<b>Expensive shuffles.</b> Wide operations like <font face="Courier">groupBy</font>, <font face="Courier">join</font> and '
 '<font face="Courier">reduceByKey</font> move data across the network. On a real cluster, shuffles are often the biggest '
 'bottleneck.',
 '<b>Not ideal for true real-time or small workloads.</b> Structured Streaming processes data in micro-batches by default, so '
 'latency is usually in the hundreds of milliseconds, higher than engines built for record-at-a-time streaming such as Apache Flink. '
 'For small datasets, Spark\'s start-up overhead makes it slower than plain pandas or a single database.',
 '<b>No storage layer of its own.</b> Spark is a compute engine only. It must be paired with HDFS, Amazon S3, a database, or '
 'a table format such as Delta Lake, which adds more components to install and secure.',
 '<b>Python overhead.</b> PySpark code that uses plain Python UDFs has to move data between the JVM and Python processes, which '
 'is slower than built-in DataFrame functions. Developers must learn to prefer built-in functions.',
 '<b>Cost and skills.</b> Production clusters (on-premises or cloud services like Databricks, Amazon EMR, or Google Dataproc) '
 'can be expensive, and teams need skills in distributed systems, cluster management and security (authentication, '
 'encryption, access control are not all enabled by default).'])
s += [P('<b>Conclusion.</b> Spark was straightforward to set up in local mode once the environment was isolated, and it handled '
        'both RDD and DataFrame/SQL workloads correctly. Its real challenges appear at scale, in memory management, shuffles, '
        'tuning and operating a cluster. Knowing these limits helps decide when Spark is the right tool and when a simpler one is enough.')]

s += [PageBreak(), Paragraph('References', h1)]
refs = [
 'Apache Software Foundation. (2026a). <i>Apache Spark documentation: Overview and downloading</i>. https://spark.apache.org/docs/latest/',
 'Apache Software Foundation. (2026b). <i>Cluster mode overview</i>. https://spark.apache.org/docs/latest/cluster-overview.html',
 'Apache Software Foundation. (2026c). <i>PySpark getting started: Installation</i>. https://spark.apache.org/docs/latest/api/python/getting_started/install.html',
 'Apache Software Foundation. (2026d). <i>Spark SQL, DataFrames and Datasets guide</i>. https://spark.apache.org/docs/latest/sql-programming-guide.html',
 'Karau, H., &amp; Warren, R. (2017). <i>High performance Spark: Best practices for scaling and optimizing Apache Spark</i>. O\'Reilly Media.',
 'Zaharia, M., Xin, R. S., Wendell, P., Das, T., Armbrust, M., Dave, A., Meng, X., Rosen, J., Venkataraman, S., Franklin, M. J., '
 'Ghodsi, A., Gonzalez, J., Shenker, S., &amp; Stoica, I. (2016). Apache Spark: A unified engine for big data processing. '
 '<i>Communications of the ACM, 59</i>(11), 56–65. https://doi.org/10.1145/2934664',
]
refst = ParagraphStyle('r', parent=body, leftIndent=22, firstLineIndent=-22, alignment=0, fontSize=10.5)
s += [Paragraph(r, refst) for r in refs]

def footer(c, d):
    c.saveState(); c.setFont('Times-Roman',9); c.setFillColor(colors.grey)
    c.drawString(inch*0.9, 0.55*inch, 'COSC 611 HW1 – Olorunfunmi Shobowale')
    c.drawRightString(letter[0]-inch*0.9, 0.55*inch, f'Page {d.page}'); c.restoreState()

doc = SimpleDocTemplate('Shobowale_COSC611_HW1.pdf', pagesize=letter, leftMargin=0.9*inch, rightMargin=0.9*inch,
                        topMargin=0.8*inch, bottomMargin=0.8*inch, title='COSC 611 HW1 - Apache Spark', author='Olorunfunmi Shobowale')
doc.build(s, onFirstPage=footer, onLaterPages=footer)
