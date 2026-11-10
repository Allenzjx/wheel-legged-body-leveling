"""Record the portable package's current files; never modifies runtime values."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
INCLUDED = ("src", "configs", "reference", "artifacts", "assets", "checkpoints", "scripts")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    files = []
    for name in INCLUDED:
        for path in (ROOT / name).rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc":
                files.append({"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "bytes": path.stat().st_size})
    for name in ("stages.json", "pyproject.toml", ".gitattributes"):
        path = ROOT / name
        if path.exists():
            files.append({"path": name, "sha256": sha(path), "bytes": path.stat().st_size})
    result = {"schema": "wlr50.portable-package.v1", "scope": "Portable source, numeric configuration, assets and model bundles", "files": sorted(files, key=lambda item: item["path"])}
    (ROOT / "package-manifest.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"files": len(files), "manifest": "package-manifest.json"}))


if __name__ == "__main__":
    main()
