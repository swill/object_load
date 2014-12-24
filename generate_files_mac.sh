#!/bin/bash

# make root directory
mkdir "uploads"

# small directory
mkdir "uploads/small"

# medium directory
mkdir "uploads/medium"

# large directory
mkdir "uploads/large"

# generate files
for i in {1..20}
do
  # small
  mkfile $(($i*50))"k" "uploads/small/$(($i*50)).txt"
  
  # medium
  mkfile $(($i*5))"m" "uploads/medium/$(($i*5)).txt"
done

for i in {1..5}
do
  # large
  mkfile $(($i*200))"m" "uploads/large/$(($i*200)).txt"
done
