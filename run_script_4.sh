#!/bin/bash

SCRIPT1="dissertation_workplace_script.py"
SCRIPT2="dissertation_workplace_script_1LargeLayer.py"
SCRIPT3="dissertation_workplace_script_double_sized_layers.py"
SCRIPT4="dissertation_workplace_script_sampleEfficiency.py"


RUN_NAME1="testRun_onlyCommercials_GPU"
RUN_NAME2="testRun_onlyResidential_GPU"
RUN_NAME3="testRun_onlyIndustrial_GPU"
RUN_NAME4="testRun_onlyBuildingTypes_GPU"
RUN_NAME5="testRun_onlyConjunctions_GPU"
RUN_NAME6="testRun_onlyEquivalences_GPU"


RUN_NAME7="testRun_baselineStratified_GPU"
RUN_NAME8="testRun_1LargeLayer_GPU"
RUN_NAME9="testRun_onlyBuildingTypesContinuiation_GPU"

RUN_NAME10="testRun_8000Samples"
RUN_NAME11="testRun_4000Samples"
RUN_NAME12="testRun_2000Samples"

ONTOLOGY1="COMMERCIAL_ONLY"
ONTOLOGY2="RESIDENTIAL_ONLY"
ONTOLOGY3="INDUSTRIAL_ONLY"
ONTOLOGY4="BUILDING_TYPES_ONLY"
ONTOLOGY5="CONJUNCTIONS_ONLY"
ONTOLOGY6="EQUIVALENCES_ONLY"



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
    ./venv/bin/python "$SCRIPT3" "$RUN_NAME9" "$ONTOLOGY4"
    exit_code=$?
done

exit_code=1

exit_code=1

while [ $exit_code -ne 0 ] && [ $exit_code -ne 130 ]; do

    echo "RETRIES = "$((++RETRIES))""
    ./venv/bin/python "$SCRIPT4" "$RUN_NAME10" "$ONTOLOGY4" "$SUBSET_SIZE1"
    exit_code=$?
done


exit_code=1

while [ $exit_code -ne 0 ] && [ $exit_code -ne 130 ]; do

    echo "RETRIES = "$((++RETRIES))""
    ./venv/bin/python "$SCRIPT4" "$RUN_NAME11" "$ONTOLOGY4" "$SUBSET_SIZE2"
    exit_code=$?
done

exit_code=1

while [ $exit_code -ne 0 ] && [ $exit_code -ne 130 ]; do

    echo "RETRIES = "$((++RETRIES))""
    ./venv/bin/python "$SCRIPT4" "$RUN_NAME12" "$ONTOLOGY4" "$SUBSET_SIZE3"
    exit_code=$?
done

echo "Done with $RETRIES"
