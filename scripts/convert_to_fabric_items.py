#!/usr/bin/env python3
"""
Convert ipynb files into Microsoft Fabric REST API item definition JSON files.

Usage:
  python3 scripts/convert_to_fabric_items.py --src generated_notebooks --out generated_items

Each output file will be named `item_notebook_###.json` and contain a JSON structure
with `format: ipynb` and `parts` including `artifact.content.ipynb` with `InlineBase64` payload.
"""
import os
import json
import base64
from argparse import ArgumentParser
from pathlib import Path
from copy import deepcopy


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def encode_file_to_base64(path):
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode("ascii")


def make_item(json_b64, platform_b64=None):
    parts = [
        {
            "path": "artifact.content.ipynb",
            "payload": json_b64,
            "payloadType": "InlineBase64"
        }
    ]
    if platform_b64:
        parts.append({
            "path": ".platform",
            "payload": platform_b64,
            "payloadType": "InlineBase64"
        })

    return {"format": "ipynb", "parts": parts}


def convert_all(src_dir, out_dir):
    ensure_dir(out_dir)
    src = Path(src_dir)
    created = []
    for fp in sorted(src.glob("*.ipynb")):
        b64 = encode_file_to_base64(fp)
        # Create a platform metadata payload per item
        idx = fp.stem.split("_")[-1]
        platform_obj = {
            "kernel_info": {"name": "synapse_pyspark"},
            "dependencies": {},
            "displayName": f"Generated Notebook {int(idx)}",
            "metadata": {"language": "python", "language_group": "synapse_pyspark"}
        }
        platform_json = json.dumps(platform_obj, separators=(",", ":"))
        platform_b64 = base64.b64encode(platform_json.encode("utf-8")).decode("ascii")
        item = make_item(b64, platform_b64)
        idx = fp.stem.split("_")[-1]
        out_name = f"item_{fp.stem}.json"
        out_path = os.path.join(out_dir, out_name)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(item, f, indent=2)
        created.append(out_path)

    # zip them for convenience
    zip_path = os.path.join(os.path.dirname(out_dir), os.path.basename(out_dir) + ".zip")
    try:
        import zipfile
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for p in created:
                zf.write(p, arcname=os.path.basename(p))
    except Exception:
        zip_path = None

    return created, zip_path


def main():
    p = ArgumentParser()
    p.add_argument("--src", default="generated_notebooks")
    p.add_argument("--out", default="generated_items")
    args = p.parse_args()

    created, zip_path = convert_all(args.src, args.out)
    print(f"Created {len(created)} item JSON files in: {args.out}")
    if zip_path:
        print(f"Zip created: {zip_path}")


if __name__ == "__main__":
    main()
