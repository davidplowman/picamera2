#!/bin/bash

count=0

while true
do
    python ~/pfc.py
    code=$?
    echo $count $code
    if [ $code -ne 0 ]; then
	exit 1
    fi
    count=$((count+1))
done
