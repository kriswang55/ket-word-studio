"""Create platform-specific release assets from tracked source and verified EXEs."""

from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
VERSION = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))["version"]
EXCLUDED = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "node_modules",
}


def source_files():
    if (ROOT / ".git").exists():
        result = subprocess.run(
            ["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True
        )
        return [
            ROOT / name for name in result.stdout.decode("utf-8").split("\0") if name
        ]
    return [
        p
        for p in ROOT.rglob("*")
        if p.is_file()
        and not EXCLUDED.intersection(p.relative_to(ROOT).parts)
        and p.suffix not in {".exe", ".zip", ".pyc", ".log", ".sqlite3", ".tmp"}
        and p.relative_to(ROOT).parts[:2] != ("releases", "packages")
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "releases/packages")
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    exes = [
        ROOT / "releases/windows" / name
        for name in ("KETWordStudio.exe", "KETWordStudioWeb.exe")
    ]
    for exe in exes:
        if not exe.is_file():
            raise SystemExit(f"Build the Windows executable first: {exe.name}")
    recorded = dict(
        line.strip().split("  ", 1)[::-1]
        for line in (ROOT / "releases/windows/SHA256SUMS.txt").read_text().splitlines()
        if line.strip()
    )
    for exe in exes:
        if hashlib.sha256(exe.read_bytes()).hexdigest() != recorded.get(exe.name):
            raise SystemExit(f"Executable checksum differs: {exe.name}")
    files = source_files()
    source = [(p, p.relative_to(ROOT).as_posix()) for p in files]
    licenses = [
        (p, "licenses/" + p.relative_to(ROOT / "releases/windows/licenses").as_posix())
        for p in (ROOT / "releases/windows/licenses").rglob("*")
        if p.is_file()
    ]
    bundles = {
        f"KETWordStudio-Online-{VERSION}.zip": [
            (p, p.name) for p in sorted((ROOT / "launchers").glob("Open-KET-Online.*"))
        ],
        f"KETWordStudio-{VERSION}.zip": source
        + [(p, "releases/windows/" + p.name) for p in exes],
        f"KETWordStudio-Source-{VERSION}.zip": source,
        f"KETWordStudio-Windows-Qt-{VERSION}.zip": [(exes[0], exes[0].name)] + licenses,
        f"KETWordStudio-Windows-Web-{VERSION}.zip": [(exes[1], exes[1].name)]
        + licenses,
        f"KETWordStudio-Mac-Web-{VERSION}.zip": [
            (p, name)
            for p, name in source
            if name.startswith("site/")
            or name
            in {
                "run_web.py",
                "Start-Web-Mac.command",
                "ket_studio/__init__.py",
                "ket_studio/paths.py",
                "ket_studio/web_server.py",
            }
        ],
        f"KETWordStudio-Website-{VERSION}.zip": [
            (p, name.removeprefix("site/"))
            for p, name in source
            if name.startswith("site/")
        ],
    }
    guides = json.loads(
        (ROOT / "releases/instructions.json").read_text(encoding="utf-8")
    )
    instructions = guides["instructions"]
    archives = []
    for name, entries in bundles.items():
        target = output / name
        with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
            seen = set()
            for file, relative in entries:
                if relative in seen:
                    raise ValueError(f"Duplicate archive entry: {relative}")
                seen.add(relative)
                info = zipfile.ZipInfo.from_file(file, "KETWordStudio/" + relative)
                if file.suffix == ".command":
                    info.create_system = 3
                    info.external_attr = 0o100755 << 16
                archive.writestr(
                    info, file.read_bytes(), compress_type=zipfile.ZIP_DEFLATED
                )
            for kind, content in instructions.items():
                if f"-{kind}-" in name:
                    locales = ["en", "zh-CN", "zh-HK"]
                    names = ["README.md", "README.zh-CN.md", "README.zh-HK.md"]
                    labels = ["English", "简体中文", "繁体中文"]
                    for index, locale in enumerate(locales):
                        navigation = " | ".join(
                            f"**{label}**" if i == index else f"[{label}]({names[i]})"
                            for i, label in enumerate(labels)
                        )
                        archive.writestr(
                            "KETWordStudio/" + names[index],
                            f"# KET Word Studio {VERSION}\n\n{navigation}\n\n{content[locale]}\n\n{guides['intro'][locale]}\n",
                        )
        with zipfile.ZipFile(target) as archive:
            if archive.testzip() is not None:
                raise RuntimeError(f"ZIP verification failed: {name}")
        archives.append(target)
        print(f"{name}: {target.stat().st_size:,} bytes")
    checksum = output / f"SHA256SUMS-v{VERSION}.txt"
    launchers = sorted((ROOT / "launchers").glob("Open-KET-Online.*"))
    checksum.write_text(
        "".join(
            f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n"
            for p in [*archives, *exes, *launchers]
        ),
        encoding="ascii",
    )
    print(checksum.name)


if __name__ == "__main__":
    main()
