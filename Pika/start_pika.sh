#!/bin/bash

# This script attempts to start the Pika Backup daemon.
# It requires sudo privileges.

PIKA_SERVICE_NAME="pika-backup.service" # <<< VERIFY THIS SERVICE NAME IS CORRECT FOR YOUR SYSTEM

echo "Attempting to start Pika Backup service: $PIKA_SERVICE_NAME"
sudo systemctl start "$PIKA_SERVICE_NAME"

if [ $? -eq 0 ]; then
    echo "Pika Backup service started successfully."
else
    echo "Error: Failed to start Pika Backup service. Please check the service name and system logs."
fi

echo "Pika Backup daemon start attempt complete."
