# Practical Python Automation

A collection of practical, useful, real-world Python automation scripts.

This repository starts with a **File Organizer with Watch Mode**, a flexible script that automatically sorts files in a folder (e.g., Downloads) into categorized subfolders based on their extensions. It works on macOS, Linux, and Windows.

The script includes:

- 🗂 Automatic file organization by extension  
- 👀 Real-time watch mode using `watchdog`  
- ↩ Undo mode with CSV logs  
- 🧪 Dry-run mode (simulate without moving files)  
- 🗺 Customizable mapping with JSON  
- 🔥 Python 3.7+ compatible  

---

## 📦 Features

### ✔ Organize files automatically
Moves files into folders like `Images/`, `Docs/`, `Video/`, `Others/` etc.

### ✔ Watch Mode
Runs continuously and organizes files as they arrive.

### ✔ Undo support
All moves are logged in a CSV so you can revert actions later.

### ✔ Dry-run
Preview what would change before actually moving any files.

---

## 🚀 Usage

### One-time organization
```bash
python3 organizer.py --src "$HOME/Downloads" --log-file moves.csv --verbose
