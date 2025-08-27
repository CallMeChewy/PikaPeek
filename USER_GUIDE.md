# 🐭 PikaPeek User Guide

**The Ultimate Borg Backup Explorer with GPU Acceleration**

PikaPeek is a powerful, user-friendly application for exploring and recovering files from Borg backup repositories. With GPU acceleration and a beautiful dark mode interface, it makes backup recovery fast and easy on your eyes.

## 🚀 Quick Start

### 1. Choose Your Explorer

PikaPeek offers three main applications optimized for different needs:

#### 🌙 **Dark GPU Explorer** (Recommended)

- **Best for:** Daily use, RTX 4070 users, eye comfort
- **Features:** Dark theme, GPU acceleration, real-time monitoring
- **Launch:** Double-click `PikaPeek-DarkGPU.desktop` or run `./Scripts/Launchers/launch-dark-gpu-explorer.sh`

#### 🚀 **GPU Explorer**

- **Best for:** High-performance backup browsing
- **Features:** Light theme, GPU acceleration, performance monitoring
- **Launch:** Double-click `PikaPeek-GPU.desktop` or run `./Scripts/Launchers/launch-gpu-explorer.sh`

#### 🐭 **Standard Explorer**

- **Best for:** Basic backup browsing, older hardware
- **Features:** Simple interface, reliable performance
- **Launch:** Double-click `PikaPeek.desktop` or run `./Scripts/Launchers/run-backup-explorer.sh`

### 2. First Time Setup

1. **Install Dependencies:**
   
   ```bash
   pip install PySide6
   ```

2. **Verify Borg Installation:**
   
   ```bash
   borg --version
   ```

3. **Check GPU (for GPU versions):**
   
   ```bash
   nvidia-smi
   ```

## 📖 How to Use PikaPeek

### Step 1: Launch the Application

Choose your preferred explorer and launch it using the desktop icons or command line.

### Step 2: Select a Backup Date

1. Click the dropdown menu labeled "📅 Select Backup"
2. Choose from available backup archives (most recent first)
3. Click "🌙 Mount Archive" (Dark mode) or "🔗 Mount Archive" (other versions)

### Step 3: Browse Your Files

- **Left Panel:** Quick navigation to common folders (Desktop, Documents, etc.)
- **Right Panel:** File browser with detailed information
- **Double-click folders** to navigate deeper
- **Single-click files** to select them

### Step 4: Recover Files

1. **Select a file** in the right panel
2. Choose your recovery option:
   - **🌙 Quick Copy** - Copy to temporary preview folder
   - **💾 Permanent Copy** - Copy to permanent recovery folder
   - **👁️ Preview File** - View file information

### Step 5: Access Recovered Files

- Click **🌙 Temp Folder** to open temporary copies
- Click **🌙 Recovery Folder** to open permanent copies
- Files are automatically organized and renamed to avoid conflicts

## 🎨 Interface Guide

### 🌙 Dark GPU Explorer Features

**Header Bar:**

- **RTX 4070 Dark Mode** indicator shows GPU status
- **Archive selector** for choosing backup dates
- **Mount/Unmount** controls for archive access

**Status Information:**

- Real-time GPU memory usage and temperature
- Current archive and path information  
- File operation progress and status

**File Actions:**

- **Preview** - Quick file information popup
- **Quick Copy** - Fast temporary file recovery
- **Permanent Copy** - Save files to recovery folder
- **Folder Access** - Open recovery folders in file manager

### Performance Monitoring (GPU Versions)

- **VRAM Usage:** Monitor graphics memory consumption
- **GPU Temperature:** Real-time thermal monitoring
- **Archive Status:** Current mounted backup information

## 🛠️ Advanced Features

### Custom Mount Points

Each explorer uses its own mount point to avoid conflicts:

- Dark GPU: `/home/herb/dark-gpu-backup-mount`
- GPU: `/home/herb/gpu-backup-mount`  
- Standard: `/home/herb/simple-pika-mount`

### File Recovery Locations

- **Temporary:** `/home/herb/Desktop/TempPreview`
- **Permanent:** `/home/herb/Desktop/RecoveredFiles`

### GPU Optimization (RTX 4070)

- **Vulkan Backend:** Hardware-accelerated rendering
- **High DPI Support:** Optimized for 4K displays
- **Zero-Copy Operations:** Reduced memory overhead

## 🔧 Troubleshooting

### Common Issues

**"Repository Error" Message:**

- Verify your backup repository path exists
- Check that Borg can access the repository
- Ensure you have read permissions

**GPU Not Detected:**

- Install NVIDIA drivers: `sudo apt install nvidia-driver-xxx`
- Verify with: `nvidia-smi`
- GPU versions will fall back to software rendering

**Desktop Icons Not Working:**

- Make desktop files executable: `chmod +x *.desktop`
- Install from Applications menu if needed

**Mount Failures:**

- Unmount existing archives first
- Check available disk space
- Verify repository isn't corrupted

### Performance Tips

**For Best Performance:**

1. Use Dark GPU Explorer with RTX 4070
2. Close other GPU-intensive applications
3. Ensure adequate system RAM (8GB+ recommended)
4. Use SSD storage for mount points

**For Battery Life:**

1. Use Standard Explorer on laptops
2. Disable GPU acceleration if not needed
3. Close application when not in use

## 📋 System Requirements

### Minimum Requirements

- **OS:** Linux (Ubuntu 20.04+, similar distributions)
- **Python:** 3.8+
- **RAM:** 4GB
- **Storage:** 2GB free space
- **Borg:** Latest version installed

### Recommended for GPU Versions

- **GPU:** NVIDIA RTX 4070 or compatible
- **RAM:** 8GB+
- **Storage:** SSD with 10GB+ free space
- **Display:** 1080p+ resolution

## 🆘 Support

### Getting Help

1. Check this guide first
2. Review error messages carefully
3. Verify all dependencies are installed
4. Test with Standard Explorer if GPU versions fail

### Log Files

- Application logs are displayed in the status bar
- Use terminal launch for detailed debugging
- GPU information available in status bar

### Common Solutions

- **Restart the application** for persistent issues
- **Unmount and remount** archives if browsing fails
- **Check file permissions** for recovery operations
- **Free up disk space** if operations are slow

---

## 🎉 Enjoy PikaPeek!

PikaPeek makes backup recovery simple, fast, and visually appealing. Whether you're recovering a single file or exploring entire backup archives, the GPU-accelerated dark mode interface provides a premium experience that's easy on your eyes and powerful for your workflow.

**Happy backup exploring!** 🐭✨