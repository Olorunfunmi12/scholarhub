#!/bin/bash
# Runs each command for real and saves "prompt + command + combined output" transcripts.
cd /home/user/scholarhub/spark_hw1
unset JAVA_TOOL_OPTIONS
export PIP_PROGRESS_BAR=off PIP_ROOT_USER_ACTION=ignore PIP_DISABLE_PIP_VERSION_CHECK=1
PS='root@vm:~/spark_hw1$ '
run() { # $1=file, $2=prompt, rest=command
  f=$1; p=$2; shift 2
  printf '%s%s\n' "$p" "$*" >> "shots/$f.txt"
  bash -c "$*" >> "shots/$f.txt" 2>&1
}
rm -f shots/*.txt
rm -rf .venv output
run s1_install "$PS" "java -version"
run s1_install "$PS" "python3 --version"
run s1_install "$PS" "python3 -m venv .venv"
run s1_install "$PS" "source .venv/bin/activate"
. .venv/bin/activate
V='(.venv) root@vm:~/spark_hw1$ '
run s1_install "$V" "pip install --upgrade pip setuptools wheel | tail -1"
run s1_install "$V" "pip install pyspark | tail -2"
run s1_install "$V" "python -c \"import pyspark; print(pyspark.__version__)\""
echo "$V" >> shots/s1_install.txt
run s2_warn "$V" "python part1_wordcount.py"
echo "$V" >> shots/s2_warn.txt
run s3_fixed "$V" "export SPARK_LOCAL_IP=127.0.0.1"
export SPARK_LOCAL_IP=127.0.0.1
run s3_fixed "$V" "python part1_wordcount.py"
echo "$V" >> shots/s3_fixed.txt
run s4_ops "$V" "python part2_operations.py"
run s5_parquet "$V" "ls output/sales_parquet"
echo "$V" >> shots/s5_parquet.txt
