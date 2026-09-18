#!/bin/bash

SCRIPT="$1"
RUN_NAME="$2"
ONTOLOGY="$3"
LIMIT=10

exit_code=1
RETRIES=-1

# ./venv/bin/python "$SCRIPT" "$RUN_NAME"
# exit_code=$?

while [ $exit_code -ne 0 ] && [ $exit_code -ne 130 ]; do

    echo "RETRIES = "$((++RETRIES))""
    ./venv/bin/python "$SCRIPT" "$RUN_NAME" "$ONTOLOGY"
    exit_code=$?
done

echo "Done with $RETRIES"




