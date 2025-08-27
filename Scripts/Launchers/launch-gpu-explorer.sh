#!/bin/bash
# Launch GPU-Accelerated Backup Explorer

echo "🚀 Starting RTX 4070 Accelerated Backup Explorer..."

# Set GPU environment variables
export CUDA_VISIBLE_DEVICES=0
export QT_QPA_PLATFORM=xcb
export QT_QUICK_BACKEND=rhi
export QSG_RHI_BACKEND=vulkan
export QTWEBENGINE_CHROMIUM_FLAGS="--enable-gpu-rasterization --enable-zero-copy"

# Check GPU status
echo "🔍 Checking RTX 4070 status..."
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader 2>/dev/null || echo "⚠️ nvidia-smi not available"

# Set display
export DISPLAY=:0

echo "🎮 GPU Environment configured"
echo "📂 Working directory: $(pwd)"

# Launch application
cd /home/herb
python3 GPUBackupExplorer.py

echo "Application finished."