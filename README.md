# Python File Integrity Monitor

A small defensive Python utility that stores SHA-256 hashes for files in a watched directory and detects added, removed, or modified files.

## Quick start

```powershell
mkdir watched
Set-Content watched/example.txt 'Original content'
python monitor.py init
python monitor.py check
Set-Content watched/example.txt 'Modified content'
python monitor.py check
```

The last command reports `CHANGED: example.txt` and exits with code 1. Run `python monitor.py init` again to accept a new trusted baseline.

## Security considerations

- SHA-256 detects changes relative to the stored baseline; it does **not** establish who changed a file.
- Store baseline.json in a separately protected location for real-world use; an attacker who can alter both the files and baseline can evade detection.
- This is a local educational monitoring utility, not a real-time endpoint protection system.
- The monitor excludes its own baseline if the baseline is within the watched directory and skips `.git` directories.
