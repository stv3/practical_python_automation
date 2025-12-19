Largest Files Scanner — Practical Python Automation

A practical, real-world Python automation script that scans any directory and identifies the largest files, making it easy to locate space-consuming data on your system.

This tool is fully interactive, cross-platform, dependency-free, and includes a smooth progress bar to visualize scan progress.
Works on macOS, Linux, and Windows.

The script includes:
📁 Recursive directory scanning
📊 Real-time progress bar
📐 Human-readable file sizes (KB, MB, GB, TB)
🔢 Customizable “Top N” results
🧪 Graceful handling of permission errors
🐍 Python 3.7+ compatible


📦 Features
✔ Scan directories recursively
Searches through the chosen directory—including all subfolders—to locate every file.

✔ Interactive mode
User is prompted for:
The directory to scan
Number of largest files to display
No arguments or setup required.

✔ Real-time progress bar
Provides visual feedback from 0% → 100% while scanning files.

✔ Human-readable sizes
Converts raw bytes into human-friendly units:
B → KB → MB → GB → TB

✔ Error-safe
Skips files that cannot be accessed due to permission issues, locks, or broken symlinks.

🚀 Usage
Run the interactive scanner
python3 largest_files.py

Example interaction
Enter a directory path (e.g. /home/stv3/Downloads): /home/stv3/Downloads

Counting files...
Found 3245 files. Scanning...

[██████████████--------------------------] 44.21%

How many top files do you want to see? (e.g. 20): 20

Top 20 largest files under: /home/stv3/Downloads

 1.45 GB | /home/stv3/Downloads/ubuntu.iso
920.12 MB | /home/stv3/Downloads/game.zip
512.33 MB | /home/stv3/Downloads/video.mp4
...

