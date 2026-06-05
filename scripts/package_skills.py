"""Package MoneyPrinter skills as .skill zip archives."""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path


EXCLUDED_NAMES = {"__pycache__", ".DS_Store"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".tmp", ".skill"}


def should_include(path: Path) -> bool:
    """Return True when a path should be included in a skill package."""
    if any(part in EXCLUDED_NAMES for part in path.parts):
        return False
    if path.suffix in EXCLUDED_SUFFIXES:
        return False
    return True


def find_skill_dirs(root: Path) -> list[Path]:
    """Find direct child directories that contain a SKILL.md file."""
    return sorted(
        path for path in root.iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    )


def package_skill(skill_dir: Path, root: Path) -> Path:
    """Package one skill directory into a sibling .skill archive."""
    output_path = root / f"{skill_dir.name}.skill"
    files = sorted(
        path for path in skill_dir.rglob("*")
        if path.is_file() and should_include(path)
    )

    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path in files:
            archive.write(file_path, file_path.relative_to(root).as_posix())

    return output_path


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Package docs/skills folders into .skill archives.")
    parser.add_argument(
        "--root",
        default="docs/skills",
        help="Skills root directory. Defaults to docs/skills.",
    )
    parser.add_argument(
        "--skill",
        default="",
        help="Package one skill by folder name. Defaults to all skills.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    root = Path(args.root).resolve()

    if not root.is_dir():
        print(f"error: skills root not found: {root}", file=sys.stderr)
        return 1

    if args.skill:
        skill_dir = root / args.skill
        if not (skill_dir / "SKILL.md").is_file():
            print(f"error: skill not found or missing SKILL.md: {skill_dir}", file=sys.stderr)
            return 1
        skill_dirs = [skill_dir]
    else:
        skill_dirs = find_skill_dirs(root)

    if not skill_dirs:
        print(f"error: no skills found under {root}", file=sys.stderr)
        return 1

    for skill_dir in skill_dirs:
        output_path = package_skill(skill_dir, root)
        print(output_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
