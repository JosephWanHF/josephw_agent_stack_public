#!/usr/bin/env python3
"""Export, install, and validate Joseph's portable agent stack."""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import hmac
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
import shutil
import sys
from typing import Any


STACK_NAME = "josephw_agent_stack"
STATE_FILE = ".josephw-agent-stack-state.json"
BACKUP_DIR = ".josephw-agent-stack-backups"
PUBLIC_EXPORT_CONFIG = "public-export.json"

SKILL_IGNORE_DIRS = {
    ".git",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
}

SKILL_IGNORE_FILES = {
    ".DS_Store",
    "Thumbs.db",
}

SKILL_IGNORE_GLOBS = {
    "*.pyc",
    "*.pyo",
}

FORBIDDEN_REPO_GLOBS = {
    "auth.json",
    "config.toml",
    ".codex-global-state.json",
    "cap_sid",
    "*.sqlite",
    "*.sqlite-shm",
    "*.sqlite-wal",
    "*.db",
    "*.log",
    "logs_*.sqlite",
    "thread_history_*.sqlite",
    "state_*.sqlite",
    "queue_*.sqlite",
    "memories_*.sqlite",
}

DECLARED_CONNECTORS = [
    {
        "name": "GitHub",
        "purpose": "Repository transport, issues, pull requests, and publishing.",
        "reauthorize_on_target": True,
    },
    {
        "name": "Gmail",
        "purpose": "Mail search and message workflows used by personal capture skills.",
        "reauthorize_on_target": True,
    },
    {
        "name": "Google Calendar",
        "purpose": "Calendar search, availability, and scheduling workflows.",
        "reauthorize_on_target": True,
    },
    {
        "name": "Google Drive",
        "purpose": "Drive, Docs, Sheets, and Slides workflows.",
        "reauthorize_on_target": True,
    },
    {
        "name": "Figma",
        "purpose": "Figma design, FigJam, slides, and design-to-code workflows.",
        "reauthorize_on_target": True,
    },
    {
        "name": "Hugging Face",
        "purpose": "Model, dataset, paper, Space, and Hub job workflows.",
        "reauthorize_on_target": True,
    },
    {
        "name": "OpenAI Developers",
        "purpose": "OpenAI API, Agents SDK, troubleshooting, and API key workflows.",
        "reauthorize_on_target": True,
    },
    {
        "name": "Supabase",
        "purpose": "Database management and query workflows.",
        "reauthorize_on_target": True,
    },
    {
        "name": "Vercel",
        "purpose": "Deployment, hosting, project, and observability workflows.",
        "reauthorize_on_target": True,
    },
    {
        "name": "Sites",
        "purpose": "OpenAI Sites creation and hosting workflows.",
        "reauthorize_on_target": True,
    },
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def default_codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()


def default_skills_dir() -> Path:
    return default_codex_home() / "skills"


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def safe_rmtree(path: Path, allowed_parent: Path) -> None:
    path = path.resolve()
    allowed_parent = allowed_parent.resolve()
    if path == allowed_parent or not is_relative_to(path, allowed_parent):
        raise RuntimeError(f"Refusing to remove path outside allowed parent: {path}")
    if path.exists():
        shutil.rmtree(path)


def should_ignore_file(path: Path) -> bool:
    if any(part in SKILL_IGNORE_DIRS for part in path.parts):
        return True
    if path.name in SKILL_IGNORE_FILES:
        return True
    return any(fnmatch.fnmatch(path.name, pattern) for pattern in SKILL_IGNORE_GLOBS)


def iter_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        if path.is_file() and not should_ignore_file(path.relative_to(root)):
            files.append(path)
    return files


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_directory(root: Path) -> str:
    digest = hashlib.sha256()
    for path in iter_files(root):
        relative = path.relative_to(root).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        digest.update(b"\0")
    return digest.hexdigest()


def file_count(root: Path) -> int:
    return len(iter_files(root))


def copy_skill_tree(source: Path, destination: Path) -> None:
    def ignore(directory: str, names: list[str]) -> set[str]:
        ignored: set[str] = set()
        for name in names:
            path = Path(directory) / name
            rel = path.relative_to(source) if is_relative_to(path, source) else Path(name)
            if path.is_dir() and name in SKILL_IGNORE_DIRS:
                ignored.add(name)
            elif path.is_file() and should_ignore_file(rel):
                ignored.add(name)
        return ignored

    shutil.copytree(source, destination, ignore=ignore)


def discover_skills(skills_dir: Path) -> list[Path]:
    if not skills_dir.exists():
        raise RuntimeError(f"Skills directory does not exist: {skills_dir}")
    skills: list[Path] = []
    for child in sorted(skills_dir.iterdir(), key=lambda item: item.name.lower()):
        if not child.is_dir():
            continue
        if child.name.startswith("."):
            continue
        if (child / "SKILL.md").is_file():
            skills.append(child)
    return skills


def latest_version_name(version_names: list[str]) -> str | None:
    if not version_names:
        return None
    return sorted(version_names)[-1]


def detect_curated_plugins(codex_home: Path) -> list[dict[str, Any]]:
    root = codex_home / "plugins" / "cache" / "openai-curated-remote"
    if not root.exists():
        return []
    plugins: list[dict[str, Any]] = []
    for child in sorted(root.iterdir(), key=lambda item: item.name.lower()):
        if not child.is_dir():
            continue
        versions = [item.name for item in child.iterdir() if item.is_dir()]
        plugins.append(
            {
                "id": child.name,
                "versions_seen": versions,
                "latest_seen": latest_version_name(versions),
                "vendor_code_not_vendored": True,
            }
        )
    return plugins


def yaml_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    return json.dumps(str(value), ensure_ascii=False)


def write_yaml_value(lines: list[str], value: Any, indent: int, key: str | None = None) -> None:
    prefix = " " * indent
    if key is not None:
        if isinstance(value, (dict, list)):
            lines.append(f"{prefix}{key}:")
            write_yaml_value(lines, value, indent + 2)
        else:
            lines.append(f"{prefix}{key}: {yaml_scalar(value)}")
        return

    if isinstance(value, dict):
        for child_key, child_value in value.items():
            write_yaml_value(lines, child_value, indent, str(child_key))
    elif isinstance(value, list):
        if not value:
            lines.append(f"{prefix}[]")
        for item in value:
            if isinstance(item, dict):
                lines.append(f"{prefix}-")
                write_yaml_value(lines, item, indent + 2)
            else:
                lines.append(f"{prefix}- {yaml_scalar(item)}")
    else:
        lines.append(f"{prefix}{yaml_scalar(value)}")


def write_manifest(repo_root: Path, manifest: dict[str, Any]) -> None:
    lines = ["# Generated by scripts/agent-stack.py. Edit source skills, then run export.\n"]
    write_yaml_value(lines, manifest, 0)
    (repo_root / "agent-stack.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def manifest_skill_names(repo_root: Path) -> list[str]:
    manifest = repo_root / "agent-stack.yaml"
    if not manifest.exists():
        return []
    names: list[str] = []
    in_skills = False
    for raw_line in manifest.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        if line == "skills:":
            in_skills = True
            continue
        if in_skills and line and not line.startswith(" "):
            break
        stripped = line.strip()
        if in_skills and stripped.startswith("name:"):
            value = stripped.split(":", 1)[1].strip()
            try:
                names.append(json.loads(value))
            except json.JSONDecodeError:
                names.append(value.strip("\"'"))
    return names


def manifest_skill_entries(repo_root: Path) -> list[dict[str, Any]]:
    """Parse the generated skills section without accepting arbitrary YAML tags."""
    manifest = repo_root / "agent-stack.yaml"
    if not manifest.is_file():
        raise RuntimeError("Missing agent-stack.yaml")

    entries: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    in_skills = False
    for raw_line in manifest.read_text(encoding="utf-8").splitlines():
        if raw_line == "skills:":
            in_skills = True
            continue
        if in_skills and raw_line and not raw_line.startswith(" "):
            break
        if not in_skills:
            continue
        stripped = raw_line.strip()
        if stripped == "-":
            if current is not None:
                entries.append(current)
            current = {}
            continue
        if current is None or ":" not in stripped:
            continue
        key, raw_value = stripped.split(":", 1)
        if key not in {"name", "path", "files", "sha256"}:
            continue
        value = raw_value.strip()
        try:
            current[key] = json.loads(value)
        except json.JSONDecodeError as error:
            raise RuntimeError(f"Invalid manifest value for {key}: {value}") from error
    if current is not None:
        entries.append(current)
    return entries


def verify_manifest_integrity(repo_root: Path) -> list[str]:
    entries = manifest_skill_entries(repo_root)
    if not entries:
        return ["Manifest has no skill entries"]

    errors: list[str] = []
    seen_names: set[str] = set()
    seen_paths: set[str] = set()
    declared_names: set[str] = set()
    skills_root = (repo_root / "skills").resolve()

    for index, entry in enumerate(entries, start=1):
        missing = {"name", "path", "files", "sha256"} - entry.keys()
        if missing:
            errors.append(f"Manifest skill entry {index} is missing: {', '.join(sorted(missing))}")
            continue
        name = entry["name"]
        relative_path = entry["path"]
        expected_files = entry["files"]
        expected_hash = entry["sha256"]
        if not isinstance(name, str) or not name or Path(name).name != name:
            errors.append(f"Manifest skill entry {index} has an invalid name")
            continue
        if name in seen_names:
            errors.append(f"Duplicate manifest skill name: {name}")
        seen_names.add(name)
        declared_names.add(name)
        if not isinstance(relative_path, str) or relative_path in seen_paths:
            errors.append(f"Duplicate or invalid manifest path for skill: {name}")
            continue
        seen_paths.add(relative_path)
        source = (repo_root / relative_path).resolve()
        if not is_relative_to(source, skills_root) or source.parent != skills_root:
            errors.append(f"Manifest path escapes or is not a direct child of skills/: {relative_path}")
            continue
        if source.name != name:
            errors.append(f"Manifest name/path mismatch: {name} != {relative_path}")
        if not source.is_dir() or not (source / "SKILL.md").is_file():
            errors.append(f"Manifest skill is missing or invalid: {relative_path}")
            continue
        actual_files = file_count(source)
        actual_hash = sha256_directory(source)
        if not isinstance(expected_files, int) or actual_files != expected_files:
            errors.append(f"File count mismatch for {name}: expected {expected_files}, got {actual_files}")
        if not isinstance(expected_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_hash):
            errors.append(f"Invalid SHA-256 in manifest for {name}")
        elif not hmac.compare_digest(actual_hash, expected_hash):
            errors.append(f"SHA-256 mismatch for {name}: expected {expected_hash}, got {actual_hash}")

    actual_names = {skill.name for skill in discover_skills(skills_root)}
    for name in sorted(actual_names - declared_names):
        errors.append(f"Unexpected skill not declared in manifest: {name}")
    for name in sorted(declared_names - actual_names):
        errors.append(f"Manifest declares missing skill: {name}")
    return errors


def refresh_manifest_integrity(repo_root: Path) -> None:
    manifest = repo_root / "agent-stack.yaml"
    lines = manifest.read_text(encoding="utf-8").splitlines()
    current_name: str | None = None
    in_skills = False
    for index, raw_line in enumerate(lines):
        if raw_line == "skills:":
            in_skills = True
            continue
        if in_skills and raw_line and not raw_line.startswith(" "):
            break
        if not in_skills:
            continue
        stripped = raw_line.strip()
        if stripped.startswith("name:"):
            current_name = json.loads(stripped.split(":", 1)[1].strip())
        elif current_name and stripped.startswith("files:"):
            source = repo_root / "skills" / current_name
            lines[index] = f"    files: {file_count(source)}"
        elif current_name and stripped.startswith("sha256:"):
            source = repo_root / "skills" / current_name
            lines[index] = f'    sha256: "{sha256_directory(source)}"'
    manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")


def command_public_export(args: argparse.Namespace) -> int:
    repo_root = args.repo_root.resolve()
    output_dir = args.output_dir.expanduser().resolve()
    integrity_errors = verify_manifest_integrity(repo_root)
    if integrity_errors:
        raise RuntimeError("Private stack integrity check failed:\n- " + "\n- ".join(integrity_errors))
    config_path = repo_root / PUBLIC_EXPORT_CONFIG
    if not config_path.is_file():
        raise RuntimeError(f"Missing {PUBLIC_EXPORT_CONFIG}")
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if output_dir == repo_root or is_relative_to(repo_root, output_dir):
        raise RuntimeError("Public output directory cannot contain the private repository")
    if output_dir.exists():
        safe_rmtree(output_dir, output_dir.parent)

    excluded_roots = {".git", ".github", PUBLIC_EXPORT_CONFIG, "public"}

    def ignore(_directory: str, names: list[str]) -> set[str]:
        return {name for name in names if name in excluded_roots or name == BACKUP_DIR}

    shutil.copytree(repo_root, output_dir, ignore=ignore)
    public_assets = repo_root / "public"
    for asset in ("README.md", "AGENTS.md"):
        source = public_assets / asset
        if source.is_file():
            shutil.copy2(source, output_dir / asset)

    for rule in config.get("replacements", []):
        target = output_dir / rule["path"]
        if not target.is_file():
            raise RuntimeError(f"Public replacement target is missing: {rule['path']}")
        content = target.read_text(encoding="utf-8")
        old = rule["old"]
        count = content.count(old)
        if count != rule.get("count", 1):
            raise RuntimeError(
                f"Public replacement count mismatch for {rule['path']}: "
                f"expected {rule.get('count', 1)}, got {count}"
            )
        target.write_text(content.replace(old, rule["new"]), encoding="utf-8")

    refresh_manifest_integrity(output_dir)
    public_errors = verify_manifest_integrity(output_dir)
    if public_errors:
        raise RuntimeError("Generated public stack failed integrity check:\n- " + "\n- ".join(public_errors))

    forbidden_patterns = config.get("forbidden_public_patterns", [])
    leaks: list[str] = []
    for path in iter_files(output_dir):
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in forbidden_patterns:
            if re.search(pattern, content):
                leaks.append(f"{path.relative_to(output_dir).as_posix()}: {pattern}")
    if leaks:
        raise RuntimeError("Generated public stack contains forbidden private data:\n- " + "\n- ".join(leaks))
    print(f"Generated public stack: {output_dir}")
    return 0


def command_export(args: argparse.Namespace) -> int:
    repo_root = args.repo_root.resolve()
    codex_home = args.codex_home.expanduser().resolve()
    source_skills_dir = args.skills_dir.expanduser().resolve() if args.skills_dir else codex_home / "skills"
    destination_skills_dir = repo_root / "skills"

    skills = discover_skills(source_skills_dir)
    if not skills:
        raise RuntimeError(f"No skills with SKILL.md found in {source_skills_dir}")

    destination_skills_dir.mkdir(parents=True, exist_ok=True)
    safe_rmtree(destination_skills_dir, repo_root)
    destination_skills_dir.mkdir(parents=True, exist_ok=True)

    skill_entries: list[dict[str, Any]] = []
    for skill in skills:
        destination = destination_skills_dir / skill.name
        copy_skill_tree(skill, destination)
        skill_entries.append(
            {
                "name": skill.name,
                "path": f"skills/{skill.name}",
                "files": file_count(destination),
                "sha256": sha256_directory(destination),
            }
        )

    manifest = {
        "name": STACK_NAME,
        "version": "0.1.0",
        "generated_at": utc_now(),
        "source": {
            "type": "codex-profile",
            "skills_dir": "$CODEX_HOME/skills or ~/.codex/skills",
        },
        "policy": {
            "vendors_openai_default_skills": False,
            "vendors_plugin_caches": False,
            "requires_target_reauthorization": True,
        },
        "skills": skill_entries,
        "curated_plugins_seen": detect_curated_plugins(codex_home),
        "connectors": DECLARED_CONNECTORS,
        "omitted": [
            "OpenAI built-in/default skills",
            "plugin cache contents",
            "OAuth tokens and auth.json",
            "browser state",
            "logs and SQLite runtime databases",
            "machine-local Codex state",
        ],
    }
    write_manifest(repo_root, manifest)
    print(f"Exported {len(skill_entries)} skills to {destination_skills_dir}")
    print(f"Wrote {repo_root / 'agent-stack.yaml'}")
    return 0


def command_install(args: argparse.Namespace) -> int:
    repo_root = args.repo_root.resolve()
    integrity_errors = verify_manifest_integrity(repo_root)
    if integrity_errors:
        raise RuntimeError("Refusing to install a stack with integrity errors:\n- " + "\n- ".join(integrity_errors))
    source_skills_dir = repo_root / "skills"
    target_skills_dir = args.skills_dir.expanduser().resolve() if args.skills_dir else default_skills_dir().resolve()
    skills = discover_skills(source_skills_dir)
    if not skills:
        raise RuntimeError(f"No stack skills found in {source_skills_dir}")

    target_skills_dir.mkdir(parents=True, exist_ok=True)
    backups_dir = target_skills_dir / BACKUP_DIR
    installed: list[str] = []
    current: list[str] = []
    changed: list[str] = []

    for source in skills:
        destination = target_skills_dir / source.name
        source_hash = sha256_directory(source)
        destination_hash = sha256_directory(destination) if destination.exists() and destination.is_dir() else None

        if destination_hash == source_hash:
            current.append(source.name)
            continue

        changed.append(source.name)
        if args.dry_run:
            continue

        if destination.exists():
            backups_dir.mkdir(exist_ok=True)
            backup = backups_dir / f"{destination.name}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
            number = 2
            while backup.exists():
                backup = backups_dir / f"{destination.name}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{number}"
                number += 1
            if not is_relative_to(destination, target_skills_dir):
                raise RuntimeError(f"Refusing to move path outside skills dir: {destination}")
            shutil.move(str(destination), str(backup))
        copy_skill_tree(source, destination)
        installed.append(source.name)

    print(f"Target skills dir: {target_skills_dir}")
    if current:
        print(f"Already current ({len(current)}): {', '.join(current)}")
    if args.dry_run:
        print(f"Would install or update ({len(changed)}): {', '.join(changed) if changed else 'none'}")
        print("No files were changed.")
        return 0

    state = {
        "stack": STACK_NAME,
        "installed_at": utc_now(),
        "repo": str(repo_root),
        "skills": [skill.name for skill in skills],
    }
    (target_skills_dir / STATE_FILE).write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    print(f"Installed or updated ({len(installed)}): {', '.join(installed) if installed else 'none'}")
    print("Install complete.")
    return 0


def forbidden_repo_files(repo_root: Path) -> list[Path]:
    bad: list[Path] = []
    for path in sorted(repo_root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(repo_root).as_posix()
        if ".git/" in rel or rel.startswith(".git/"):
            continue
        for pattern in FORBIDDEN_REPO_GLOBS:
            if fnmatch.fnmatch(path.name, pattern) or fnmatch.fnmatch(rel, pattern):
                bad.append(path)
                break
    return bad


def command_validate(args: argparse.Namespace) -> int:
    repo_root = args.repo_root.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    if not (repo_root / "README.md").is_file():
        errors.append("Missing README.md")
    if not (repo_root / "AGENTS.md").is_file():
        errors.append("Missing AGENTS.md")
    if not (repo_root / "scripts" / "agent-stack.py").is_file():
        errors.append("Missing scripts/agent-stack.py")
    if not (repo_root / "agent-stack.yaml").is_file():
        warnings.append("Missing agent-stack.yaml; run export to generate it.")

    stack_skills_dir = repo_root / "skills"
    try:
        skills = discover_skills(stack_skills_dir)
    except RuntimeError as error:
        skills = []
        errors.append(str(error))

    for skill in skills:
        if not (skill / "SKILL.md").is_file():
            errors.append(f"Skill missing SKILL.md: {skill.name}")

    manifest_names = manifest_skill_names(repo_root)
    if manifest_names:
        skill_names = sorted(skill.name for skill in skills)
        if sorted(manifest_names) != skill_names:
            warnings.append("agent-stack.yaml skill list differs from skills/; run export.")

    if (repo_root / "agent-stack.yaml").is_file():
        errors.extend(verify_manifest_integrity(repo_root))

    bad_files = forbidden_repo_files(repo_root)
    for path in bad_files:
        errors.append(f"Forbidden local-state or secret-looking file: {path.relative_to(repo_root).as_posix()}")

    if args.skills_dir:
        target_skills_dir = args.skills_dir.expanduser().resolve()
        missing = [skill.name for skill in skills if not (target_skills_dir / skill.name / "SKILL.md").is_file()]
        if missing:
            warnings.append(f"Target skills dir is missing {len(missing)} stack skills: {', '.join(missing)}")

    report = {
        "repo": str(repo_root),
        "skills": len(skills),
        "errors": errors,
        "warnings": warnings,
    }
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Repo: {repo_root}")
        print(f"Skills: {len(skills)}")
        for warning in warnings:
            print(f"Warning: {warning}")
        for error in errors:
            print(f"Error: {error}", file=sys.stderr)
        print("Validation passed." if not errors else "Validation failed.")
    return 1 if errors else 0


def command_list(args: argparse.Namespace) -> int:
    repo_root = args.repo_root.resolve()
    skills = discover_skills(repo_root / "skills")
    for skill in skills:
        print(skill.name)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=repo_root_from_script(),
        help="Stack repository root. Defaults to this script's parent repo.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    export_parser = subparsers.add_parser("export", help="Export local Codex skills into this repo.")
    export_parser.add_argument("--codex-home", type=Path, default=default_codex_home())
    export_parser.add_argument("--skills-dir", type=Path, default=None)
    export_parser.set_defaults(func=command_export)

    install_parser = subparsers.add_parser("install", help="Install stack skills into a Codex skills dir.")
    install_parser.add_argument("--skills-dir", type=Path, default=None)
    install_parser.add_argument("--dry-run", action="store_true")
    install_parser.set_defaults(func=command_install)

    validate_parser = subparsers.add_parser("validate", help="Validate repo shape and target availability.")
    validate_parser.add_argument("--skills-dir", type=Path, default=None)
    validate_parser.add_argument("--json", action="store_true")
    validate_parser.set_defaults(func=command_validate)

    list_parser = subparsers.add_parser("list", help="List skills in this stack.")
    list_parser.set_defaults(func=command_list)

    public_parser = subparsers.add_parser(
        "public-export", help="Generate a sanitized public stack from this private canonical repository."
    )
    public_parser.add_argument("--output-dir", type=Path, required=True)
    public_parser.set_defaults(func=command_public_export)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except (OSError, RuntimeError) as error:
        print(f"agent-stack: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
