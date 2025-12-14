#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File Organizer with Watch Mode (Python 3.7+ compatible)
- Moves files from a source folder into category subfolders based on extension.
- Features:
  * --dry-run (simulate)
  * CSV log to enable --undo
  * Optional JSON mapping file
  * Watch mode (requires 'watchdog') for real-time organization
  * Ignores temporary/partial downloads by default (.part, .crdownload, .tmp)
"""

import argparse
import csv
import json
import sys
import shutil
import time
import threading
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Set

# Watchdog is only needed for --watch
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except Exception:
    WATCHDOG_AVAILABLE = False

DEFAULT_MAP: Dict[str, List[str]] = {
    "Images":   ["jpg","jpeg","png","gif","webp","heic","tif","tiff","svg"],
    "Docs":     ["pdf","doc","docx","xls","xlsx","ppt","pptx","csv","txt","md","rtf"],
    "Audio":    ["mp3","flac","wav","aac","m4a","ogg","aiff"],
    "Video":    ["mp4","mkv","mov","avi","webm","m4v"],
    "Archives": ["zip","rar","7z","tar","gz","bz2","xz"],
    "Code":     ["py","ipynb","js","ts","json","yml","yaml","sh","html","css","c","cpp","rs","go","java","kt"],
    "Images.RAW":["cr2","nef","arw","rw2","orf","dng"],
}
LOG_HEADERS = ["timestamp","action","src","dst"]
DEFAULT_IGNORE_EXTS: Set[str] = {".part", ".crdownload", ".tmp"}

def load_map(map_path: Optional[Path]) -> Dict[str, List[str]]:
    if not map_path:
        return DEFAULT_MAP
    with map_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    norm: Dict[str, List[str]] = {}
    for folder, exts in data.items():
        norm[folder] = sorted({str(e).lower().lstrip(".") for e in exts})
    return norm

def ext_to_folder(ext: str, mapping: Dict[str, List[str]]) -> str:
    e = ext.lower().lstrip(".")
    for folder, exts in mapping.items():
        if e in exts:
            return folder
    return "Others"

def ensure_log(path: Optional[Path]) -> None:
    if not path:
        return
    if not path.exists():
        with path.open("w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(LOG_HEADERS)

def append_log(path: Optional[Path], action: str, src: Path, dst: Path) -> None:
    if not path:
        return
    with path.open("a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([datetime.now().isoformat(timespec="seconds"), action, str(src), str(dst)])

def scan_files(src_dir: Path) -> List[Path]:
    # non-recursive by default; only top-level files
    return [p for p in src_dir.iterdir() if p.is_file()]

def unique_destination(dst: Path) -> Path:
    if not dst.exists():
        return dst
    stem, suffix = dst.stem, dst.suffix
    parent = dst.parent
    i = 1
    while True:
        cand = parent / f"{stem} ({i}){suffix}"
        if not cand.exists():
            return cand
        i += 1

def should_ignore(p: Path, ignore_exts: Set[str]) -> bool:
    return p.suffix.lower() in ignore_exts or p.name.startswith("~$")

def move_one(file_path: Path, src_dir: Path, mapping: Dict[str, List[str]],
             dry: bool, log_file: Optional[Path], verbose: bool,
             ignore_exts: Set[str]) -> bool:
    if not file_path.exists() or not file_path.is_file():
        return False
    if should_ignore(file_path, ignore_exts):
        if verbose:
            print(f"- ignoring (temp): {file_path.name}")
        return False

    folder = ext_to_folder(file_path.suffix, mapping)
    target_dir = src_dir / folder
    target_dir.mkdir(parents=True, exist_ok=True)
    dst = unique_destination(target_dir / file_path.name)

    if file_path.parent == target_dir:
        if verbose:
            print(f"= already in place: {file_path.name} -> {folder}")
        return False

    if dry:
        print(f"[DRY] move: {file_path.name}  ->  {dst}")
        return True
    else:
        try:
            shutil.move(str(file_path), str(dst))
            append_log(log_file, "move", file_path, dst)
            if verbose:
                print(f"✓ moved: {file_path.name}  ->  {dst}")
            return True
        except Exception as e:
            print(f"! failed to move {file_path}: {e}", file=sys.stderr)
            return False

def organize(src_dir: Path, mapping: Dict[str, List[str]], dry: bool,
             log_file: Optional[Path], verbose: bool, ignore_exts: Set[str]) -> int:
    moved = 0
    files = scan_files(src_dir)
    if verbose:
        print(f"Found {len(files)} files in {src_dir}")
    for f in files:
        if move_one(f, src_dir, mapping, dry, log_file, verbose, ignore_exts):
            moved += 1
    if verbose:
        print(f"Done. Files moved: {moved}")
    return moved

def undo(log_file: Path, limit: Optional[int], verbose: bool) -> int:
    if not log_file.exists():
        print("Log file not found; nothing to undo.", file=sys.stderr)
        return 0

    with log_file.open("r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    rows_to_process = [r for r in reversed(rows) if r.get("action") == "move"]

    undone = 0
    for r in rows_to_process:
        if limit is not None and undone >= limit:
            break
        src = Path(r["src"])
        dst = Path(r["dst"])
        if dst.exists():
            back_dst = unique_destination(src) if src.exists() else src
            back_dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(dst), str(back_dst))
            undone += 1
            if verbose:
                print(f"↩ undone: {dst} -> {back_dst}")
        else:
            if verbose:
                print(f"! missing moved file (skip): {dst}")

    if verbose:
        print(f"Undo complete. Reverted: {undone}")
    return undone

# ---------------- Watch Mode ----------------

class DebouncedMover(FileSystemEventHandler):
    """Batch events and move after a short idle period to avoid partial downloads."""
    def __init__(self, src_dir: Path, mapping: Dict[str, List[str]], dry: bool,
                 log_file: Optional[Path], verbose: bool, ignore_exts: Set[str],
                 debounce_sec: float = 2.0):
        self.src_dir = src_dir
        self.mapping = mapping
        self.dry = dry
        self.log_file = log_file
        self.verbose = verbose
        self.ignore_exts = ignore_exts
        self.debounce_sec = debounce_sec
        self._lock = threading.Lock()
        self._pending: Set[Path] = set()
        self._timer = None  # type: Optional[threading.Timer]

    def on_created(self, event):
        self._queue(event)

    def on_moved(self, event):
        self._queue(event)

    def on_modified(self, event):
        self._queue(event)

    def _queue(self, event):
        if event.is_directory:
            return
        p = Path(getattr(event, "dest_path", getattr(event, "src_path", "")))
        if not p:
            return
        if self.verbose:
            print(f"(event) {event.event_type}: {p.name}")
        with self._lock:
            self._pending.add(p)
            self._arm_timer()

    def _arm_timer(self):
        if self._timer:
            self._timer.cancel()
        self._timer = threading.Timer(self.debounce_sec, self._flush)
        self._timer.daemon = True
        self._timer.start()

    def _flush(self):
        with self._lock:
            batch = list(self._pending)
            self._pending.clear()
        time.sleep(0.5)
        for p in batch:
            try:
                size1 = p.stat().st_size
                time.sleep(0.4)
                size2 = p.stat().st_size
                if size1 != size2:
                    with self._lock:
                        self._pending.add(p)
                        self._arm_timer()
                    continue
            except Exception:
                pass
            move_one(p, self.src_dir, self.mapping, self.dry, self.log_file, self.verbose, self.ignore_exts)

def watch_loop(src_dir: Path, mapping: Dict[str, List[str]], dry: bool,
               log_file: Optional[Path], verbose: bool, ignore_exts: Set[str],
               recursive: bool) -> None:
    if not WATCHDOG_AVAILABLE:
        print("Watch mode requires 'watchdog'. Install with: pip install watchdog", file=sys.stderr)
        sys.exit(2)
    handler = DebouncedMover(src_dir, mapping, dry, log_file, verbose, ignore_exts)
    observer = Observer()
    observer.schedule(handler, path=str(src_dir), recursive=recursive)
    observer.start()
    try:
        if verbose:
            print(f"Watching {src_dir} (recursive={recursive}). Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        if verbose:
            print("\nStopping watcher…")
        observer.stop()
    observer.join()

# ---------------- CLI ----------------

def main() -> None:
    ap = argparse.ArgumentParser(description="Auto-organize files by extension with dry-run, undo, and watch mode.")
    ap.add_argument("--src", required=True, help="Source folder (e.g., ~/Downloads)")
    ap.add_argument("--map", help="Path to JSON mapping (folder -> [extensions])")
    ap.add_argument("--dry-run", action="store_true", help="Simulation: do not move files")
    ap.add_argument("--log-file", help="CSV log to record moves (required for --undo)")
    ap.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    ap.add_argument("--watch", action="store_true", help="Watch mode: organize new files in real-time")
    ap.add_argument("--recursive", action="store_true", help="In watch mode, also watch subfolders")
    ap.add_argument("--undo", action="store_true", help="Undo previous moves using the CSV log")
    ap.add_argument("--undo-limit", type=int, help="Max number of moves to revert")
    ap.add_argument("--ignore-ext", action="append", help="Extra extensions to ignore (e.g., --ignore-ext .download)")

    args = ap.parse_args()
    src_dir = Path(args.src).expanduser().resolve()

    if args.undo:
        if not args.log_file:
            print("--undo requires --log-file", file=sys.stderr)
            sys.exit(2)
        undo(Path(args.log_file).expanduser().resolve(), args.undo_limit, args.verbose)
        return

    if not src_dir.exists() or not src_dir.is_dir():
        print(f"Folder does not exist: {src_dir}", file=sys.stderr)
        sys.exit(2)

    mapping = load_map(Path(args.map).expanduser().resolve()) if args.map else DEFAULT_MAP
    log_path = Path(args.log_file).expanduser().resolve() if args.log_file else None
    ensure_log(log_path)

    ignore_exts: Set[str] = set(DEFAULT_IGNORE_EXTS)
    if args.ignore_ext:
        for ext in args.ignore_ext:
            if not ext.startswith("."):
                ext = "." + ext
            ignore_exts.add(ext.lower())

    if args.watch:
        watch_loop(src_dir, mapping, args.dry_run, log_path, args.verbose, ignore_exts, args.recursive)
    else:
        organize(src_dir, mapping, args.dry_run, log_path, args.verbose, ignore_exts)

if __name__ == "__main__":
    main()
