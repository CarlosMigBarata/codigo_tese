#!/bin/bash
# Runs archmax_generate.py in small batches to work around Blender's memory leak.
# Edit TOTAL and BATCH_SIZE as needed.

TOTAL=20000
BATCH_SIZE=${1:-5}
OUTPUT_DIR="results/full_run"
SCRIPT="archmax_generate.py"

mkdir -p "$OUTPUT_DIR/images"

count=0
echo " batch size: $1"
while [ "$count" -lt "$TOTAL" ]; do
    remaining=$((TOTAL - count))
    batch=$((remaining < BATCH_SIZE ? remaining : BATCH_SIZE))

    echo "==> Rendering batch: images $count to $((count + batch - 1))"

    blender -b --python "$SCRIPT" -- -n "$batch" --output_dir /tmp/blender_batch

    # Move images into the final folder with correct offset names
    for f in /tmp/blender_batch/*/images/*.jpg; do
        [ -f "$f" ] || continue
        fname=$(basename "$f" .jpg)
        mv "$f" "$OUTPUT_DIR/images/$((fname + count)).jpg"
    done

    # Append labels CSV if it exists
    labels_file=$(find /tmp/blender_batch -name "*.csv" | head -1)
    if [ -n "$labels_file" ]; then
        if [ "$count" -eq 0 ]; then
            cp "$labels_file" "$OUTPUT_DIR/labels.csv"
        else
            tail -n +2 "$labels_file" >> "$OUTPUT_DIR/labels.csv"
        fi
    fi

    rm -rf /tmp/blender_batch
    count=$((count + batch))
    echo "    Done. Total so far: $count / $TOTAL"
done

echo "All $TOTAL images saved to $OUTPUT_DIR"
