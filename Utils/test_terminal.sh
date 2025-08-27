#!/bin/bash
# Test script to simulate opening a new terminal

echo "Testing what happens when a new terminal opens..."

# Source bashrc like a new terminal would
echo "Sourcing ~/.bashrc..."
source ~/.bashrc

echo "✅ Terminal simulation complete - no auto-launches should have occurred"