#!/bin/bash
# Runs archmax_generate.py in small batches to work around Blender's memory leak.
# Resumable: keeps a checkpoint file so Ctrl+C + rerun picks up where it left off.
# Edit TOTAL and BATCH_SIZE as needed.

TOTAL=20000
BATCH_SIZE=${1:-5}
OUTPUT_DIR="results/full_run"
SCRIPT="archmax_generate.py"
CHECKPOINT="$OUTPUT_DIR/checkpoint.txt"
MAX_RETRIES=3

mkdir -p "$OUTPUT_DIR/images"

if [ -f "$CHECKPOINT" ]; then
    count=$(cat "$CHECKPOINT")
    echo "Resuming from checkpoint: $count / $TOTAL already done"
else
    count=0
fi

echo " batch size: $1"
while [ "$count" -lt "$TOTAL" ]; do
    remaining=$((TOTAL - count))
    batch=$((remaining < BATCH_SIZE ? remaining : BATCH_SIZE))

    echo "==> Rendering batch: images $count to $((count + batch - 1))"

    attempt=0
    until blender -b --python "$SCRIPT" -- -n "$batch" --output_dir /tmp/blender_batch; do
        attempt=$((attempt + 1))
        echo "    WARNING: batch at $count failed (exit $?), attempt $attempt/$MAX_RETRIES"
        rm -rf /tmp/blender_batch
        if [ "$attempt" -ge "$MAX_RETRIES" ]; then
            echo "    FATAL: batch at $count failed $MAX_RETRIES times. Re-run this script to resume from $count."
            exit 1
        fi
    done

    # Move images into the final folder with correct offset names
    for f in /tmp/blender_batch/*/images/*.jpg; do
        [ -f "$f" ] || continue
        fname=$(basename "$f" .jpg)
        mv "$f" "$OUTPUT_DIR/images/$((fname + count)).jpg"
    done

    # Append labels CSV — use only the final labels.csv, not checkpoint files
    labels_file=$(find /tmp/blender_batch -name "labels.csv" | head -1)
    if [ -z "$labels_file" ]; then
        echo "    FATAL: no labels.csv produced for batch at $count. Re-run this script to resume from $count."
        rm -rf /tmp/blender_batch
        exit 1
    fi

    if [ "$count" -eq 0 ] && [ ! -f "$OUTPUT_DIR/labels.csv" ]; then
        cp "$labels_file" "$OUTPUT_DIR/labels.csv"
    else
        # offset the id and row index by count
        tail -n +2 "$labels_file" | awk -F',' -v offset="$count" 'BEGIN{OFS=","} {$1=$1+offset; $2=$2+offset; print}' >> "$OUTPUT_DIR/labels.csv"
    fi

    rm -rf /tmp/blender_batch
    count=$((count + batch))

    # Write checkpoint atomically (temp file + rename) so a Ctrl+C here can't
    # leave a half-written checkpoint file behind
    echo "$count" > "$CHECKPOINT.tmp" && mv "$CHECKPOINT.tmp" "$CHECKPOINT"

    echo "    Done. Total so far: $count / $TOTAL"
done

echo "All $TOTAL images saved to $OUTPUT_DIR"