#!/bin/bash

for (( i = 1; i <= 20; i = i + 1 ))
do
    index=$(printf "%0*d\n" 2 $i)
    echo "Test $index"
    dir_name=$(find . -type d -name "*$index")
    res=`python3 ../SemantickiAnalizator.py < $dir_name/Test.in | diff $dir_name/Test.out -`
    if [ "$res" != "" ]
        then 
            echo "FAIL"
            echo $res
        else
            echo "OK"
        fi
done