#! /usr/bin/env bash

for file in $(find -name '*.py')
do
  # echo 'processing' $file
  # if grep -Fxq '          "status": 302,' $file
  if grep -Eq "SPIDER_MIDDLEWARES" $file
  then
    echo $file
  fi
done
