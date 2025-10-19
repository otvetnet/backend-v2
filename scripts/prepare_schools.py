#!/usr/bin/env python3
"""Prepare schools_prepaired.csv by removing duplicate school ids from schools_processed.csv.

Creates `app/data/schools_prepaired.csv` next to the original file. Keeps the first
occurrence of each id. Uses utf-8-sig to handle BOM and semicolon delimiter.
"""
from pathlib import Path
import csv
from datetime import datetime


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    src = repo_root / 'app' / 'data' / 'schools_processed.csv'
    dst = repo_root / 'app' / 'data' / 'schools_prepaired.csv'

    if not src.exists():
        print(f"Source CSV not found: {src}")
        return 1

    print(f"Reading from: {src}")
    seen = set()
    kept = 0
    skipped = 0

    with src.open('r', encoding='utf-8-sig', newline='') as f_in:
        reader = csv.DictReader(f_in, delimiter=';', skipinitialspace=True)
        fieldnames = reader.fieldnames or []

        with dst.open('w', encoding='utf-8', newline='') as f_out:
            writer = csv.DictWriter(f_out, fieldnames=fieldnames, delimiter=';')
            if fieldnames:
                writer.writeheader()

            for row in reader:
                # Normalize id value as string
                id_raw = ''
                if fieldnames:
                    # prefer 'id' key if present
                    if 'id' in row:
                        id_raw = (row.get('id') or '').strip()
                    else:
                        # fallback to first column
                        first_key = fieldnames[0]
                        id_raw = (row.get(first_key) or '').strip()
                else:
                    # no header: try taking first item
                    vals = list(row.values())
                    id_raw = vals[0].strip() if vals else ''

                if id_raw == '':
                    # no id -> keep the row
                    writer.writerow(row)
                    kept += 1
                    continue

                if id_raw in seen:
                    skipped += 1
                    continue

                seen.add(id_raw)
                writer.writerow(row)
                kept += 1

    print(f"Wrote: {dst}")
    print(f"Kept: {kept}, Skipped duplicates: {skipped}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
