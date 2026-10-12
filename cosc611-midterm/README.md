# COSC 611 Big Data Analytics — Midterm Take-Home

* `COSC611_Midterm_Report.md` / `.docx`: the written answers to Q1–Q4
* `code/`: the PySpark programs, one per question (submit these with the report)
* `outputs/`: the console output of each program, quoted in the report

## Running the code

The code needs Java 17 or 21, Python 3.9+, PySpark 4.x and SciPy. SciPy is used only
for p-values and cross-checks.

```bash
python3 -m venv sparkenv && . sparkenv/bin/activate
pip install pyspark==4.0.1 scipy numpy
python code/q1_similarity.py        > outputs/q1_similarity.txt
python code/q2_hypothesis_tests.py  > outputs/q2_hypothesis_tests.txt
python code/q3_clustering.py        > outputs/q3_clustering.txt
python code/q4_classification.py    > outputs/q4_classification.txt
```

You can also run each one with `spark-submit code/<file>.py`. Every script uses
`local[*]` mode and fixed random seeds, so the outputs are reproducible.
