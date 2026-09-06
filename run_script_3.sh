#!/bin/bash

SCRIPT="$1"
RUN_NAME1="testRun_8000Samples"
RUN_NAME2="testRun_4000Samples"
RUN_NAME3="testRun_2000Samples"
LIMIT=10

SUBSET_SIZE1=8000
SUBSET_SIZE2=4000
SUBSET_SIZE3=2000

exit_code=1
RETRIES=-1

# ./venv/bin/python "$SCRIPT" "$RUN_NAME"
# exit_code=$?

while [ $exit_code -ne 0 ] && [ $exit_code -ne 130 ]; do

    echo "RETRIES = "$((++RETRIES))""
    ./venv/bin/python "$SCRIPT" "$RUN_NAME1" "$SUBSET_SIZE1"
    exit_code=$?
done



exit_code=1

while [ $exit_code -ne 0 ] && [ $exit_code -ne 130 ]; do

    echo "RETRIES = "$((++RETRIES))""
    ./venv/bin/python "$SCRIPT" "$RUN_NAME2" "$SUBSET_SIZE2"
    exit_code=$?
done


exit_code=1

while [ $exit_code -ne 0 ] && [ $exit_code -ne 130 ]; do

    echo "RETRIES = "$((++RETRIES))""
    ./venv/bin/python "$SCRIPT" "$RUN_NAME3" "$SUBSET_SIZE3"
    exit_code=$?
done

echo "Done with $RETRIES"




