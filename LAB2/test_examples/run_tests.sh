#!/bin/bash

for (( i = 1; i <= 39; i = i + 2 ))
do
    index=$(printf "%0*d\n" 2 $i)
    echo "Test $index"
    dir_name=$(find . -type d -name "$index*")
    res=`python3 ../SintaksniAnalizator.py < $dir_name/test.in | diff $dir_name/test.out -`
    if [ "$res" != "" ]
        then 
            echo "FAIL"
            echo $res
        else
            echo "OK"
        fi
done
