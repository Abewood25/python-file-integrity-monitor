"""Small file-integrity monitor for a local directory."""
import argparse
import hashlib
import json
from pathlib import Path


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def snapshot(directory, baseline):
    root = directory.resolve()
    baseline = baseline.resolve()
    result = {}
    for path in sorted(root.rglob('*')):
        if path.is_file() and path.resolve() != baseline and '.git' not in path.relative_to(root).parts:
            result[path.relative_to(root).as_posix()] = digest(path)
    return result


def main():
    parser = argparse.ArgumentParser(description='SHA-256 file integrity monitor')
    parser.add_argument('command', choices=['init', 'check'])
    parser.add_argument('--directory', type=Path, default=Path('watched'))
    parser.add_argument('--baseline', type=Path, default=Path('baseline.json'))
    args = parser.parse_args()
    if not args.directory.is_dir():
        parser.error(f'Directory not found: {args.directory}')
    current = snapshot(args.directory, args.baseline)
    if args.command == 'init':
        args.baseline.write_text(json.dumps(current, indent=2) + '\n', encoding='utf-8')
        print(f'Baseline saved for {len(current)} files to {args.baseline}')
        return 0
    if not args.baseline.is_file():
        parser.error('Baseline missing; run init first')
    original = json.loads(args.baseline.read_text(encoding='utf-8'))
    added = sorted(current.keys() - original.keys())
    removed = sorted(original.keys() - current.keys())
    changed = sorted(k for k in current.keys() & original.keys() if current[k] != original[k])
    for label, paths in [('ADDED', added), ('REMOVED', removed), ('CHANGED', changed)]:
        for path in paths:
            print(f'{label}: {path}')
    if not (added or removed or changed):
        print('PASS: No file changes detected')
        return 0
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
