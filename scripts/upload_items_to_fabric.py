#!/usr/bin/env python3
"""
Upload generated Fabric item JSON files to a Microsoft Fabric workspace via REST API.

Usage:
  python3 scripts/upload_items_to_fabric.py --endpoint https://<fabric-endpoint>/items/create \
      --token <token> --src generated_items --concurrency 4 --retries 3 --dry-run

Notes:
- This script requires a valid Fabric REST endpoint and an auth token with item create permissions.
- Use `--dry-run` to only enumerate files and show what would be posted.
"""
import os
import json
import time
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import requests


def post_item(session, endpoint, token, filepath, timeout=30):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    with open(filepath, "rb") as f:
        data = f.read()
    resp = session.post(endpoint, headers=headers, data=data, timeout=timeout)
    return resp.status_code, resp.text


def worker(session, endpoint, token, filepath, retries):
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            status, text = post_item(session, endpoint, token, filepath)
            return True, status, text
        except Exception as e:
            last_exc = e
            time.sleep(1 * attempt)
    return False, None, str(last_exc)

def chunked(iterable, size):
    for i in range(0, len(iterable), size):
        yield iterable[i:i + size]


def main():
    p = ArgumentParser()
    p.add_argument("--endpoint", required=True)
    p.add_argument("--token", required=False)
    p.add_argument("--src", default="generated_items")
    p.add_argument("--concurrency", type=int, default=4)
    p.add_argument("--retries", type=int, default=3)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--batch-size", type=int, default=50, help="Number of items per batch before sleeping")
    p.add_argument("--sleep-after", type=int, default=45, help="Seconds to sleep after each batch")
    args = p.parse_args()

    src = Path(args.src)
    files = sorted(src.glob("*.json"))
    if not files:
        print("No JSON files found in", args.src)
        return

    if args.dry_run:
        print(f"Dry-run: {len(files)} files found. Showing first 10:")
        for f in files[:10]:
            print(" -", f.name)
        print(f"Batch size: {args.batch_size}, sleep after each batch: {args.sleep_after}s")
        return

    if not args.token:
        print("Error: --token is required for actual upload")
        return

    session = requests.Session()
    results = []

    total_files = len(files)
    batch_num = 0
    for batch in chunked(files, args.batch_size):
        batch_num += 1
        print(f"Starting batch {batch_num}: {len(batch)} items (files {files.index(batch[0])+1}..{files.index(batch[-1])+1} of {total_files})")
        with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
            futures = {ex.submit(worker, session, args.endpoint, args.token, str(fp), args.retries): fp for fp in batch}
            for fut in as_completed(futures):
                fp = futures[fut]
                try:
                    success, status, text = fut.result()
                except Exception as e:
                    print(fp.name, "error", e)
                    results.append((fp.name, False, None, str(e)))
                    continue
                results.append((fp.name, success, status, text[:200]))
                print(fp.name, "->", "OK" if success else "FAILED", status)

        # If there are more files remaining, sleep
        processed = sum(1 for r in results)
        remaining = total_files - processed
        if remaining > 0:
            print(f"Batch {batch_num} complete. Sleeping {args.sleep_after} seconds before next batch... ({remaining} items remaining)")
            time.sleep(args.sleep_after)

    # Summary
    ok = sum(1 for r in results if r[1])
    total = len(results)
    print(f"Uploaded {ok}/{total} items")


if __name__ == "__main__":
    main()
