#!/usr/bin/env python3
"""Download unchanged original images and validate the complete ten-character set."""
import hashlib
import json
import time
import urllib.request
from pathlib import Path
from io import BytesIO
from PIL import Image

root = Path(__file__).resolve().parent.parent
items = json.loads((root / "data/portrait-sources.json").read_text("utf-8"))["files"]
assert len(items) == 10
staged = []
verification = []
for item in items:
    target = root / item["destination"]
    binary = target.read_bytes() if target.exists() else None
    if binary is None:
        errors = []
        for host in ("i0.hdslb.com", "i1.hdslb.com", "i2.hdslb.com"):
            for attempt in range(2):
                try:
                    url = item["original_url"].replace("i0.hdslb.com", host)
                    request = urllib.request.Request(url, headers={
                        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/125.0",
                        "Referer": "https://www.bilibili.com/",
                        "Accept": "image/*",
                    })
                    with urllib.request.urlopen(request, timeout=25) as r:
                        binary = r.read(25 * 1024 * 1024 + 1)
                    if len(binary) > 25 * 1024 * 1024:
                        raise ValueError("Image larger than 25 MiB")
                    break
                except Exception as exc:
                    errors.append(str(exc))
                    time.sleep(attempt + 1)
            if binary is not None:
                break
        if binary is None:
            raise RuntimeError(f"{item['character']} failed: {errors[-4:]}")
    if len(binary) < 81920:
        raise ValueError(f"Image too small for original: {item['character']}")
    with Image.open(BytesIO(binary)) as im:
        im.verify()
    with Image.open(BytesIO(binary)) as im:
        width, height, fmt = im.width, im.height, im.format
    expected = "PNG" if target.suffix.lower() == ".png" else "JPEG"
    if min(width, height) < 700 or fmt != expected:
        raise ValueError(f"Not full-size expected source: {item['character']} {fmt} {width}x{height}")
    staged.append((target, binary))
    verification.append({
        "character": item["character"],
        "destination": item["destination"],
        "source_url": item["original_url"],
        "opus_id": item["opus_id"],
        "picture_position": item["position"],
        "format": fmt, "width": width, "height": height,
        "bytes": len(binary),
        "sha256": hashlib.sha256(binary).hexdigest(),
        "unaltered_bytes": True
    })
# No partial image dump: write only after all ten pass.
for path, binary in staged:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(binary)
(root / "data/artwork-verification.json").write_text(
    json.dumps({"status":"validated", "count":len(verification), "files":verification},
               indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
)
print(f"Validated {len(verification)} original images.")
