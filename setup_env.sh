#!/usr/bin/env bash
set -euo pipefail
ENV_NAME="${1:-thesis-env}"
PYTHON_VERSION="3.11"
MINICONDA_DIR="$HOME/miniconda3"
if [ ! -d "$MINICONDA_DIR" ]; then
    echo "Installing Miniconda to $MINICONDA_DIR..."
    curl -sS -o /tmp/miniconda.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
    bash /tmp/miniconda.sh -b -p "$MINICONDA_DIR"
    rm -f /tmp/miniconda.sh
else
    echo "Miniconda already installed at $MINICONDA_DIR, skipping install"
fi
# shellcheck disable=SC1091
source "$MINICONDA_DIR/etc/profile.d/conda.sh"
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main 2>/dev/null || true
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r 2>/dev/null || true
if conda env list | grep -q "^$ENV_NAME "; then
    echo "Conda env '$ENV_NAME' already exists, reusing it"
else
    echo "Creating conda env '$ENV_NAME' with Python $PYTHON_VERSION..."
    conda create -y -n "$ENV_NAME" python="$PYTHON_VERSION"
fi
conda activate "$ENV_NAME"
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
    echo "All packages installed successfully in conda env '$ENV_NAME'"
else
    echo "Finished with failures: ${FAILED[*]}"
    exit 1
fi
echo "To use this environment later, run:"
echo "  source $MINICONDA_DIR/etc/profile.d/conda.sh && conda activate $ENV_NAME"
EOF
chmod +x setup_env.sh