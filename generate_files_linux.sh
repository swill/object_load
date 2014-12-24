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
  truncate -s $(($i*50))"K" "uploads/small/$(($i*50)).txt"
  
  # medium
  truncate -s $(($i*5))"M" "uploads/medium/$(($i*5)).txt"
done

for i in {1..5}
do
  # large
  truncate -s $(($i*200))"M" "uploads/large/$(($i*200)).txt"
done
