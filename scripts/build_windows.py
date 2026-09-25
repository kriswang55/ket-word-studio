"""Build both Windows executables using the active Python environment."""

from pathlib import Path
import argparse
import hashlib
import os
import subprocess
import sys
import tempfile


def main():
    if sys.platform != "win32":
        raise SystemExit("Build Windows executables on Windows. macOS uses run_web.py.")
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", choices=["all", "desktop", "web"], default="all")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    # Avoid collecting incompatible ICU/UCRT DLLs from unrelated programs on PATH.
    # This changes only the build subprocess, never the user's system environment.
    env = os.environ.copy()
    windows = Path(os.environ.get("SystemRoot", "C:/Windows"))
    env["PATH"] = os.pathsep.join(
        map(
            str,
            [
                Path(sys.executable).parent,
                Path(sys.base_prefix),
                windows / "System32",
                windows,
            ],
        )
    )
    for key in ("QT_PLUGIN_PATH", "QT_QPA_PLATFORM_PLUGIN_PATH", "QML2_IMPORT_PATH"):
        env.pop(key, None)
    targets = [
        ("desktop", "KETWordStudio", "run_desktop.py"),
        ("web", "KETWordStudioWeb", "run_web.py"),
    ]
    for kind, name, entry in targets:
        if args.target not in ("all", kind):
            continue
        with tempfile.TemporaryDirectory(prefix="ket-build-") as scratch:
            command = [
                sys.executable,
                "-m",
                "PyInstaller",
                "--noconfirm",
                "--clean",
                "--onefile",
                "--name",
                name,
                "--paths",
                str(root),
                "--distpath",
                str(root / "releases/windows"),
                "--workpath",
                str(Path(scratch) / "build"),
                "--specpath",
                scratch,
                "--icon",
                str(root / "ket_studio/assets/app.ico"),
                "--add-data",
                str(root / "ket_studio/assets") + ";ket_studio/assets",
                "--add-data",
                str(root / "site") + ";site",
                "--exclude-module",
                "PyQt5",
                "--exclude-module",
                "PyQt6",
                "--exclude-module",
                "PySide2",
            ]
            if kind == "desktop":
                command.append("--windowed")
            else:
                command += ["--exclude-module", "PySide6"]
            command.append(str(root / entry))
            subprocess.run(command, cwd=root, env=env, check=True)
    output = root / "releases/windows"
    executables = sorted(output.glob("*.exe"))
    (output / "SHA256SUMS.txt").write_text(
        "".join(
            f"{hashlib.sha256(file.read_bytes()).hexdigest()}  {file.name}\n"
            for file in executables
        ),
        encoding="ascii",
    )
    print("Executables: " + str(output))


if __name__ == "__main__":
    main()
