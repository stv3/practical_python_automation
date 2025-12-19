import os
import sys
import time

def human(size):
    for u in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.2f} {u}"
        size /= 1024
    return f"{size:.2f} PB"

def progress(current, total, bar_len=40):
    pct = current / total
    filled = int(bar_len * pct)
    bar = "█" * filled + "-" * (bar_len - filled)
    sys.stdout.write(f"\r[{bar}] {pct*100:6.2f}%")
    sys.stdout.flush()

def main():
    # --- User Inputs ---
    path = input("Enter a directory path (e.g. /home/stv3/Downloads): ").strip()
    if not os.path.isdir(path):
        print("❌ Invalid directory.")
        return

    try:
        top_n = int(input("How many top files do you want to see? (e.g. 20): ").strip())
    except:
        print("⚠ Invalid number, defaulting to 20")
        top_n = 20

    # --- Count number of files first (to know 100% size) ---
    print("\nCounting files...")
    total_files = 0
    for _, _, files in os.walk(path):
        total_files += len(files)

    if total_files == 0:
        print("No files found in this directory.")
        return

    print(f"Found {total_files} files. Scanning...\n")

    # --- Scan phase with progress bar ---
    files = []
    scanned = 0

    for root, _, filenames in os.walk(path):
        for name in filenames:
            scanned += 1
            progress(scanned, total_files)

            full = os.path.join(root, name)
            try:
                size = os.path.getsize(full)
                files.append((full, size))
            except:
                pass

    sys.stdout.write("\n\n")  # formatting

    # --- Sort results ---
    files.sort(key=lambda x: x[1], reverse=True)

    print(f"Top {top_n} largest files under: {path}\n")
    for fp, size in files[:top_n]:
        print(f"{human(size):>10} | {fp}")

if __name__ == "__main__":
    main()

