#!/bin/bash

# 🧭 CONFIG SECTION
REPO_PATH="/media/herb/Linux_Drive_2/Pika Backups/backup-herb-Ubuntu-24.10-2TB-herb-2024-12-23"
FLATPAK_ID="org.gnome.World.PikaBackup"

# 🧪 1. Confirm the repo path exists
if [ ! -d "$REPO_PATH" ]; then
    echo "❌ ERROR: Repo path not found: $REPO_PATH"
    exit 1
fi

export BORG_REPO="$REPO_PATH"

# 🔐 2. Retrieve passphrase from GNOME keyring
export BORG_PASSCOMMAND="secret-tool lookup borg repo"
PASSPHRASE=$(secret-tool lookup borg repo)

if [ -z "$PASSPHRASE" ]; then
    echo "❌ ERROR: No passphrase found in keyring for key 'borg repo'"
    echo "💡 Run: secret-tool store --label='Borg Repo Key' borg repo"
    exit 2
fi

# ✅ 3. Test repo accessibility
echo "🔍 Verifying Borg repository access..."
if ! borg list "$BORG_REPO" > /dev/null 2>&1; then
    echo "❌ ERROR: Borg cannot access the repository. Check your passphrase or repo path."
    exit 3
fi
echo "✅ Repo is accessible."

# 🚀 4. Launch Pika Backup via Flatpak
echo "🧠 Launching Pika..."
flatpak run "$FLATPAK_ID"
