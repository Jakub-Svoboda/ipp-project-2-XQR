#!/bin/bash

# VUT FIT
# IPP Projekt - XQR (python3) 2014/2015
# Autor: Lucie Sedláčková
# Spuštění: 1) chmod +x tester.sh 
#           2) ./tester.sh

INTERPRET='python3'
SCRIPT=xqr.py

rm -f tests/*.log 

if [ ! -e $SCRIPT ]
then
  echo "$SCRIPT NOT FOUND!"
  exit
else
  head -3 $SCRIPT > tests/third_line
  tail -1l tests/third_line > tests/third_line.log
  rm -f tests/third_line
  thr=`cat tests/third_line.log`
  if [ ${#thr} -lt 13 ]
  then 
    echo "Treti radek skriptu: FAIL"
  else
    if [ ${thr:0:5} = '#XQR:' ]
    then
      echo "Treti radek skriptu: "
      echo "${thr:0:5} OK"
      echo "Zadany LOGIN: ${thr:5:8}"
      echo 'Zbytek radku: "'${thr:13}'"'
    else
      echo "Treti radek skriptu: FAIL"
    fi
  fi
fi

##### TESTY NA PARAMETRY:
echo "------- PARAMETRY (err_code/ref) ------"
echo "PARAMETRY: " >> tests/all.log 2>&1

$INTERPRET $SCRIPT --help > tests/help.log
if [[ $? -eq 0 ]]
then
  echo "TEST --help                (0)     OK"
  echo "--------------- NAPOVEDA --------------"
  cat tests/help.log
else
  echo "TEST --help                (0)     FAIL"
fi

echo "<?xml version=\"1.0\" encoding=\"UTF-8\" ?><el>hello</el>" | $INTERPRET $SCRIPT --query='SELECT el FROM ROOT' >> tests/stdin.log 2>&1
if [[ $? -eq 0 ]]
then 
  echo "TEST stdin + --query       (0)     OK"
  java -jar /pub/courses/ipp/jexamxml/jexamxml.jar tests/stdin.log tests/test001.ref delta.xml /pub/courses/ipp/jexamxml/xqr_options >> tests/all.log 2>&1
  if [[ $? -eq 0 ]]
  then
    echo "TEST stdin + --query       (ref)   OK"
  else
    echo "TEST stdin + --query       (ref)   FAIL"
  fi
else
  echo "TEST stdin + --query       (0)     FAIL"
fi

$INTERPRET $SCRIPT --input=tests/input-file1.xml --input=ddd --query='SELECT el FROM ROOT' >> tests/all.log 2>&1
if [[ $? -eq 1 ]]
then
  echo "TEST opakujici se          (1)     OK"
else
  echo "TEST opakujici se          (1)     FAIL"
fi

$INTERPRET $SCRIPT --help --input=tests/input-file1.xml --query='SELECT el FROM ROOT' >> tests/all.log 2>&1
if [[ $? -eq 1 ]]
then
  echo "TEST --help + jiny         (1)     OK"
else
  echo "TEST --help + jiny         (1)     FAIL"
fi

$INTERPRET $SCRIPT --input=tests/input-file1.xml -m --query='SELECT el FROM ROOT' >> tests/all.log 2>&1
if [[ $? -eq 1 ]]
then
  echo "TEST jiny                  (1)     OK"
else
  echo "TEST jiny                  (1)     FAIL"
fi

$INTERPRET $SCRIPT --root=root --input=tests/input-file1.xml >> tests/no.log 2>&1
if [[ $? -eq 0 ]]
then
  echo "TEST neni dotaz            (0)     OK"
  java -jar /pub/courses/ipp/jexamxml/jexamxml.jar tests/no.log tests/test002.ref delta.xml /pub/courses/ipp/jexamxml/xqr_options >> tests/all.log 2>&1
  if [[ $? -eq 0 ]]
  then
    echo "TEST neni dotaz            (ref)   OK"
  else
    echo "TEST neni dotaz            (ref)   FAIL"
  fi
else
  echo "TEST neni dotaz            (0)     FAIL"
fi

$INTERPRET $SCRIPT --qf=tests/que001.qu --input=tests/input-file1.xml --query='SELECT el FROM ROOT' >> tests/all.log 2>&1
if [[ $? -eq 1 ]]
then
  echo "TEST --qf + --query        (1)     OK"
else
  echo "TEST --qf + --query        (1)     FAIL"
fi

$INTERPRET $SCRIPT --input=tests/input-file0.xml --query='SELECT el FROM ROOT' >> tests/all.log 2>&1
if [[ $? -eq 2 ]]
then
  echo "TEST input neex            (2)     OK"
else
  echo "TEST input neex            (2)     FAIL"
fi

i=1
$INTERPRET $SCRIPT --root=root --input=tests/input-file1.xml --qf=tests/que00$i.qu --output=tests/out00$i.log >> tests/all.log 2>&1
if [[ $? -eq 0 ]]
then 
  echo "TEST neni dotaz 2          (0)     OK"
  java -jar /pub/courses/ipp/jexamxml/jexamxml.jar tests/out00$i.log tests/test002.ref delta.xml /pub/courses/ipp/jexamxml/xqr_options >> tests/all.log 2>&1
  if [[ $? -eq 0 ]]
  then
    echo "TEST neni dotaz 2          (ref)   OK"
  else
    echo "TEST neni dotaz 2          (ref)   FAIL"
  fi
else
  echo "TEST neni dotaz 2          (0)     FAIL"
fi

echo "----------- DOTAZY (chybne) -----------"
echo "DOTAZY: " >> tests/all.log 2>&1

i=2
while [[ $i -lt 10 ]]
do
  echo $i":" >> tests/all.log
  $INTERPRET $SCRIPT --input=tests/input-file1.xml --qf=tests/que00$i.qu --output=tests/out00$i.log >> tests/all.log 2>&1
  if [[ $? -eq 80 ]]
  then
    x=`cat tests/que00$i.qu`
    echo "TEST dotaz 00$i             (80)    OK     \"$x\""
  else
    x=`cat tests/que00$i.qu`
    echo "TEST dotaz 00$i             (80)    FAIL   \"$x\""
  fi
  i=`expr $i + 1`
done

while [[ $i -lt 41 ]]
do
  echo $i":" >> tests/all.log
  $INTERPRET $SCRIPT --input=tests/input-file1.xml --qf=tests/que0$i.qu --output=out0$i.log >> tests/all.log 2>&1
  if [[ $? -eq 80 ]]
  then
    x=`cat tests/que0$i.qu`
    echo "TEST dotaz 0$i             (80)    OK     \"$x\""
  else
    x=`cat tests/que0$i.qu`
    echo "TEST dotaz 0$i             (80)    FAIL   \"$x\""
  fi
  i=`expr $i + 1`
done

echo "----------- DOTAZY (spravne) ----------"
echo "DOTAZY (spravne): " >> tests/all.log 2>&1
i=50
while [[ $i -lt 93 ]]
do
  echo $i":" >> tests/all.log
  $INTERPRET $SCRIPT --root=root --input=tests/input-file2.xml --qf=tests/test0$i.qu --output=tests/out0$i.log >> tests/all.log 2>&1
  if [[ $? -eq 0 ]]
  then
    x=`cat tests/test0$i.qu`
    echo "TEST 0$i                   (0)     OK     \"$x\"" 
    java -jar /pub/courses/ipp/jexamxml/jexamxml.jar tests/out0$i.log tests/test0$i.ref delta.xml /pub/courses/ipp/jexamxml/xqr_options >> tests/all.log 2>&1
    if [[ $? -eq 0 ]]
    then
      echo "TEST 0$i                   (ref)   OK"
    else
      echo "TEST 0$i                   (ref)   FAIL"
    fi
  else
    x=`cat tests/test0$i.qu`
    echo "TEST 0$i                   (0)     FAIL   \"$x\""
  fi
  i=`expr $i + 1`
done



