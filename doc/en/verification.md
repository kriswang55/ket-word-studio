# Verification record

**English** | [简体中文](../zh-CN/verification.md) | [繁体中文](../zh-HK/verification.md)

Validation date: 2026-09-25. Version: 3.1.0.

## Automated checks

| Scope | Result |
| --- | --- |
| JavaScript domain logic and localization | 18 passed |
| Python service, HTTP preview, localization and Qt widgets | 23 passed |
| Total | 41 passed |

The existing tests cover initialization without accounts, sample markers, word creation / editing / disabling, duplicate validation, role constraints, sampling, normalization, aliases, submission retries, resume, snapshots, mistake removal, abandonment, weighted statistics, JSON / CSV exports, formula escaping, storage failures, reset and visitor isolation.

Localization checks cover identical catalogue keys and placeholders, English defaults, Traditional Chinese display, invalid locale handling, preference write failures, data isolation and localized CSV headings. Qt widget tests switch languages with an unsubmitted answer, after feedback and after the final question, verifying the same practice and result remain.

Python tests also cover concurrent duplicate submission, preserving damaged databases, static resource access and directory boundaries. The original Qt workflow opens the word editor, saves a word, switches views, starts a practice and grades a correct answer.

Reproduce the checks with:

```bash
npm test
npm run check:docs
python -m pytest -q
```

Python tests use `requirements-dev.txt` and temporary data directories. Website tests use isolated memory storage. The documentation checker verifies language links, local files and heading anchors.

## Runtime verification

- Windows Qt: student and teacher screens render with native widgets; screenshots are in `doc/images/`.
- Windows executables: desktop and local-browser variants are launched with isolated test data or a dedicated local preview.
- Browser: English default, all three language options, topic labels, form labels, validation feedback and saved language choice are inspected.
- Active practice: a typed `SMALL` answer survives language switching, grades correctly, and a two-question result remains 50% after another language change.
- Student and teacher navigation remain separate. Language switching does not introduce accounts or duplicate learning data.
- Root and repository-subpath hosting are supported. Website resources use relative URLs.
- Online shortcuts use valid Windows `.url` and Mac `.webloc` formats and target the deployed Pages address.

The deployed website is linked from the repository's About section. Repeat the HTTPS checks in [Deployment](deployment.md) after publication.

## Validation limits

Testing was performed on Windows. There has been no acceptance test on physical macOS or Safari, and no native macOS installation package is claimed. The website has narrow-screen layouts, but a complete mobile-device compatibility matrix has not been tested.

## Deliverables

Source, two Windows executables, dependency declarations, build and packaging scripts, automated tests, three-language Markdown documentation and screenshots. Archives exclude runtime databases, caches, virtual environments and build scratch files. Executable checksums are in `releases/windows/SHA256SUMS.txt`.

[Back to README](../../README.md)
