# 🛠️ PikaPeek Installation Guide

**Complete setup instructions for the GPU-accelerated Borg backup explorer**

## 📋 Prerequisites

### System Requirements
- **Operating System:** Linux (Ubuntu 20.04+, Debian 11+, or similar)
- **Python:** 3.8 or higher
- **Architecture:** x86_64
- **RAM:** 4GB minimum, 8GB+ recommended for GPU versions
- **Storage:** 2GB free space, SSD recommended

### Required Software
- **Borg Backup:** Latest version
- **Python 3:** With pip package manager
- **Git:** For cloning the repository (optional)

## 🚀 Quick Installation

### Method 1: Direct Download
```bash
# Clone or download PikaPeek
git clone <repository-url> PikaPeek
cd PikaPeek

# Install Python dependencies
pip install PySide6

# Make scripts executable
chmod +x Scripts/Launchers/*.sh
chmod +x *.desktop

# Launch Dark GPU Explorer
./Scripts/Launchers/launch-dark-gpu-explorer.sh
```

### Method 2: Manual Setup
```bash
# Install dependencies
sudo apt update
sudo apt install python3 python3-pip borgbackup

# Install PySide6
pip3 install PySide6

# Download PikaPeek files to your preferred location
# Make all scripts executable
find . -name "*.sh" -exec chmod +x {} \;
```

## 🎮 GPU Setup (RTX 4070 Optimization)

### NVIDIA Driver Installation
```bash
# Check current driver
nvidia-smi

# Install latest NVIDIA drivers (if needed)
sudo apt install nvidia-driver-535  # or latest version
sudo reboot

# Verify installation
nvidia-smi --query-gpu=name,driver_version --format=csv
```

### Vulkan Support
```bash
# Install Vulkan runtime
sudo apt install vulkan-utils mesa-vulkan-drivers

# For NVIDIA cards
sudo apt install nvidia-vulkan-driver

# Test Vulkan (optional)
vulkaninfo | grep "GPU id"
```

## 📦 Borg Backup Setup

### Install Borg
```bash
# Ubuntu/Debian
sudo apt install borgbackup

# Or install latest from source
pip3 install borgbackup

# Verify installation
borg --version
```

### Repository Access
Ensure your Borg repositories are accessible:
```bash
# Test repository access
borg list /path/to/your/repository

# If using remote repositories
borg list user@server:/path/to/repository
```

## 🖥️ Desktop Integration

### Install Desktop Icons
```bash
# Copy desktop files to applications directory (optional)
cp *.desktop ~/.local/share/applications/

# Or use them directly from the PikaPeek directory
# Desktop files are already configured and executable
```

### Create Desktop Shortcuts
```bash
# Link to your desktop (optional)
ln -s /path/to/PikaPeek/PikaPeek-DarkGPU.desktop ~/Desktop/
ln -s /path/to/PikaPeek/PikaPeek-GPU.desktop ~/Desktop/
ln -s /path/to/PikaPeek/PikaPeek.desktop ~/Desktop/
```

## ⚙️ Configuration

### Default Settings
PikaPeek works out of the box with these defaults:
- **Repository Path:** `/media/herb/Linux_Drive_2/PikaBackups/From_2502-07-11`
- **Mount Points:** Automatic temporary directories
- **Recovery Folders:** `~/Desktop/RecoveredFiles` and `~/Desktop/TempPreview`

### Custom Configuration
Edit the repository path in the Python files if needed:
```python
# In Extensions/*.py files, modify this line:
self.repo_path = "/your/custom/repository/path"
```

## 🧪 Verify Installation

### Test Basic Functionality
```bash
# Test standard explorer
./Scripts/Launchers/run-backup-explorer.sh

# Test GPU explorer (if GPU available)
./Scripts/Launchers/launch-gpu-explorer.sh

# Test dark mode GPU explorer
./Scripts/Launchers/launch-dark-gpu-explorer.sh
```

### Check GPU Acceleration
```bash
# Verify GPU detection
nvidia-smi

# Check Vulkan support
vulkaninfo | head -20

# Test with GPU explorer - you should see GPU stats in the status bar
```

## 🐛 Troubleshooting Installation

### Common Issues

**Python/PySide6 Issues:**
```bash
# If pip install fails
sudo apt install python3-dev python3-pip
pip3 install --upgrade pip
pip3 install PySide6

# Alternative installation
sudo apt install python3-pyside6*
```

**Borg Not Found:**
```bash
# Check if borg is in PATH
which borg

# If not found, install from package manager
sudo apt install borgbackup

# Or add to PATH if installed elsewhere
export PATH=$PATH:/path/to/borg
```

**GPU Driver Issues:**
```bash
# Check GPU status
lspci | grep -i nvidia

# Reinstall drivers if needed
sudo apt purge nvidia-*
sudo apt install nvidia-driver-535
sudo reboot
```

**Permission Issues:**
```bash
# Fix script permissions
find . -name "*.sh" -exec chmod +x {} \;

# Fix desktop file permissions
chmod +x *.desktop

# Ensure repository access
ls -la /path/to/your/repository
```

### Dependency Issues

**Missing Qt Libraries:**
```bash
sudo apt install qt6-base-dev qt6-tools-dev
```

**Missing System Libraries:**
```bash
sudo apt install libgl1-mesa-glx libegl1-mesa libxrandr2 libxss1 \
    libxcursor1 libxcomposite1 libasound2 libxi6 libxtst6
```

## 🔧 Advanced Installation

### Virtual Environment Setup
```bash
# Create virtual environment
python3 -m venv pikapeek-env
source pikapeek-env/bin/activate

# Install dependencies
pip install PySide6

# Create launcher script
echo '#!/bin/bash' > launch-pikapeek-venv.sh
echo 'source /path/to/pikapeek-env/bin/activate' >> launch-pikapeek-venv.sh
echo 'cd /path/to/PikaPeek' >> launch-pikapeek-venv.sh
echo './Scripts/Launchers/launch-dark-gpu-explorer.sh' >> launch-pikapeek-venv.sh
chmod +x launch-pikapeek-venv.sh
```

### System-wide Installation
```bash
# Install PikaPeek system-wide (optional)
sudo cp -r PikaPeek /opt/
sudo ln -s /opt/PikaPeek/Scripts/Launchers/launch-dark-gpu-explorer.sh /usr/local/bin/pikapeek-dark
sudo ln -s /opt/PikaPeek/Scripts/Launchers/launch-gpu-explorer.sh /usr/local/bin/pikapeek-gpu
sudo ln -s /opt/PikaPeek/Scripts/Launchers/run-backup-explorer.sh /usr/local/bin/pikapeek

# Now you can run from anywhere
pikapeek-dark
```

## ✅ Installation Complete!

After successful installation, you should be able to:

1. **Launch PikaPeek** using desktop icons or command line
2. **Browse backup archives** with GPU acceleration (if available)
3. **Recover files** with the dark mode interface
4. **Monitor GPU performance** in real-time

### Next Steps:
- Read the [USER_GUIDE.md](USER_GUIDE.md) for usage instructions
- Configure your backup repository paths
- Test file recovery with some sample files

**Enjoy your enhanced backup exploration experience!** 🎉