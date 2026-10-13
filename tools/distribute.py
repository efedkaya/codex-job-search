#!/usr/bin/env python3
"""Validate, package, or locally install the explicit public distribution."""

import argparse
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import sys
import tempfile
from urllib.parse import unquote, urlsplit
import zipfile

ROOT = Path(__file__).resolve().parent.parent
SKILL_PREFIX = "skills/job-search/"
PRIVATE = re.compile(r"^(?:profile\.json|tracker\.json|evidence\.json|search_state\.json|discoveries\.json|vacancies\.json|run_metrics\.json|candidate-brief\.json|\.(?:search_state|vacancies|tracker)\.lock|\.env(?:\..*)?|secrets?.*|credentials?.*|id_rsa|id_ed25519)$", re.I)
SENSITIVE = [
    re.compile(r"/(?:Users|home)/[^/\s\"'<>]+"),
    re.compile(r"[A-Za-z]:[\\/]+Users[\\/]+[^\\/\s\"'<>]+", re.I),
    re.compile(r"-----BEGIN (?:[A-Z ]*PRIVATE KEY)-----"),
    re.compile(r"(?:AKIA|ASIA)[A-Z0-9]{16}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}"),
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
]
LINK = re.compile(r"!?\[[^\]]*\]\((?:<([^>]+)>|([^\s)]+))(?:\s+[\"'][^)]*[\"'])?\)")


def safe_relative(value):
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        raise ValueError("Manifest paths must be nonempty relative POSIX paths")
    if any(ord(character) < 32 or ord(character) == 127 for character in value) or value.lower().endswith(".zip"):
        raise ValueError("Control characters and nested ZIP archives are not allowed")
    if any(part in ("", ".", "..") for part in value.split("/")) or PurePosixPath(value).is_absolute():
        raise ValueError("Manifest contains an unsafe path")
    if any(part.casefold() in {"applications", "sources"} for part in value.split("/")[:-1]):
        raise ValueError("Manifest contains a private-state directory")
    for part in value.split("/"):
        if PRIVATE.fullmatch(part) and not part.lower().endswith("_fictional.json"):
            raise ValueError("Manifest contains a private-state filename")
    return value


def no_symlinks(path, boundary):
    current = path
    while current != boundary:
        if current.is_symlink():
            raise ValueError("Symlinks are not allowed")
        if current.parent == current:
            raise ValueError("Path escapes its boundary")
        current = current.parent


def check_links(root, path, content, allowed):
    for match in LINK.finditer(content):
        target = match.group(1) or match.group(2)
        if target.startswith("#"):
            continue
        parsed = urlsplit(target)
        if parsed.scheme in ("http", "https") and parsed.netloc:
            continue
        if parsed.scheme or parsed.netloc or target.startswith("/") or "\\" in target:
            raise ValueError(f"Unsupported Markdown link in {path.name}")
        linked = path.parent / unquote(parsed.path)
        resolved = linked.resolve()
        if not resolved.is_relative_to(root) or not resolved.exists():
            raise ValueError(f"Missing or escaping Markdown link in {path.name}")
        no_symlinks(linked, root)
        relative = resolved.relative_to(root).as_posix()
        if resolved.is_file() and relative not in allowed:
            raise ValueError(f"Markdown link targets an unlisted file in {path.name}")
        if resolved.is_dir() and relative != "." and not any(isinstance(name, str) and name.startswith(relative + "/") for name in allowed):
            raise ValueError(f"Markdown link targets an unlisted directory in {path.name}")


def check(root=ROOT):
    root = Path(root).resolve()
    manifest = root / "distribution.json"
    no_symlinks(manifest, root)
    data = json.loads(manifest.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("version"), str) or not data["version"]:
        raise ValueError("Manifest requires a version string")
    names = data.get("files")
    if not isinstance(names, list) or not names or "distribution.json" not in names:
        raise ValueError("Manifest must explicitly include distribution.json")
    checked, seen = [], set()
    for name in names:
        safe_relative(name)
        if name.casefold() in seen:
            raise ValueError("Duplicate or case-colliding manifest paths")
        seen.add(name.casefold())
        path = root / name
        no_symlinks(path, root)
        if not path.is_file():
            raise ValueError(f"Missing public file: {name}")
        content = path.read_text(encoding="utf-8")
        if any(pattern.search(content) for pattern in SENSITIVE):
            raise ValueError(f"Possible credential or machine-specific path in {name}")
        if path.suffix.lower() == ".md":
            check_links(root, path, content, names)
        checked.append((name, path))
    return checked


def package(output, root=ROOT):
    files = check(root)
    output = Path(output).absolute()
    if output.suffix.lower() != ".zip":
        raise ValueError("Package output must have a .zip extension")
    no_symlinks(output, Path(output.anchor))
    if output.resolve() in {path.resolve() for _, path in files}:
        raise ValueError("Package output would overwrite a source file")
    output.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=".job-search-", suffix=".zip", dir=output.parent)
    os.close(handle)
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for name, path in sorted(files):
                info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, path.read_bytes(), compresslevel=9)
        os.replace(temporary, output)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return output


def install(skills_dir, root=ROOT):
    files = [(name[len(SKILL_PREFIX):], path) for name, path in check(root) if name.startswith(SKILL_PREFIX)]
    if not any(name == "SKILL.md" for name, _ in files):
        raise ValueError("Manifest has no installable job-search skill")
    parent = Path(skills_dir).expanduser().absolute()
    no_symlinks(parent, Path(parent.anchor))
    destination = parent / "job-search"
    no_symlinks(destination, parent)
    if destination.exists():
        if not destination.is_dir():
            raise ValueError("Existing install is not a directory; left unchanged")
        existing = list(destination.rglob("*"))
        if any(path.is_symlink() for path in existing):
            raise ValueError("Existing install contains symlinks; left unchanged")
        actual = {path.relative_to(destination).as_posix() for path in existing if path.is_file()}
        if actual != {name for name, _ in files} or any((destination / name).read_bytes() != source.read_bytes() for name, source in files):
            raise ValueError("Existing install differs; left unchanged. Choose a new skills directory or back it up yourself")
        return "unchanged"
    parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".job-search-", dir=parent))
    try:
        for name, source in files:
            target = staging / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        if destination.exists() or destination.is_symlink():
            raise ValueError("Install destination appeared during copy; left unchanged")
        staging.rename(destination)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return "installed"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("check")
    commands.add_parser("package").add_argument("--output", type=Path, required=True)
    commands.add_parser("install").add_argument("--skills-dir", type=Path, default=Path("~/.agents/skills"))
    args = parser.parse_args()
    try:
        if args.command == "check":
            print(f"Validated {len(check())} allowlisted public files")
        elif args.command == "package":
            print(f"Packaged: {package(args.output)}")
        else:
            print(f"Skill {install(args.skills_dir)}")
    except (OSError, ValueError, UnicodeError, zipfile.BadZipFile) as error:
        parser.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    main()
