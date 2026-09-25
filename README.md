# KET Word Studio

**English** | [简体中文](README.zh-CN.md) | [繁体中文](README.zh-HK.md)

## Project documentation

| Document | Contents |
| --- | --- |
| **[Project overview](doc/en/project-overview.md)** | Purpose, scope and demonstration workflow |
| **[User guide](doc/en/user-guide.md)** | Student practice, teacher vocabulary management and data |
| **[Architecture](doc/en/architecture.md)** | Website, Qt desktop, persistence and grading |
| **[Deployment](doc/en/deployment.md)** | GitHub Pages, local preview and release packaging |
| **[Verification](doc/en/verification.md)** | Automated checks, runtime checks and validation limits |
| **[Downloads](releases/README.md)** | Online shortcuts and platform-specific packages |

[![version: 3.1.0](doc/badges/version.svg)](#try-it)
[![web: HTML + CSS + JavaScript](doc/badges/web.svg)](#run-locally)
[![desktop: Python + PySide6](doc/badges/desktop.svg)](#run-locally)
[![deploy: GitHub Pages](doc/badges/deploy.svg)](#github-pages)
[![access: No login](doc/badges/access.svg)](#features)

**[Features](#features) · [Quick start](#try-it) · [Languages](#languages) · [Deployment](#github-pages) · [Local development](#run-locally) · [Directory structure](#directory-structure)**

A vocabulary learning project for technical review, with a **GitHub Pages website** and a **native Python / Qt desktop application**. Open either edition to enter the student view, then switch to the teacher view without registering or signing in.

## Try it

| Edition | How to start |
| --- | --- |
| Online website | Open the website link in the repository's About section on Windows, Mac or a mobile browser |
| Online shortcuts | Download the online package from Releases; open `.url` on Windows or `.webloc` on Mac |
| Windows Qt desktop | Run `releases/windows/KETWordStudio.exe` from the full package, or download the desktop package |
| Windows local website | Run `releases/windows/KETWordStudioWeb.exe` from the full package, or download the Windows browser package |
| Mac local website | Install Python 3.10+ and run `python3 run_web.py` |
| Development preview | Install Node.js 20+, run `npm start`, and open the URL printed in the terminal |

Both editions include **178 words, 19 topics and 3 clearly labelled sample records**. Use **Reset demo data** to restore the initial demonstration.

The Releases page offers online shortcuts, a full project, source code, Windows Qt, Windows browser, Mac browser and static website packages. See the [download guide](releases/README.md) for requirements.

## Languages

The website, Qt application and documentation support **English**, **简体中文** and **繁体中文**. English is the default on first launch. Use the language buttons in the application sidebar; your choice is remembered on that browser or computer. Documentation links at the top of each page switch to the same document in another language.

Switching language preserves the current role, practice, answer draft and completed results. Interface labels, built-in topic names, validation messages and CSV headings follow the selected language. JSON field names remain stable for tools that consume the export. This is an English spelling exercise using Chinese meanings; the built-in Chinese prompts use traditional characters in the traditional Chinese interface. Teacher-entered content remains as entered.

## Features

- Students: random or topic-based spelling practice, mistake review, resume, word search, result trends, per-question details and JSON / CSV exports.
- Teachers: add, edit or disable words, set alternative accepted answers and inspect practice records from the student view.
- Role switching: each view displays its own navigation and shares the current demonstration data.
- Grading: deterministic comparison after Unicode NFKC normalization, case normalization and whitespace cleanup; accepted aliases are supported.
- History: practices store question snapshots, so later word edits cannot change an existing practice or result.

Student and teacher are demonstration views, not accounts or permission boundaries. Website data stays in the current browser; the desktop edition stores data in local SQLite. The two editions do not synchronize. The initial word bank is a demonstration set, not a complete official examination vocabulary list.

## Three-minute review

1. Student → Word practice → choose 3 questions → submit or skip → view the result.
2. Inspect Mistake review and Learning records, including per-question details and exports.
3. Teacher → Vocabulary management → add `robot / 机器人 / 科技`, with `a robot` as an accepted answer.
4. Return to Student and practise the new topic to check word creation and alias grading.
5. Switch between the three interface languages during a practice, then use Reset demo data when finished.

## GitHub Pages

The repository includes `.github/workflows/pages.yml`. Push the source to a public repository's `main` branch, select **Settings → Pages → Source → GitHub Actions**, and run **Deploy website** in Actions.

The workflow checks documentation links and website logic before deploying only `site/`. Python source, desktop executables, tests and documentation are not part of the website deployment. No application server, paid domain or API secret is needed.

For your own deployment, the URL follows `https://<username>.github.io/<repository>/`. The current demonstration URL is in the repository's About section. See [deployment instructions](doc/en/deployment.md) and [GitHub's Pages documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages).

## Run locally

The website needs no JavaScript dependency installation:

```bash
npm start
npm test
npm run check:docs
```

You can also preview the same site with Python:

```bash
python run_web.py
# On Mac: python3 run_web.py
```

The Python preview uses port 8765 by default. If occupied, use `python run_web.py --port 8766`. Browser data is isolated by origin, including the port. Keep the preview terminal open.

Run and build the Qt desktop edition on Windows:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.venv\Scripts\python.exe run_desktop.py
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe scripts\build_windows.py
.venv\Scripts\python.exe scripts\package_releases.py
```

Windows executables are built for Windows x64. The Mac browser package does not need Qt. No native macOS installation package is provided.

## Directory structure

```text
KETWordStudio/
├── site/                         # Independently deployable website
│   ├── app.js / engine.js        # Interface and domain rules
│   ├── i18n.js                  # Language selection and formatting
│   ├── locales/                 # Shared en, zh-CN and zh-HK catalogues
│   ├── data/words.json          # Shared initial word bank
│   └── index.html / style.css / icon.svg
├── ket_studio/                   # Native Qt application and SQLite service
│   ├── desktop.py / service.py / storage.py
│   ├── i18n.py                  # Reads the same catalogues; saves preferences
│   └── vocabulary.py / paths.py / web_server.py / assets/
├── doc/
│   ├── en/                      # English documentation
│   ├── zh-CN/                   # Simplified Chinese documentation
│   ├── zh-HK/                   # Traditional Chinese documentation
│   ├── badges/                  # Shared README badges
│   └── images/                  # Shared application screenshots
├── scripts/                     # Preview, build, package and documentation checks
├── tests/                       # JavaScript, Python, Qt and language checks
├── launchers/                   # Online shortcuts for Windows and Mac
├── releases/                    # Three-language download guides
│   ├── windows/                 # Executables, checksums and dependency licences
│   └── packages/                # Generated archives, excluded from Git
├── .github/workflows/pages.yml
├── run_desktop.py / run_web.py
├── Start-Desktop-Windows.bat / Start-Web-Windows.bat / Start-Web-Mac.command
├── package.json / pyproject.toml / requirements*.txt
├── THIRD_PARTY_NOTICES.md
└── README.md / README.zh-CN.md / README.zh-HK.md
```

Language catalogues and initial words each have one shared source for the website and Qt. Images and badges are shared across documentation languages. Build outputs, databases and caches stay out of Git. See [third-party notices](THIRD_PARTY_NOTICES.md).
