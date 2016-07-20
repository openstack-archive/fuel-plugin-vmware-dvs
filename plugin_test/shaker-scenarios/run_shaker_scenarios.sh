#!/bin/bash

date "+%d-%m-%y  %H:%M:%S  INFO: Following groups should be run: $SHAKER_SCENARIOS"

# Type should be one of them: cross_az, single_zone
type=$1
start_time=$(date "+%H:%M:%S_%d-%m-%y")
reports_folder=reports/$type/$start_time
output_folder=output/$type/$start_time

mkdir -p $reports_folder
mkdir -p $output_folder

for group in ${SHAKER_SCENARIOS[*]}
do

scenario=$type/$group
name=$(echo $group | sed 's/.yaml//')
date "+TIME: %d/%m/%y  %H:%M:%S  INFO: Start group: $group"
shaker --nodebug --scenario $scenario --report $reports_folder/$name.html --output $output_folder/$name.json --image-name shaker-image-nova

if [ $? != 0 ]; then
date "+%d-%m-%y  %H:%M:%S  ERROR: Something went wrong in group $group"
fi

date "+%d-%m-%y  %H:%M:%S  INFO: Group was ended: $group"
sleep 10
done
