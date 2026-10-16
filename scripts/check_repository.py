#!/usr/bin/env python3
"""Offline verification of AIGirls manifests, local files, license records and Markdown links."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {"deepseek", "gpt", "claude", "glm", "gemini", "doubao", "grok", "qwen", "kimi", "minimax"}
FAILS: list[str] = []


def check(condition: bool, message: str) -> None:
    if not condition:
        FAILS.append(message)


def load_json(name: str) -> dict:
    try:
        return json.loads((ROOT / name).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        FAILS.append(f"{name}: {exc}")
        return {}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def scan_local_links() -> int:
    regex = re.compile(r"(?<!!)\[[^\]\n]+\]\(([^)\s]+)(?:\s+[^)]*)?\)")
    count = 0
    paths = [ROOT / "README.md", ROOT / "LICENSE_SCOPE.md", ROOT / "ARTWORK_LICENSES.md",
             ROOT / "THIRD_PARTY_NOTICES.md", *sorted((ROOT / "docs").glob("*.md")),
             *sorted((ROOT / "characters").glob("**/*.md"))]
    for doc in paths:
        if not doc.is_file():
            check(False, f"missing markdown file {doc.relative_to(ROOT)}")
            continue
        text = doc.read_text(encoding="utf-8")
        for match in regex.finditer(text):
            target = match.group(1)
            if target.startswith(("#", "/", "mailto:", "data:")) or "://" in target:
                continue
            local = unquote(target.split("#", 1)[0].split("?", 1)[0])
            if not local:
                continue
            count += 1
            check((doc.parent / local).exists(),
                  f"broken local link in {doc.relative_to(ROOT)}: {target}")
    return count


def main() -> int:
    personas = load_json("data/characters.json").get("characters", [])
    verification = load_json("data/artwork-verification.json").get("files", [])
    rights = load_json("data/artwork-licensing.json").get("records", [])
    mappings = load_json("data/portrait-sources.json").get("files", [])

    def unique_ids(rows: list[dict], key: str, label: str) -> dict[str, dict]:
        result: dict[str, dict] = {}
        for row in rows:
            name = row.get(key)
            check(isinstance(name, str) and name not in result, f"{label} duplicate or missing ID: {name}")
            if isinstance(name, str):
                result[name] = row
        check(set(result) == EXPECTED, f"{label} IDs differ: {set(result) ^ EXPECTED}")
        return result

    ps = unique_ids(personas, "id", "personas")
    pv = unique_ids(verification, "character", "verified art")
    pr = unique_ids(rights, "id", "license ledger")
    pm = unique_ids(mappings, "character", "source mappings")

    for id in sorted(EXPECTED):
        folder = ROOT / "characters" / id
        for name in ("README.md", "VISUAL.md", "SOURCE.md", "logo.svg"):
            check((folder / name).is_file(), f"{id}: missing {name}")
        svg = folder / "logo.svg"
        if svg.is_file():
            svg_text = svg.read_text(encoding="utf-8")
            check("<svg" in svg_text and "</svg>" in svg_text, f"{id}: invalid SVG wrapper")
        persona, ver, licence, mapping = (table.get(id, {}) for table in (ps, pv, pr, pm))
        portrait = persona.get("portrait_path")
        if not isinstance(portrait, str):
            check(False, f"{id}: missing portrait_path")
            continue
        check(portrait == ver.get("destination") == licence.get("portrait") == mapping.get("destination"),
              f"{id}: portrait path mismatch")
        check(persona.get("visual_design_path") == f"characters/{id}/VISUAL.md",
              f"{id}: visual_design_path mismatch")
        check(persona.get("logo_reference_path") == f"characters/{id}/logo.svg",
              f"{id}: logo_reference_path mismatch")
        image = ROOT / portrait
        if not image.is_file():
            check(False, f"{id}: missing original portrait at {portrait}")
            continue
        check(image.stat().st_size == ver.get("bytes"), f"{id}: image file size differs")
        digest = sha256(image)
        check(digest == ver.get("sha256") == persona.get("original_portrait_sha256") == licence.get("sha256"),
              f"{id}: SHA256 mismatch")
        check(image.stat().st_size > 80_000, f"{id}: suspiciously small image")
        first = image.open("rb").read(8)
        check((first.startswith(b"\x89PNG\r\n\x1a\n") if image.suffix.lower() == ".png"
               else first[:3] == b"\xff\xd8\xff"), f"{id}: unexpected image header")
        check(licence.get("license_status") not in ("", None), f"{id}: unknown license status")
        check(licence.get("permission_for_commercial_use") == "not_established",
              f"{id}: commercial use must not be incorrectly declared cleared")

    for p in ("LICENSE", "LICENSE_SCOPE.md", "ARTWORK_LICENSES.md",
              "THIRD_PARTY_NOTICES.md", "data/artwork-licensing.json"):
        check((ROOT / p).is_file(), f"missing rights document {p}")
    count = scan_local_links()
    print(f"Characters: {len(ps)}, portraits: {len(pv)}, rights: {len(pr)}, links checked: {count}")
    if FAILS:
        for msg in FAILS:
            print("ERROR:", msg)
        return 1
    print("AIGirls repository validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
