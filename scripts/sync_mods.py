#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

MANIFEST_PATH = Path("manifests/mods.json")
MODS_DIR = Path("mods")
STATE_DIR = MODS_DIR / ".managed"
API_BASE = "https://api.modrinth.com/v2/version"
USER_AGENT = "minecraft-server-mod-sync/1.0"


class SyncError(Exception):
    pass


def load_manifest() -> dict:
    try:
        data = json.loads(MANIFEST_PATH.read_text())
    except FileNotFoundError as exc:
        raise SyncError(f"Missing manifest: {MANIFEST_PATH}") from exc
    except json.JSONDecodeError as exc:
        raise SyncError(f"Invalid JSON in {MANIFEST_PATH}: {exc}") from exc

    if data.get("schema_version") != 1:
        raise SyncError("Unsupported manifest schema_version; expected 1")

    mods = data.get("mods")
    if not isinstance(mods, list):
        raise SyncError("Manifest field 'mods' must be a list")

    return data


def fetch_version(version_id: str) -> dict:
    request = urllib.request.Request(
        f"{API_BASE}/{version_id}",
        headers={"User-Agent": USER_AGENT},
    )
    try:
        with urllib.request.urlopen(request) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        raise SyncError(f"Modrinth lookup failed for version_id '{version_id}': HTTP {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise SyncError(f"Network error while fetching '{version_id}': {exc.reason}") from exc


def select_primary_file(version: dict) -> dict:
    files = version.get("files") or []
    if not files:
        raise SyncError(f"Version '{version.get('id', '<unknown>')}' has no downloadable files")

    for file_info in files:
        if file_info.get("primary"):
            return file_info
    return files[0]


def sha1_of(path: Path) -> str:
    digest = hashlib.sha1()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download_file(url: str, destination: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request) as response, destination.open("wb") as output:
        shutil.copyfileobj(response, output)


def sync_mod(entry: dict) -> dict:
    slug = entry.get("slug")
    version_id = entry.get("version_id")
    if not slug or not version_id:
        raise SyncError("Each manifest mod entry must include 'slug' and 'version_id'")

    version = fetch_version(version_id)
    file_info = select_primary_file(version)
    filename = file_info.get("filename")
    url = file_info.get("url")
    hashes = file_info.get("hashes") or {}
    expected_sha1 = hashes.get("sha1")
    if not filename or not url or not expected_sha1:
        raise SyncError(f"Version '{version_id}' is missing filename, url, or sha1")

    destination = MODS_DIR / filename
    with tempfile.NamedTemporaryFile(delete=False, dir=MODS_DIR) as tmp:
        temp_path = Path(tmp.name)

    try:
        download_file(url, temp_path)
        actual_sha1 = sha1_of(temp_path)
        if actual_sha1 != expected_sha1:
            raise SyncError(
                f"Checksum mismatch for {filename}: expected {expected_sha1}, got {actual_sha1}"
            )
        temp_path.replace(destination)
    finally:
        if temp_path.exists():
            temp_path.unlink()

    return {
        "slug": slug,
        "version_id": version_id,
        "filename": filename,
        "sha1": expected_sha1,
        "project_title": version.get("name", slug),
    }


def remove_stale_files(expected_files: set[str]) -> list[str]:
    removed: list[str] = []
    for path in MODS_DIR.iterdir():
        if path.name.startswith("."):
            continue
        if path.is_dir():
            continue
        if path.suffix != ".jar":
            continue
        if path.name not in expected_files:
            path.unlink()
            removed.append(path.name)
    return removed


def main() -> int:
    try:
        manifest = load_manifest()
        MODS_DIR.mkdir(exist_ok=True)
        STATE_DIR.mkdir(exist_ok=True)

        installed = []
        expected_files: set[str] = set()
        for entry in manifest["mods"]:
            mod_state = sync_mod(entry)
            installed.append(mod_state)
            expected_files.add(mod_state["filename"])

        removed = remove_stale_files(expected_files)
        state_path = STATE_DIR / "installed.json"
        state_path.write_text(json.dumps({"mods": installed}, indent=2) + "\n")

        print(f"Synced {len(installed)} mod(s) into {MODS_DIR}")
        for mod in installed:
            print(f"- {mod['filename']} ({mod['version_id']})")
        if removed:
            print("Removed stale mods:")
            for name in removed:
                print(f"- {name}")
        return 0
    except SyncError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
