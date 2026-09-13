#!/bin/bash

SCRIPT1="../dissertation_workplace_script.py"
SCRIPT2="../dissertation_workplace_script_1LargeLayer.py"
SCRIPT3="../dissertation_workplace_script_double_sized_layers.py"
RUN_NAME1="testRun_onlyCommercials_GPU"
RUN_NAME2="testRun_onlyResidential_GPU"
RUN_NAME3="testRun_onlyIndustrial_GPU"
ONTOLOGY1="COMMERCIAL_ONLY"
ONTOLOGY2="RESIDENTIAL_ONLY"
ONTOLOGY3="INDUSTRIAL_ONLY"
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
    ./venv/bin/python "$SCRIPT3" "$RUN_NAME1" "$ONTOLOGY1"
    exit_code=$?
done

exit_code=1

while [ $exit_code -ne 0 ] && [ $exit_code -ne 130 ]; do

    echo "RETRIES = "$((++RETRIES))""
    ./venv/bin/python "$SCRIPT3" "$RUN_NAME2" "$ONTOLOGY2"
    exit_code=$?
done

exit_code=1

while [ $exit_code -ne 0 ] && [ $exit_code -ne 130 ]; do

    echo "RETRIES = "$((++RETRIES))""
    ./venv/bin/python "$SCRIPT3" "$RUN_NAME3" "$ONTOLOGY3"
    exit_code=$?
done


echo "Done with $RETRIES"




