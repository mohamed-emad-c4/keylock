# <div align="center">🔒 KeyLock 🔒</div>

<div align="center">
  
  ![GitHub stars](https://img.shields.io/github/stars/zemax/keylock?style=for-the-badge&color=ffd700)
  ![GitHub forks](https://img.shields.io/github/forks/zemax/keylock?style=for-the-badge&color=0088ff) 
  ![License](https://img.shields.io/badge/LICENSE-MIT-brightgreen?style=for-the-badge)
  ![Status](https://img.shields.io/badge/STATUS-ACTIVE-success?style=for-the-badge)
  
  <h3>🔐 Lock your keyboard and mouse with elegance and precision 🔐</h3>
  
  <p><i>This is a public fork of <a href="https://github.com/Axorax/keylock">Axorax/keylock</a></i></p>
  
</div>

<p align="center">
    <img src="./assets/icon.png" width="120" height="120"/>
</p>

## 🌟 Features

- 🖥️ **Modern UI** - Clean, responsive design with light and dark themes
- ⌨️ **Keyboard Lock** - Prevent keyboard inputs with a single click
- 🖱️ **Mouse Lock** - Disable mouse movements and clicks instantly 
- ⏱️ **Scheduled Locking** - Set up automated locking schedules
- 🔄 **Quick Countdown** - Lock devices after a specific time period
- 🔑 **Custom Shortcuts** - Set your own unlock key combinations
- 🔔 **Status Indicators** - Clear visual feedback about locked/unlocked state

## 🖼️ Preview

<p align="center">
    <img src="./thumbnail.png" width="80%" />
</p>

## 🚀 Quick Start

1. **Download** the latest release from the [releases page](https://github.com/zemax/keylock/releases)
2. **Extract** the files to a location of your choice
3. **Run** the `keylock.exe` executable
4. **Lock** your keyboard, mouse or both using the intuitive interface
5. **Unlock** using the configured shortcut (default: `ctrl+q`)

## ⚙️ Configuration

KeyLock can be customized through the `keylock.config` file in the same directory as the executable:

```
&theme@!@light                  # UI theme (light or dark)
&unlock@!@ctrl+q                # Shortcut to unlock (Examples: ctrl+q, alt+s, shift+ctrl+q)
&onstart_lock_keyboard@!@false  # Lock keyboard on start (true or false)
&onstart_lock_mouse@!@false     # Lock mouse on start (true or false)
&refresh_rate@!@1500            # Check for lock every x milliseconds
&quit_after@!@never             # Exit app after some time (never or milliseconds: 1000, 5000)
```

## 📅 Scheduler

The scheduler feature allows you to:

- 🔁 Create **recurring schedules** (daily, weekdays, weekends)
- 🗓️ Set up **one-time schedules** for specific dates
- ⏲️ Use **countdown timers** for quick temporary locks
- ⏱️ Set **automatic unlock durations**

## 🛠️ Technical Details

KeyLock is built with:
- **Python** for core functionality
- **Tkinter** for the user interface
- **Threading** for background operations
- **JSON** for configuration storage

## 💡 Tips and Tricks

- 🔄 Use **Ctrl+Q** (default) to unlock your devices
- 🌙 Toggle between **light and dark themes** in the settings
- ⏱️ Set up a **countdown timer** for quick temporary locks
- 📋 Create **scheduled tasks** for regular locking patterns

## ⚠️ Known Issues

> [!Important]
> When locking only the mouse, if the exit shortcut includes "ctrl", you can only use a-z characters. This is not an issue when locking only the keyboard or both devices.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

<div align="center">
  <p>
    ⭐ Star this repository if you find it useful! ⭐
  </p>
  <p>
    <i>Originally created by <a href="https://github.com/axorax">Axorax</a> and forked for additional enhancements</i>
  </p>
  <p>
    <a href="https://github.com/zemax/keylock">GitHub</a> •
    <a href="https://github.com/zemax/keylock/issues">Report Bug</a> •
    <a href="https://github.com/zemax/keylock/issues">Request Feature</a>
  </p>
</div>
