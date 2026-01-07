#!/usr/bin/env python3
"""
Rewrite all item JSON files in `generated_items/` to a fixed template and set displayName to a counter.

Usage:
  python3 scripts/update_items_with_template.py --src generated_items --backup
"""
import os
import json
import base64
from argparse import ArgumentParser
from pathlib import Path

TEMPLATE_PARTS = [
    {
        "path": "notebook-content.py",
        "payload": "ewogICJuYmZvcm1hdCI6IDQsCiAgIm5iZm9ybWF0X21pbm9yIjogNSwKICAiY2VsbHMiOiBbCiAgICB7CiAgICAgICJjZWxsX3R5cGUiOiAibWFya2Rvd24iLAogICAgICAibWV0YWRhdGEiOiB7CiAgICAgICAgImxhbmd1YWdlIjogIm1hcmtkb3duIgogICAgICB9LAogICAgICAic291cmNlIjogWwogICAgICAgICIjIE5vdGVib29rIiwKICAgICAgICAiR2VuZXJhdGVkIG5vdGVib29rICMxIGZvciBGYWJyaWMgaW1wb3J0LiIKICAgICAgXQogICAgfSwKICAgIHsKICAgICAgImNlbGxfdHlwZSI6ICJjb2RlIiwKICAgICAgIm1ldGFkYXRhIjogewogICAgICAgICJsYW5ndWFnZSI6ICJweXRob24iCiAgICAgIH0sCiAgICAgICJleGVjdXRpb25fY291bnQiOiBudWxsLAogICAgICAib3V0cHV0cyI6IFtdLAogICAgICAic291cmNlIjogWwogICAgICAgICIjIFNhbXBsZSBjZWxsIiwKICAgICAgICAicHJpbnQoXCJIZWxsbyBmcm9tIGdlbmVyYXRlZCBub3RlYm9va1wiKSIKICAgICAgXQogICAgfQogIF0sCiAgIm1ldGFkYXRhIjogewogICAgImxhbmd1YWdlX2luZm8iOiB7CiAgICAgICJuYW1lIjogInB5dGhvbiIKICAgIH0KICB9Cn0=",
        "payloadType": "InlineBase64"
    },
    {
        "path": ".platform",
        "payload": "eyJrZXJuZWxfaW5mbyI6eyJuYW1lIjoic3luYXBzZV9weXNwYXJrIn0sImRlcGVuZGVuY2llcyI6e30sImRpc3BsYXlOYW1lIjoiR2VuZXJhdGVkIE5vdGVib29rIDEiLCJtZXRhZGF0YSI6eyJsYW5ndWFnZSI6InB5dGhvbiIsImxhbmd1YWdlX2dyb3VwIjoic3luYXBzZV9weXNwYXJrIn19",
        "payloadType": "InlineBase64"
    }
]


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def update_all(src_dir, backup=True):
    src = Path(src_dir)
    if backup:
        import shutil
        backup_dir = src_dir + "_bak"
        if os.path.exists(backup_dir):
            shutil.rmtree(backup_dir)
        shutil.copytree(src_dir, backup_dir)
        print("Backup created:", backup_dir)

    files = sorted(src.glob("item_*.json"))
    for i, fp in enumerate(files, start=1):
        obj = {
            "displayName": f"Notebook {i}",
            "description": "A notebook description",
            "type": "Notebook",
            "parts": TEMPLATE_PARTS
        }
        with open(fp, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=2)

    # create zip of updated files
    try:
        import zipfile
        zip_path = os.path.join(src_dir, "updated_items.zip")
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for fp in files:
                zf.write(fp, arcname=os.path.basename(fp))
        print("Created zip:", zip_path)
    except Exception as e:
        print("Failed to create zip:", e)


def main():
    p = ArgumentParser()
    p.add_argument("--src", default="generated_items")
    p.add_argument("--no-backup", dest="backup", action="store_false")
    args = p.parse_args()
    update_all(args.src, backup=args.backup)


if __name__ == "__main__":
    main()
