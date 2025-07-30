#!/bin/bash

set -e

echo "[INIT] Installing PyTorch3D..."
pip uninstall -y pytorch3d
FORCE_CUDA=1 pip install --no-cache-dir "git+https://github.com/facebookresearch/pytorch3d.git@stable"
echo "[INIT] Starting Triton Inference Server..."
tritonserver --model-repository=/models
