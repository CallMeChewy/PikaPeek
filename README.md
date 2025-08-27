# 🐭 PikaPeek - GPU-Accelerated Borg Backup Explorer

**The ultimate backup recovery experience with dark mode and RTX 4070 optimization**

PikaPeek is a powerful, beautiful, and user-friendly application for exploring and recovering files from Borg backup repositories. Featuring GPU acceleration, a stunning dark mode interface, and real-time performance monitoring, it transforms backup recovery from a chore into a pleasant experience.

## ✨ Features

### 🌙 **Dark Mode GPU Explorer** (Flagship)
- **GitHub-inspired dark theme** that's easy on your eyes
- **RTX 4070 optimized** with Vulkan backend rendering
- **Real-time GPU monitoring** - VRAM usage and temperature
- **Enhanced performance** for large backup repositories
- **Professional interface** with moon-themed icons

### 🚀 **Multi-Explorer Options**
- **Dark GPU Explorer** - Premium dark mode experience
- **GPU Explorer** - High-performance light theme
- **Standard Explorer** - Reliable backup browsing
- **Web Browsers** - Alternative web-based interfaces

### 💼 **Professional File Recovery**
- **Two-panel interface** - Navigate and browse seamlessly
- **Quick copy** to temporary preview folder
- **Permanent recovery** to organized folders
- **File preview** with detailed information
- **Automatic conflict resolution** - smart file naming

### ⚡ **Advanced Performance**
- **GPU acceleration** with Vulkan backend
- **Threaded operations** - UI never freezes
- **Smart caching** for faster browsing
- **Memory optimization** for large archives
- **Real-time monitoring** of system resources

## 🖼️ Screenshots

*The dark mode interface provides a premium backup recovery experience optimized for extended use.*

## 🚀 Quick Start

### Launch Your Preferred Explorer

**🌙 Dark Mode (Recommended):**
```bash
./Scripts/Launchers/launch-dark-gpu-explorer.sh
```

**🚀 GPU Accelerated:**
```bash
./Scripts/Launchers/launch-gpu-explorer.sh
```

**🐭 Standard:**
```bash
./Scripts/Launchers/run-backup-explorer.sh
```

### Desktop Integration
Double-click any of these desktop files:
- `PikaPeek-DarkGPU.desktop` - Dark mode GPU explorer
- `PikaPeek-GPU.desktop` - Standard GPU explorer  
- `PikaPeek.desktop` - Basic backup explorer

## 📖 Documentation

- **[Installation Guide](INSTALLATION.md)** - Complete setup instructions
- **[User Guide](USER_GUIDE.md)** - How to use PikaPeek effectively
- **[Development Guide](CLAUDE.md)** - For developers and contributors

## 🎯 Use Cases

### **Daily File Recovery**
- Accidentally deleted important files
- Need older versions of documents
- System corruption recovery
- Selective file restoration

### **Backup Exploration**
- Browse historical file versions
- Analyze backup contents
- Verify backup integrity
- Archive management

### **Professional Workflows**
- IT administrators managing backups
- Developers recovering code versions
- Content creators accessing archives
- System administrators

## 🛠️ Technical Specifications

### **System Requirements**
- **OS:** Linux (Ubuntu 20.04+, similar)
- **Python:** 3.8+
- **RAM:** 4GB minimum, 8GB+ for GPU versions
- **GPU:** NVIDIA RTX 4070 (recommended for GPU versions)

### **Dependencies**
- **PySide6** - Modern Qt6 GUI framework
- **Borg Backup** - Repository management
- **NVIDIA Drivers** - GPU acceleration support
- **Vulkan Runtime** - Graphics acceleration

### **Architecture**
- **Multi-threaded design** - Responsive UI
- **GPU-accelerated rendering** - Smooth performance
- **Modular structure** - Easy maintenance
- **Cross-platform compatibility** - Linux focus

## 📁 Project Structure

```
PikaPeek/
├── Extensions/          # Main explorer applications
│   ├── DarkGPUBackupExplorer.py    # Dark mode GPU version
│   ├── GPUBackupExplorer.py        # Standard GPU version
│   ├── PikaBackupExplorer.py       # Full-featured explorer
│   └── SimplePikaExplorer.py       # Basic version
├── Scripts/             # Supporting scripts
│   ├── Launchers/       # Application launchers
│   └── BackupBrowsers/  # Alternative browsers
├── Utils/               # Development utilities
├── Core/                # Business logic
├── Gui/                 # UI components
└── Config/              # Configuration management
```

## 🎨 Design Philosophy

### **User Experience First**
- **Dark mode by default** - Comfortable for extended use
- **GPU acceleration** - Smooth, responsive interface
- **Intuitive navigation** - Two-panel explorer design
- **Visual feedback** - Real-time status and progress

### **Performance Optimized**
- **Hardware acceleration** - Leverage modern GPUs
- **Memory efficient** - Handle large backup repositories
- **Threaded operations** - Never block the UI
- **Smart caching** - Faster subsequent operations

### **Professional Quality**
- **Robust error handling** - Graceful failure recovery
- **Comprehensive logging** - Detailed operation tracking
- **Modular architecture** - Easy to maintain and extend
- **Standards compliant** - AIDEV-PascalCase-2.1

## 🤝 Contributing

PikaPeek welcomes contributions! The codebase follows modern Python standards with comprehensive documentation.

### **Development Setup**
```bash
# Clone repository
git clone <repository-url>
cd PikaPeek

# Install development dependencies
pip install PySide6 pytest

# Run tests
python -m pytest tests/

# Launch development version
python Extensions/DarkGPUBackupExplorer.py
```

## 📄 License

*License information to be added*

## 🙏 Acknowledgments

- **Borg Backup Project** - Excellent backup solution
- **Qt/PySide6 Team** - Outstanding GUI framework
- **NVIDIA** - GPU acceleration technology
- **Dark Theme Inspiration** - GitHub's dark mode design

---

## 🌟 Why Choose PikaPeek?

### **Beyond Basic Backup Recovery**
PikaPeek isn't just another backup browser - it's a premium experience designed for users who demand both functionality and aesthetics. The dark mode interface reduces eye strain during extended recovery sessions, while GPU acceleration ensures smooth performance even with massive backup repositories.

### **Professional Grade**
Built with enterprise-level standards, PikaPeek handles edge cases gracefully, provides comprehensive error reporting, and maintains responsive performance under heavy loads. The modular architecture makes it easy to customize and extend.

### **Modern Technology Stack**
Leveraging the latest in GUI technology (Qt6/PySide6), graphics acceleration (Vulkan), and modern Python practices, PikaPeek represents the future of backup recovery tools.

**Transform your backup recovery experience today!** 🚀✨

---

*PikaPeek - Where backup recovery meets beautiful design* 🐭