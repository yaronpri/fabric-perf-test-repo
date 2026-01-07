#!/usr/bin/env python3
"""
Generate multiple ipynb files from a simple template for Fabric import.

Usage:
  python3 scripts/generate_notebooks.py --count 300

This script writes files into `generated_notebooks/` next to this script.
"""
import os
import json
import base64
from argparse import ArgumentParser
from copy import deepcopy


TEMPLATE = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {"language": "markdown"},
            "source": [
                "# Notebook",
                "This notebook was generated for import into Microsoft Fabric."
            ]
        },
        {
            "cell_type": "code",
            "metadata": {"language": "python"},
            "execution_count": None,
            "outputs": [],
            "source": [
                "# Sample cell",
                "print(\"Hello from generated notebook\")"
            ]
        }
    ],
    "metadata": {"language_info": {"name": "python"}}
}


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def generate_notebook(path, index):
    name = f"notebook_{index:03d}.ipynb"
    out = os.path.join(path, name)
    data = deepcopy(TEMPLATE)
    # Ensure we have fresh copies of cells
    data["cells"] = deepcopy(TEMPLATE["cells"])
    # Add a small unique marker to the first markdown cell
    data["cells"][0]["source"] = [
        "# Notebook",
        f"Generated notebook #{index} for Fabric import."
    ]
    # Ensure top-level nbformat fields exist
    data.setdefault("nbformat", 4)
    data.setdefault("nbformat_minor", 5)
    data.setdefault("metadata", {"language_info": {"name": "python"}})

    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return out


def main():
    p = ArgumentParser()
    p.add_argument("--count", type=int, default=300)
    p.add_argument("--outdir", type=str, default="generated_notebooks")
    args = p.parse_args()

    repo_root = os.path.dirname(os.path.dirname(__file__))
    outdir = os.path.join(repo_root, args.outdir)
    ensure_dir(outdir)

    created = []
    for i in range(1, args.count + 1):
        path = generate_notebook(outdir, i)
        created.append(path)

    # Also create a zip for easy upload
    zip_path = os.path.join(repo_root, f"{args.outdir}.zip")
    try:
        import zipfile
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for fpath in created:
                zf.write(fpath, arcname=os.path.basename(fpath))
    except Exception:
        zip_path = None

    print(f"Created {len(created)} notebooks in: {outdir}")
    if zip_path:
        print(f"Zip created: {zip_path}")


if __name__ == "__main__":
    main()
