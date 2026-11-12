#!/usr/bin/env python3
"""Safely sync the maintained Matt Pocock skill set into a Codex profile."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from datetime import datetime, timezone
from pathlib import Path
import shutil
import sys
import tempfile
from urllib.error import URLError
from urllib.request import Request, urlopen
import zipfile


REPOSITORY = "mattpocock/skills"
BRANCH = "main"
MANAGED_SKILLS = {
    "ask-matt": "skills/engineering/ask-matt",
    "code-review": "skills/engineering/code-review",
    "codebase-design": "skills/engineering/codebase-design",
    "diagnosing-bugs": "skills/engineering/diagnosing-bugs",
    "domain-modeling": "skills/engineering/domain-modeling",
    "grill-with-docs": "skills/engineering/grill-with-docs",
    "implement": "skills/engineering/implement",
    "improve-codebase-architecture": "skills/engineering/improve-codebase-architecture",
    "prototype": "skills/engineering/prototype",
    "research": "skills/engineering/research",
    "resolving-merge-conflicts": "skills/engineering/resolving-merge-conflicts",
    "setup-matt-pocock-skills": "skills/engineering/setup-matt-pocock-skills",
    "tdd": "skills/engineering/tdd",
    "to-spec": "skills/engineering/to-spec",
    "to-tickets": "skills/engineering/to-tickets",
    "triage": "skills/engineering/triage",
    "wayfinder": "skills/engineering/wayfinder",
    "grill-me": "skills/productivity/grill-me",
    "grilling": "skills/productivity/grilling",
    "handoff": "skills/productivity/handoff",
    "teach": "skills/productivity/teach",
    "writing-for-agents": "skills/productivity/writing-for-agents",
}

# Upstream renamed this managed skill. Treat the former local directory as the
# predecessor so applying the sync archives it before installing the successor.
RENAMED_SKILLS = {
    "writing-for-agents": "writing-great-skills",
}


def get_default_skills_dir() -> Path:
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()
    return codex_home / "skills"


def get_json(url: str) -> dict:
    request = Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "Codex"})
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def download_bytes(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "Codex"})
    with urlopen(request, timeout=60) as response:
        return response.read()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def manifest(directory: Path) -> dict[str, str]:
    return {
        file.relative_to(directory).as_posix(): sha256(file)
        for file in sorted(directory.rglob("*"))
        if file.is_file()
    }


def extract_snapshot(commit: str, temporary_directory: Path) -> Path:
    archive_url = f"https://github.com/{REPOSITORY}/archive/{commit}.zip"
    with zipfile.ZipFile(io.BytesIO(download_bytes(archive_url))) as archive:
        archive.extractall(temporary_directory)
    roots = [path for path in temporary_directory.iterdir() if path.is_dir()]
    if len(roots) != 1:
        raise RuntimeError("The upstream archive did not have the expected layout.")
    return roots[0]


def classify(local: Path, upstream: Path) -> str:
    if not local.exists():
        return "missing"
    if not local.is_dir() or not (local / "SKILL.md").is_file():
        return "conflict"
    return "current" if manifest(local) == manifest(upstream) else "changed"


def copy_skill(source: Path, destination: Path, backups: Path) -> str:
    if destination.exists():
        backup = backup_skill(destination, backups)
        action = f"updated (backup: {backup.name})"
    else:
        action = "installed"
    shutil.copytree(source, destination)
    return action


def backup_skill(destination: Path, backups: Path) -> Path:
    backups.mkdir(exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = backups / f"{destination.name}-{timestamp}"
    number = 2
    while backup.exists():
        backup = backups / f"{destination.name}-{timestamp}-{number}"
        number += 1
    shutil.move(str(destination), str(backup))
    return backup


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="Preview differences without changing files.")
    mode.add_argument("--apply", action="store_true", help="Install or update all managed skills.")
    parser.add_argument(
        "--skills-dir",
        type=Path,
        default=get_default_skills_dir(),
        help="Codex skills directory (default: $CODEX_HOME/skills or ~/.codex/skills).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    skills_dir = args.skills_dir.expanduser().resolve()
    try:
        commit = get_json(f"https://api.github.com/repos/{REPOSITORY}/commits/{BRANCH}")["sha"]
        with tempfile.TemporaryDirectory(prefix="mattpocock-skills-") as temporary:
            snapshot = extract_snapshot(commit, Path(temporary))
            results: list[tuple[str, str, Path]] = []
            for name, relative_source in MANAGED_SKILLS.items():
                source = snapshot / relative_source
                if not (source / "SKILL.md").is_file():
                    raise RuntimeError(f"Upstream skill is missing its SKILL.md: {relative_source}")
                local = skills_dir / name
                predecessor = skills_dir / RENAMED_SKILLS.get(name, "")
                if not local.exists() and predecessor.exists():
                    results.append((name, "changed", source))
                else:
                    results.append((name, classify(local, source), source))

            print(f"Upstream: {REPOSITORY}@{commit}")
            for status in ("missing", "changed", "conflict", "current"):
                names = [name for name, result, _ in results if result == status]
                if names:
                    print(f"{status.capitalize()} ({len(names)}): {', '.join(names)}")

            changes = [item for item in results if item[1] != "current"]
            if args.check:
                print("No local files were changed.")
                return 0

            skills_dir.mkdir(parents=True, exist_ok=True)
            backups = skills_dir / ".mattpocock-skills-backups"
            for name, status, source in changes:
                predecessor_name = RENAMED_SKILLS.get(name)
                predecessor = skills_dir / predecessor_name if predecessor_name else None
                if predecessor and predecessor.exists() and not (skills_dir / name).exists():
                    backup = backup_skill(predecessor, backups)
                    print(f"{name}: migrated {predecessor.name} to backup {backup.name}")
                action = copy_skill(source, skills_dir / name, backups)
                print(f"{name}: {action}")
            state = {
                "repository": REPOSITORY,
                "branch": BRANCH,
                "commit": commit,
                "synced_at": datetime.now(timezone.utc).isoformat(),
                "managed_skills": list(MANAGED_SKILLS),
            }
            (skills_dir / ".mattpocock-skills-state.json").write_text(
                json.dumps(state, indent=2) + "\n", encoding="utf-8"
            )
            print("Sync complete." if changes else "Already current; recorded the upstream revision.")
            return 0
    except (KeyError, RuntimeError, URLError, zipfile.BadZipFile, OSError) as error:
        print(f"Sync failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
