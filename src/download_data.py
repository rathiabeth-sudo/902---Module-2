"""Download the two public datasets used by Module 2 into data/raw (pinned versions, checksums recorded).

Usage:  python -m src.download_data
"""
from __future__ import annotations

import hashlib
import urllib.request

from .utils import load_config, p, save_json


def sha256(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch(url: str, dest) -> None:
    if dest.exists() and dest.stat().st_size > 0:
        print(f"  exists: {dest.name}")
        return
    print(f"  downloading {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "antenna-surrogate-research"})
    with urllib.request.urlopen(req) as r, open(dest, "wb") as f:
        while chunk := r.read(1 << 20):
            f.write(chunk)


def main() -> None:
    cfg = load_config()
    raw = cfg["paths"]["raw"]
    record = {}

    c = cfg["datasets"]["patch"]
    url = f"https://huggingface.co/datasets/{c['repo_id']}/resolve/{c['revision']}/{c['file']}"
    dest = p(raw, "patch", "train.parquet")
    fetch(url, dest)
    record["patch"] = {"url": url, "sha256": sha256(dest), "licence": "MIT"}

    c = cfg["datasets"]["mendeley"]
    dest = p(raw, "mendeley", "Antenna_Parameters.xlsx")
    fetch(c["file_url"], dest)
    digest = sha256(dest)
    if digest != c["sha256"]:
        raise RuntimeError(f"Mendeley checksum mismatch: {digest}")
    record["mendeley"] = {"url": c["file_url"], "sha256": digest, "licence": "CC-BY-4.0"}

    save_json(record, p(raw, "download_record.json"))
    print("done")


if __name__ == "__main__":
    main()
