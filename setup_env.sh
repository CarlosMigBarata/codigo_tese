#!/usr/bin/env bash
set -euo pipefail

ENV_DIR="${1:-venv}"

echo "Creating virtual environment at: $ENV_DIR"
python3 -m venv "$ENV_DIR"

# shellcheck disable=SC1091
source "$ENV_DIR/bin/activate"

pip install --upgrade pip

PACKAGES=(
    numpy
    pandas
    matplotlib
    torch
    torchvision
    torchmetrics
    LTNtorch
)

FAILED=()

for pkg in "${PACKAGES[@]}"; do
    echo "Installing $pkg..."
    if ! pip install "$pkg"; then
        echo "FAILED to install $pkg"
        FAILED+=("$pkg")
    fi
done

echo
if [ ${#FAILED[@]} -eq 0 ]; then
    echo "All packages installed successfully in $ENV_DIR"
else
    echo "Finished with failures: ${FAILED[*]}"
    exit 1
fi

echo "To use this environment later, run:"
echo "  source $ENV_DIR/bin/activate"
