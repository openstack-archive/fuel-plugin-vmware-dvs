#!/bin/bash

date "+%d-%m-%y  %H:%M:%S  INFO: Following groups should be run: $SHAKER_SCENARIOS"

# Type should be one of them: cross_az, single-zone
type=$1
start_time=$(date "+%H:%M:%S_%d-%m-%y")
log_folder=log/$type/$start_time
reports_folder=reports/$type/$start_time
output_folder=output/$type/$start_time

mkdir -p $log_folder
mkdir -p $reports_folder
mkdir -p $output_folder

for group in ${SHAKER_SCENARIOS[*]}
do

scenario=$type/$group
name=$(echo $group | sed 's/.yaml//')
date "+TIME: %d/%m/%y  %H:%M:%S  INFO: Start group: $group"
shaker --debug -v --scenario $scenario --report $reports_folder/$name.html --output $output_folder/$name.json --flavor-name m1.medium > $log_folder/$name.log

if [ $? != 0 ]; then
date "+%d-%m-%y  %H:%M:%S  ERROR: Something went wrong in group $group"
fi

date "+%d-%m-%y  %H:%M:%S  INFO: Group was ended: $group"
date "+%d-%m-%y  %H:%M:%S  INFO: You can find log in  $(pwd)/$log_folder/$name.log"
sleep 10
done