#!/usr/bin/env python3
"""Clean duplicate cities in app/data/cities_processed.csv by id.

Creates a backup file with a .bak timestamp and rewrites the CSV keeping the
first occurrence of each id.
"""
from pathlib import Path
import csv
from datetime import datetime


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    csv_path = repo_root / 'app' / 'data' / 'cities_processed.csv'
    if not csv_path.exists():
        print(f"CSV file not found: {csv_path}")
        return 1

    backup_path = csv_path.with_suffix('.csv.' + datetime.utcnow().strftime('%Y%m%d%H%M%S') + '.bak')
    csv_path.replace(backup_path)
    print(f"Created backup: {backup_path}")

    seen_ids = set()
    kept = 0
    skipped = 0

    with backup_path.open('r', encoding='utf-8-sig', newline='') as src, csv_path.open('w', encoding='utf-8', newline='') as dst:
        reader = csv.reader(src, delimiter=';')
        writer = csv.writer(dst, delimiter=';')

        try:
            header = next(reader)
        except StopIteration:
            print('Empty CSV, nothing to do')
            return 0

        # write header back
        writer.writerow(header)

        for row in reader:
            if not row:
                continue
            # assume first column is id
            id_raw = row[0].strip() if len(row) > 0 else ''
            if id_raw == '':
                # keep rows without id (no dedupe)
                writer.writerow(row)
                kept += 1
                continue
            if id_raw in seen_ids:
                skipped += 1
                continue
            seen_ids.add(id_raw)
            writer.writerow(row)
            kept += 1

    print(f"Finished cleaning. Kept: {kept}, Skipped duplicates: {skipped}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
