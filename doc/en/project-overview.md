# Project overview

**English** | [简体中文](../zh-CN/project-overview.md) | [繁体中文](../zh-HK/project-overview.md)

KET Word Studio is a vocabulary-learning technical demonstration for academic project review and postgraduate applications. Reviewers can inspect the complete workflow from vocabulary maintenance and question sampling to grading, mistake review and statistics, without signing in.

## Scope and use

The student view provides practice, word search, mistake review and results. The teacher view provides vocabulary management and practice records. Both views share the current demonstration data and are selected from the sidebar.

The online website is statically hosted. Each reviewer works independently in their own browser. The native Qt edition uses SQLite to demonstrate Python application organization, widget events and transactional persistence.

## Core features

| Module | Behaviour |
| --- | --- |
| Vocabulary | 178 initial words, 19 topics; add, edit, disable and accept aliases |
| Sampling | Select one topic or all words without replacement; use the available count when fewer words exist |
| Grading | NFKC normalization, case normalization, whitespace cleanup and accepted-answer matching |
| Progress | Save each submitted answer; resume unfinished practice after reopening |
| Mistakes | Review words whose latest completed answer was incorrect; remove after a later correct completed answer |
| Statistics | Practice and question counts, weighted overall accuracy, mean accuracy, highest / lowest scores and trends |
| Export | Per-question JSON and practice-summary CSV |
| Reset | Restore the original word bank and 3 sample results |
| Languages | English by default, with Simplified and Traditional Chinese, shared catalogues and persistent preferences |

The three sample results are 40%, 60% and 80%, each containing 5 questions. The interface and exports label their source. They are demonstration data, not evidence of learning outcomes.

## Design decisions

No accounts are required, reducing review setup. Local data isolation keeps visitors from overwriting each other's work. The browser edition needs no running Python server when hosted on GitHub Pages; the desktop application runs independently with equivalent practice rules.

The project does not implement authentication, cross-device synchronization, real class management, a cloud database or AI semantic grading. Role switching selects a view and is not a security boundary.

All application and documentation languages use the codes `en`, `zh-CN` and `zh-HK`. A language change does not create a second copy of learning data. Teacher-authored content remains unchanged; the spelling exercise still asks for English answers to Chinese meanings.

[Back to README](../../README.md)
