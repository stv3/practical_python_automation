
# 📂 **Largest Files Scanner**  
### *A Practical Python Automation Tool to Find the Biggest Space Hogs on Your System*

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.7+-blue?logo=python" />
  <img src="https://img.shields.io/badge/Platform-macOS%20%7C%20Linux%20%7C%20Windows-green" />
  <img src="https://img.shields.io/badge/License-MIT-purple" />
</p>

## 📝 **Overview**
The **Largest Files Scanner** is a lightweight, interactive Python automation script that scans any directory and displays the **largest N files** found, sorted from biggest to smallest. It helps you quickly identify what's consuming disk space — whether in your Downloads folder, home directory, or large external drives.

It includes:
- 📁 Recursive scanning  
- 📊 Real-time progress bar  
- 🔢 Configurable "Top N" results  
- 📐 Human-readable file sizes  
- ⚙️ No external dependencies  
- 🖥 Works on macOS, Linux, and Windows  

## ✨ **Features**
### ✔ Recursive directory scanning  
Searches every file within the provided folder (and subfolders).

### ✔ Interactive prompts  
The script asks you:
- Which directory to scan  
- How many largest files to display  

### ✔ Real-time progress bar  
A clean terminal progress bar updates from **0% → 100%**.

### ✔ Human-readable sizes  
Outputs file sizes in:


### ✔ Error-safe scanning  
Skips unreadable or inaccessible files automatically.

## 🚀 **Usage**
### Run the script
```bash
python3 largest_files.py


Enter a directory path (e.g. /home/stv3/Downloads): /home/stv3/Downloads

Counting files...
Found 3245 files. Scanning...

[██████████████--------------------------] 43.87%

How many top files do you want to see? (e.g. 20): 20

Top 20 largest files under: /home/stv3/Downloads

 1.45 GB | /home/stv3/Downloads/ubuntu.iso
920.12 MB | /home/stv3/Downloads/game.zip
512.33 MB | /home/stv3/Downloads/video.mp4
...
