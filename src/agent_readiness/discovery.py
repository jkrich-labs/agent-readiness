from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


LANGUAGE_MARKERS = {
    "python": ("pyproject.toml", "requirements.txt", "setup.py"),
    "typescript": ("tsconfig.json", "package.json"),
    "javascript": ("package.json",),
    "go": ("go.mod",),
    "rust": ("Cargo.toml",),
}


@dataclass(frozen=True)
class ApplicationInfo:
    path: str
    description: str
    languages: tuple[str, ...]


@dataclass(frozen=True)
class RepositoryDiscovery:
    root: Path
    apps: dict[str, ApplicationInfo]
    languages: tuple[str, ...]


def _has_any_file(root: Path, names: tuple[str, ...]) -> bool:
    return any((root / name).exists() for name in names)


def _contains_suffix(root: Path, suffixes: tuple[str, ...], max_files: int = 600) -> bool:
    seen = 0
    for path in root.rglob("*"):
        if path.is_dir():
            if path.name in {".git", "node_modules", ".venv", "dist", "build", "target", ".pytest_cache"}:
                continue
            continue
        seen += 1
        if path.suffix.lower() in suffixes:
            return True
        if seen >= max_files:
            break
    return False


def detect_languages(root: Path) -> tuple[str, ...]:
    found: list[str] = []

    if _has_any_file(root, LANGUAGE_MARKERS["python"]) or _contains_suffix(root, (".py",)):
        found.append("python")
    if (root / "package.json").exists():
        if _has_any_file(root, ("tsconfig.json",)) or _contains_suffix(root, (".ts", ".tsx")):
            found.append("typescript")
        elif _contains_suffix(root, (".js", ".jsx", ".mjs", ".cjs")):
            found.append("javascript")
        else:
            found.append("javascript")
    if _has_any_file(root, LANGUAGE_MARKERS["go"]) or _contains_suffix(root, (".go",)):
        found.append("go")
    if _has_any_file(root, LANGUAGE_MARKERS["rust"]) or _contains_suffix(root, (".rs",)):
        found.append("rust")

    return tuple(dict.fromkeys(found))


def _looks_like_app(path: Path) -> bool:
    if not path.is_dir():
        return False

    marker_files = (
        "pyproject.toml",
        "requirements.txt",
        "setup.py",
        "package.json",
        "go.mod",
        "Cargo.toml",
        "Dockerfile",
    )
    if any((path / marker).exists() for marker in marker_files):
        return True

    return (path / "src").is_dir() or (path / "app").is_dir()


def _describe_app(path: Path, root: Path) -> str:
    readme = path / "README.md"
    if readme.exists():
        for line in readme.read_text(encoding="utf-8", errors="ignore").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            return stripped[:140]

    relative = "." if path == root else str(path.relative_to(root))
    if relative == ".":
        return "Repository root application"
    return f"Application at {relative}"


def discover_repository(repo_root: Path) -> RepositoryDiscovery:
    root = repo_root.resolve()

    fixed_candidates = ["backend", "frontend", "api", "web", "app", "service", "services", "cli"]
    candidates: list[Path] = []
    for name in fixed_candidates:
        candidate = root / name
        if _looks_like_app(candidate):
            candidates.append(candidate)

    apps_dir = root / "apps"
    if apps_dir.is_dir():
        for child in sorted(apps_dir.iterdir()):
            if _looks_like_app(child):
                candidates.append(child)

    if not candidates:
        if _looks_like_app(root):
            candidates = [root]
        else:
            # Droid behavior: fallback to root when no explicit apps are found.
            candidates = [root]

    unique_candidates: list[Path] = []
    seen = set()
    for candidate in sorted(candidates):
        resolved = candidate.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        unique_candidates.append(resolved)

    apps: dict[str, ApplicationInfo] = {}
    for candidate in unique_candidates:
        rel = "." if candidate == root else str(candidate.relative_to(root))
        languages = detect_languages(candidate)
        apps[rel] = ApplicationInfo(
            path=rel,
            description=_describe_app(candidate, root),
            languages=languages,
        )

    repo_languages = detect_languages(root)
    return RepositoryDiscovery(root=root, apps=apps, languages=repo_languages)
