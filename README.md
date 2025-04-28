# <div align="center">🔒 KeyLock 🔒</div>

<div align="center">
  
  ![GitHub stars](https://img.shields.io/github/stars/Axorax/keylock?style=for-the-badge&color=ffd700)
  ![GitHub forks](https://img.shields.io/github/forks/Axorax/keylock?style=for-the-badge&color=0088ff)
  ![License](https://img.shields.io/badge/LICENSE-AGPL--3.0-brightgreen?style=for-the-badge)
  ![Status](https://img.shields.io/badge/STATUS-ACTIVE-success?style=for-the-badge)
  
  <h3>🔐 Lock your keyboard and mouse with elegance and precision 🔐</h3>
  
  <p><i>This project is based on and compatible with <a href="https://github.com/Axorax/keylock">Axorax/keylock</a></i></p>
  
</div>

<p align="center">
    <img src="./assets/icon.png" width="120" alt="KeyLock Icon"/>
</p>

---

## 🌟 Features

- 🖥️ **Modern UI**: Clean, responsive design with light and dark themes
- ⌨️ **Keyboard Lock**: Prevent keyboard inputs with a single click
- 🖱️ **Mouse Lock**: Disable mouse movements and clicks instantly
- ⏱️ **Scheduled Locking**: Set up automated locking schedules
- 🔄 **Quick Countdown**: Lock devices after a specific time period
- 🔔 **Status Indicators**: Clear visual feedback about locked/unlocked state

---

## 🖼️ Preview

<p align="center">
    <img src="./preview.png" width="45%" alt="KeyLock Dashboard Screenshot"/>
</p>

---

## 🚀 Quick Start

1. **Download** the latest release from the [releases page](https://github.com/Axorax/keylock/releases)
2. **Extract** the files to a location of your choice
3. **Run** the `keylock.exe` executable
4. **Lock** your keyboard, mouse, or both using the intuitive interface
5. **Unlock** using the configured shortcut (default: `ctrl+q`)

---

## ⚙️ Configuration

KeyLock can be customized through the `keylock.config` file in the same directory as the executable:

```ini
&theme@!@light                  # UI theme (light or dark)
&unlock@!@ctrl+q                # Shortcut to unlock (Examples: ctrl+q, alt+s, shift+ctrl+q)
&onstart_lock_keyboard@!@false  # Lock keyboard on start (true or false)
&onstart_lock_mouse@!@false     # Lock mouse on start (true or false)
&refresh_rate@!@1500            # Check for lock every x milliseconds
&quit_after@!@never             # Exit app after some time (never or milliseconds: 1000, 5000)
```

---

## 📅 Scheduler

- 🗓️ **One-time schedules** for specific dates
- ⏲️ **Countdown timers** for quick temporary locks
- ⏱️ **Automatic unlock durations**

---

## 🛠️ Technical Details

- **Python** for core functionality
- **Tkinter** for the user interface
- **Threading** for background operations
- **JSON** for configuration storage

---

## 💡 Tips and Tricks

- 🌙 Toggle between **light and dark themes** in the settings
- ⏱️ Set up a **countdown timer** for quick temporary locks

---

## ⚠️ Known Issues

> When locking only the mouse, if the exit shortcut includes "ctrl", you can only use a-z characters. This is not an issue when locking only the keyboard or both devices.

---

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request. For major changes, open an issue first to discuss what you would like to change.

---

## 📄 License

This project is licensed under the AGPL-3.0 License 

---

## 🙏 Acknowledgements

- Inspired by the original [Axorax/keylock](https://github.com/Axorax/keylock) project.
- Thanks to all contributors and users!

---

**For more information, support, or to report bugs, visit the [main repository](https://github.com/Axorax/keylock).**

<div align="center">
  <p>
    ⭐ Star this repository if you find it useful! ⭐
  </p>
  <p>
    <i>Originally created by <a href="https://github.com/axorax">Axorax</a> and enhanced by the community.</i>
  </p>
  <p>
    <a href="https://github.com/Axorax/keylock">Main GitHub</a> •
    <a href="https://github.com/Axorax/keylock/issues">Report Bug</a> •
    <a href="https://github.com/Axorax/keylock/issues">Request Feature</a>
  </p>
</div>
