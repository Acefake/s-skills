#!/usr/bin/env python3
"""Bump plugin versions after skill files change.

Plugin hosts keep the installed copy until the version string
in plugin.json changes. Run this after editing a plugin, then commit the
manifest, README/docs version lines and plugin-versions.lock.json updates together.

    python3 scripts/bump_plugin_version.py s-atlas
    python3 scripts/bump_plugin_version.py --all

The script adds 1 to the last number: 1.0.0 becomes 1.0.1. To publish
1.1.0 or 2.0.0, edit the version in the lock file and in all registered manifests
for that plugin, then run scripts/check_marketplace.py.
"""

from __future__ import annotations

import argparse
import sys

from marketplace_lib import (
    LOCK_PATH,
    PLUGIN_ORDER,
    bump_patch,
    content_hash,
    load_lock,
    manifest_paths,
    set_doc_versions,
    set_manifest_version,
    write_json,
)


def bump_one(lock: dict, name: str) -> str:
    if name not in PLUGIN_ORDER:
        raise SystemExit(f"unknown plugin {name!r}. Known: {', '.join(PLUGIN_ORDER)}")
    entry = lock["plugins"][name]
    current = entry["version"]
    actual = content_hash(name)
    if entry.get("contentSha256") == actual:
        return f"{name}: content matches {current}, no bump"
    version = bump_patch(current)
    for path in manifest_paths(name):
        set_manifest_version(path, version)
    set_doc_versions(name, version)
    entry["version"] = version
    entry["contentSha256"] = actual
    return f"{name}: {current} -> {version}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Bump plugin versions after content changes")
    parser.add_argument("plugin", nargs="?", help="plugin id, for example s-atlas")
    parser.add_argument("--all", action="store_true", help="bump every plugin whose files changed")
    args = parser.parse_args()
    if args.all == bool(args.plugin):
        parser.error("pass one plugin id, or pass --all")
    lock = load_lock()
    names = list(PLUGIN_ORDER) if args.all else [args.plugin]
    messages = [bump_one(lock, name) for name in names]
    write_json(LOCK_PATH, lock)
    print("\n".join(messages))
    return 0


if __name__ == "__main__":
    sys.exit(main())
