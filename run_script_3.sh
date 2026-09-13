#!/bin/bash

SCRIPT1="../dissertation_workplace_script.py"
SCRIPT2="../dissertation_workplace_script_1LargeLayer.py"
SCRIPT3="../dissertation_workplace_script_double_sized_layers.py"
RUN_NAME1="testRun_NoPredicates_Sept_new"
RUN_NAME2="testRun_NoPredicates_1LargeLayer_Sept_new"
RUN_NAME3="testRun_NoPredicates_Sept_double_sized_layers"
ONTOLOGY="CLASSIC_ONTOLOGY"
LIMIT=100

SUBSET_SIZE1=8000
SUBSET_SIZE2=4000
SUBSET_SIZE3=2000

exit_code=1
RETRIES=-1

# ./venv/bin/python "$SCRIPT" "$RUN_NAME"



exit_code=1

while [ $exit_code -ne 0 ] && [ $exit_code -ne 130 ]; do

    echo "RETRIES = "$((++RETRIES))""
    ./venv/bin/python "$SCRIPT3" "$RUN_NAME3" "$ONTOLOGY"
    exit_code=$?
done

exit_code=$?

while [ $exit_code -ne 0 ] && [ $exit_code -ne 130 ]; do

    echo "RETRIES = "$((++RETRIES))""
    ./venv/bin/python "$SCRIPT1" "$RUN_NAME1" "$ONTOLOGY"
    exit_code=$?
done

exit_code=1

while [ $exit_code -ne 0 ] && [ $exit_code -ne 130 ]; do

    echo "RETRIES = "$((++RETRIES))""
    ./venv/bin/python "$SCRIPT2" "$RUN_NAME2" "$ONTOLOGY"
    exit_code=$?
done


echo "Done with $RETRIES"




