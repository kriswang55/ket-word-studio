# User guide

**English** | [简体中文](../zh-CN/user-guide.md) | [繁体中文](../zh-HK/user-guide.md)

## Open and switch views

The website and desktop application open directly in the student view. Choose **Teacher** on the website or **Switch to teacher** in the desktop sidebar to inspect teacher functions. Return to Student to practise. No account or password is needed.

Student navigation: Learning overview, Word practice, Wordbook, Mistake review and Learning records. Teacher navigation: Management overview, Vocabulary management and Practice records.

## Choose a language

Use the three language buttons in the sidebar: **English**, **简体中文** or **繁体中文**. First launch defaults to English. The website remembers the choice in the current browser; Qt saves `preferences.json` beside its database. Changing language preserves the selected role, active question, typed answer and feedback. Resetting demo data keeps the language preference.

Interface messages, built-in topics and CSV headings follow the selected language. Built-in Chinese meanings use traditional characters in the traditional Chinese interface. The exercise still tests English spelling. New or edited teacher content is kept as entered. JSON uses stable field names for programmatic access.

## Practice

1. Open Word practice and choose Random practice or Mistake review.
2. Set the question count and topic. Only enabled words are used, up to the available count.
3. Enter the English answer for the Chinese meaning, then Submit answer or press Enter. Skipping counts as incorrect.
4. Read the feedback, continue to the next question, and view the result after the final answer.

Grading ignores case, surrounding or repeated whitespace and full-width character differences. It does not correct spelling or accept synonyms absent from the aliases. Submitted answers cannot be edited.

You can resume an unfinished practice after leaving or closing the program. An explicitly ended incomplete practice is excluded from scores and the mistake list.

## Manage vocabulary

In Vocabulary management, enter English, Chinese meaning and a topic. Separate additional accepted answers with semicolons. Select an existing topic or type a new one. Duplicate English entries are rejected, including case and full-width variants.

Disable a word to hide it from future practices and the student wordbook. Re-enable it to restore availability. Active practices and historical results use the question content saved when the practice began.

## Inspect and export

Learning records / Practice records show every question's meaning, correct spelling, submitted answer and result. JSON includes per-question details. CSV contains summaries and prefixes text that could be interpreted as a spreadsheet formula.

Mean accuracy is the arithmetic mean of practice scores. Overall accuracy is total correct answers divided by total answered questions. One correct 1-question practice and an incorrect 3-question practice therefore produce 50% mean accuracy and 25% overall accuracy.

## Data and reset

The website uses localStorage, normally retained after closing. Clearing site data or using private browsing can remove it. Browsers and URL origins, including ports, have separate data. Visitors cannot see each other's work. Other tabs in the same browser show an update notice; avoid editing simultaneously because there is no cross-tab transaction lock.

Desktop database locations:

- Windows: `%LOCALAPPDATA%\KETWordStudio\demo.sqlite3`.
- Mac: `~/Library/Application Support/KETWordStudio/demo.sqlite3`.
- Linux: `$XDG_DATA_HOME/KETWordStudio/demo.sqlite3`, or `~/.local/share/KETWordStudio/demo.sqlite3` when the variable is unset.

Use `--data-dir PATH` for a separate desktop data directory.

**Reset demo data** asks for confirmation, then removes added words and practices and restores the initial vocabulary and 3 sample records. It affects only the current browser or desktop data directory. Exports are not full backups; importing or restoring them is not supported.

## Troubleshooting

- Do not open HTML directly: modules and word-bank loading require HTTP / HTTPS. Use the hosted URL or a local preview command.
- If port 8765 is occupied, close the existing preview or use `--port 8766`.
- If saving fails, check browser storage permissions and available storage.
- If mistake review has no words, choose All topics or check that the relevant words are enabled.
- Website and desktop records differ because the editions do not synchronize.

[Back to README](../../README.md)
