#!/bin/bash

INVALIDOPTS_ERR=100
NOTYPENAME=101
NOSCENARIOS=102

ShowHelp() {
cat << EOF
Run shaker scenarios

-t (name)    - Types name of suite to run scenarios. It can be cross_az or single_zone
              Uses TYPE if not set.
-s (list)    - Names of shaker scenarios separated by space
              Uses SHAKER_SCENARIOS if not set. See file name in folders cross_az and single_zone.
              Names can be specified as <name>.yaml ar <name>
-i (name)    - Shaker image name which is using in Openstack to run Shaker
-n           - No debug
-h           - Show this message

EOF
}

function log_info {
    message=$1
    date "+%d/%m/%y  %H:%M:%S  INFO: $message"
}

function log_error {
    message=$1
    date "+%d-%m-%y  %H:%M:%S  ERROR: $message"
}

GetoptsVariables() {
  while getopts ":t:s:i:nh" opt; do
    case ${opt} in
      t)
        TYPE="${OPTARG}"
        ;;
      s)
        SHAKER_SCENARIOS="${OPTARG}"
        ;;
      i)
        SHAKER_IMAGE="${OPTARG}"
        ;;
      n)
        NODEBUG="--nodebug"
        ;;
      h)
        ShowHelp
        exit 0
        ;;
      \?)
        echo "Invalid option: -$OPTARG"
        ShowHelp
        exit ${INVALIDOPTS_ERR}
        ;;
      :)
        echo "Option -$OPTARG requires an argument."
        ShowHelp
        exit ${INVALIDOPTS_ERR}
        ;;
    esac
  done
}

CheckVariables() {

  if [ -z "${SHAKER_SCENARIOS}" ]; then
    echo "Error! SHAKER_SCENARIOS is not set!"
    exit ${NOSCENARIOS}
  fi

  if [ -z "${TYPE}" ]; then
    echo "Error! TYPE is not set!"
    exit ${NOTYPENAME}
  fi

  if [ -n "${SHAKER_IMAGE}" ]; then
    SHAKER_IMAGE="--image-name $SHAKER_IMAGE"
  fi

}

MakeDir() {

start_time=$(date "+%H:%M:%S_%d-%m-%y")
reports_folder=reports/${TYPE}/${start_time}
output_folder=output/${TYPE}/${start_time}

mkdir -p ${reports_folder}
mkdir -p ${output_folder}

}


RunTests() {

log_info "Following groups should be run: $SHAKER_SCENARIOS"

for group in ${SHAKER_SCENARIOS}
do

name=$(echo ${group} | sed 's/.yaml//')
log_info "Start group: $group"
scenario=${TYPE}/${group}

SHAKER="shaker ${NODEBUG} --scenario ${scenario} --report ${reports_folder}/${name}.html --output ${output_folder}/${name}.json ${SHAKER_IMAGE}"
log_info "Command to run: ${SHAKER}"

${SHAKER}
if [ $? != 0 ]; then
log_error "Something went wrong in group $group"
fi

sleep 5
done

}

# first we want to get variable from command line options
GetoptsVariables "${@}"

# check do we have all critical variables set
CheckVariables

# make reports and outputs directories
MakeDir

RunTests
