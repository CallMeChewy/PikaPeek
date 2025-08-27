#!/bin/bash

# ========================================
# Himalaya Secure Borg+Pika Init Script
# Generated: 2025-07-11_00-28-53
# ========================================

set -e

echo "🚀 Himalaya Secure Borg+Pika Repo Setup"

# Step 1: Ask for target backup location
read -rp "📁 Full path for new Borg repo (e.g. /media/herb/BackupDrive/PikaSecureRepo): " REPO_PATH

# Validate the path
if [ -z "$REPO_PATH" ]; then
  echo "❌ Repo path is required."
  exit 1
fi

# Step 2: Ask for passphrase
read -rsp "🔐 Enter a NEW passphrase for this repo: " BORG_PASS
echo ""
read -rsp "🔐 Confirm passphrase: " BORG_PASS_CONFIRM
echo ""

if [ "$BORG_PASS" != "$BORG_PASS_CONFIRM" ]; then
  echo "❌ Passphrases do not match. Aborting."
  exit 1
fi

# Step 3: Store the passphrase in GNOME Keyring
echo -n "$BORG_PASS" | secret-tool store --label="HimalayaBorgRepo" borg repo="$REPO_PATH"

# Step 4: Set export to use secret-tool
export BORG_PASSCOMMAND="secret-tool lookup borg repo='$REPO_PATH'"

# Step 5: Create the repo with encryption (repokey-blake2)
borg init --encryption=repokey-blake2 "$REPO_PATH"

# Step 6: Verify creation
echo "✅ Verifying..."
borg info "$REPO_PATH"

# Step 7: Launch Pika
echo "🚀 Launching Pika with secured access"
flatpak run --env=BORG_PASSCOMMAND="secret-tool lookup borg repo='$REPO_PATH'" org.gnome.World.PikaBackup &

echo ""
echo "✅ Done. New Borg repo created at:"
echo "   $REPO_PATH"
echo "   Passphrase stored securely via secret-tool."
