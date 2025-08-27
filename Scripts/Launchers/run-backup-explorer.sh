#!/bin/bash
# Launch Backup Explorer with proper environment

echo "🐭 Starting Simple Pika Backup Explorer..."
echo "Display: $DISPLAY"
echo "Working directory: $(pwd)"

# Set environment
export QT_QPA_PLATFORM=xcb
export DISPLAY=:0

# Check if GUI is available
if ! command -v nautilus &> /dev/null; then
    echo "Warning: GUI file manager not found"
fi

# Run the application
echo "Launching application..."
python3 /home/herb/Desktop/PikaPeek/Extensions/SimplePikaExplorer.py

echo "Application finished."