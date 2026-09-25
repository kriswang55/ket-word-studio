# Download guide

**English** | [简体中文](README.zh-CN.md) | [繁体中文](README.zh-HK.md)

Current release: **v3.1.0**. Download the appropriate files from the repository's **Releases** page and extract ZIP packages before use.

| File | Purpose | Requirements |
| --- | --- | --- |
| `KETWordStudio-Online-3.1.0.zip` | Online shortcuts that open GitHub Pages | `.url` for Windows, `.webloc` for Mac; an internet connection |
| `Open-KET-Online.url` / `Open-KET-Online.webloc` | Individual online shortcuts | Browser; no Python |
| `KETWordStudio-3.1.0.zip` | Full source, documentation and both Windows executables | Run directly on Windows; website source works on other platforms |
| `KETWordStudio-Source-3.1.0.zip` | Development, review and rebuilding | Node.js 20+ or Python 3.10+ for website preview; install dependencies for Qt |
| `KETWordStudio-Windows-Qt-3.1.0.zip` | Native Qt desktop application | Windows x64; no Python installation |
| `KETWordStudio-Windows-Web-3.1.0.zip` | Launch a local website | Windows x64; no Python installation |
| `KETWordStudio-Mac-Web-3.1.0.zip` | Local browser demonstration on Mac | Python 3.10+; no Qt |
| `KETWordStudio-Website-3.1.0.zip` | Static files for hosting or HTTP preview | Modern browser; do not open HTML directly |
| `KETWordStudio.exe` | Standalone desktop executable | Windows x64 |
| `KETWordStudioWeb.exe` | Standalone local-website executable | Windows x64 |
| `SHA256SUMS-v3.1.0.txt` | Download-integrity manifest | Any SHA-256 checksum tool |

The Mac browser package contains a Python static-preview launcher and website files, not a native `.app`. The deployed website needs no download or installation.

The website and desktop open in English and offer Simplified and Traditional Chinese. They need no login, support Student / Teacher views and use browser localStorage or desktop SQLite respectively. Each ZIP contains an English README plus linked Chinese instructions.

## Rebuild the packages

On Windows, run `python scripts/build_windows.py`, then `python scripts/package_releases.py`. Output defaults to `releases/packages/`; use `--output PATH` to choose another directory. The packager verifies ZIP integrity and produces the SHA-256 manifest. Source packaging uses tracked Git files, so stage new source and documentation files first.

[Back to README](../README.md)
