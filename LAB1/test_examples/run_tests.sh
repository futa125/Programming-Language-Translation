#!/bin/bash

for (( i = 1; i <= 29; i = i + 2 ))
do
    dir=$(printf "%0*d\n" 2 $i)
    echo "Test $dir"
    res=`python3 ../LeksickiAnalizator.py < test_$dir/test.in | diff test_$dir/test.out -`
    if [ "$res" != "" ]
        then 
            echo "FAIL"
            echo $res
        else
            echo "OK"
        fi
done