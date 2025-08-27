#!/bin/bash
# File: launch-dark-gpu-explorer.sh
# Path: /home/herb/Desktop/PikaPeek/Scripts/Launchers/launch-dark-gpu-explorer.sh
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-29
# Last Modified: 2025-07-29 07:32AM

echo "🌙 Starting Dark GPU-Accelerated Backup Explorer..."

# Set GPU environment variables for RTX 4070
export CUDA_VISIBLE_DEVICES=0
export QT_QPA_PLATFORM=xcb
export QT_QUICK_BACKEND=rhi
export QSG_RHI_BACKEND=vulkan
export QTWEBENGINE_CHROMIUM_FLAGS="--enable-gpu-rasterization --enable-zero-copy"

# Check RTX 4070 status
echo "🔍 Checking RTX 4070 status..."
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader 2>/dev/null || echo "⚠️ nvidia-smi not available"

# Set display
export DISPLAY=:0

echo "🌙 Dark GPU Environment configured"
echo "📂 Working directory: $(pwd)"

# Launch dark mode application
cd /home/herb/Desktop/PikaPeek/Extensions
echo "🌙 Launching Dark GPU Backup Explorer..."
python3 DarkGPUBackupExplorer.py

echo "🌙 Dark mode application finished."