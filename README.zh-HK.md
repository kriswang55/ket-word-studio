# KET Word Studio

[English](README.md) | [简体中文](README.zh-CN.md) | **繁体中文**

## 項目文檔

| 文檔入口 | 內容 |
| --- | --- |
| **[項目說明](doc/zh-HK/project-overview.md)** | 項目目標、功能範圍與演示方式 |
| **[使用說明](doc/zh-HK/user-guide.md)** | 學生練習、教師詞庫管理與數據操作 |
| **[架構設計](doc/zh-HK/architecture.md)** | 網站與 Qt 桌面端的結構、數據與判分邏輯 |
| **[部署說明](doc/zh-HK/deployment.md)** | GitHub Pages 發佈、本地啓動與構建 |
| **[驗收記錄](doc/zh-HK/verification.md)** | 自動測試、運行驗證與已知驗證邊界 |
| **[下載說明](releases/README.zh-HK.md)** | 在線快捷方式及各平台發佈包的選擇 |

[![version: 3.1.0](doc/badges/version.svg)](#體驗方式)
[![web: HTML + CSS + JavaScript](doc/badges/web.svg)](#本地運行)
[![desktop: Python + PySide6](doc/badges/desktop.svg)](#本地運行)
[![deploy: GitHub Pages](doc/badges/deploy.svg)](#github-pages-部署)
[![access: No login](doc/badges/access.svg)](#功能)

**[它做什麼](#功能) · [快速體驗](#體驗方式) · [在線部署](#github-pages-部署) · [本地啓動](#本地運行) · [目錄結構](#目錄) · [項目文檔](#項目文檔)**

用於技術評審的詞彙學習演示項目，包含 **GitHub Pages 網站**和 **Python / Qt 桌面程序**。打開即進入學生頁面，無需註冊或登錄，可隨時切換教師頁面。

## 體驗方式

| 方式 | 啓動方法 |
| --- | --- |
| 在線網站 | 從倉庫右側 About 中的網站入口訪問，支持 Windows、Mac 和移動設備瀏覽器 |
| 在線快捷方式 | 下載 Release 中的在線啓動包；Windows 雙擊 `.url`，Mac 雙擊 `.webloc` |
| Windows Qt 桌面版 | 雙擊 `releases/windows/KETWordStudio.exe` |
| Windows 本地網站 | 雙擊 `releases/windows/KETWordStudioWeb.exe` |
| Mac 本地網站 | 安裝 Python 3.10+，執行 `python3 run_web.py` |
| 開發預覽 | 安裝 Node.js 20+，執行 `npm start`，打開終端顯示的網址 |

網站與桌面版都內置 **178 個詞彙、19 個主題和 3 條明確標註的示例成績**。數據可通過界面的“重置演示數據”恢復。

在倉庫 **Releases** 中選擇在線快捷方式、完整包、源碼包、Windows Qt 桌面包、Windows 瀏覽器包、Mac 瀏覽器包或靜態網站包。各包用途和運行要求見 [下載說明](releases/README.zh-HK.md)。

## 語言切換

網站、Qt 桌面版與文檔均提供 **English / 简体中文 / 繁体中文**，首次啓動默認英語。點擊側邊欄的三個語言按鈕即可切換，當前語言會高亮；網站記住當前瀏覽器的選擇，Qt 在數據庫旁的 `preferences.json` 中儲存選擇。文檔頂部的鏈接會切換到同一篇文檔。

切換語言保留當前身份、練習進度、未提交的答案和判分結果。導航、內置主題、提示與 CSV 表頭隨語言變化，JSON 字段名保持穩定。這是根據中文釋義填寫英文的練習，繁體界面顯示內置釋義的繁體版本；教師自行輸入的內容保持原樣。

## 功能

- 學生：隨機拼寫測試、按主題抽題、錯題溫習、練習續接、詞彙搜索、成績趨勢、逐題詳情、JSON / CSV 導出。
- 教師：新增 / 編輯 / 停用詞彙、設置其他可接受答案、查看學生頁面產生的練習記錄。
- 身份切換：學生與教師分別展示對應導航；切換不會中斷未完成的練習。
- 判分：忽略大小寫、多餘空白和全角字符差異；採用詞條及其別名的確定性匹配。
- 歷史保護：練習儲存題目快照，編輯詞庫不會改變已開始練習的題目與成績。

此項目用於技術演示。學生和教師是界面模式，不是賬户或安全權限系統。網站數據只儲存在當前瀏覽器；桌面數據儲存在本機 SQLite，兩端不互相同步。初始詞庫為演示練習集，不代表完整官方考試詞表。

## 三分鐘評審路線

1. 學生頁面 → 詞彙練習 → 選擇 3 道題 → 提交或跳過 → 查看成績。
2. 打開錯題溫習和學習記錄，查看逐題判分與導出功能。
3. 切換教師頁面 → 詞庫管理 → 新增 `robot / 機器人 / 科技`，填寫其他可接受答案 `a robot`。
4. 返回學生頁面，按“科技”主題練習，驗證新增詞條及別名判分。
5. 使用“重置演示數據”恢復初始狀態。

## GitHub Pages 部署

項目已提供 `.github/workflows/pages.yml`。將源碼推送至公開倉庫的 `main` 分支，在 **Settings → Pages → Source** 中選擇 **GitHub Actions**，然後在 Actions 頁面運行 **Deploy website**。

工作流先檢查文檔鏈接並執行網站邏輯測試，再僅發佈 `site/`。Python 源碼、桌面程序、測試文件和文檔不會進入網站發佈目錄。無需服務器、付費域名或環境密鑰。

部署到自己的倉庫時，地址格式為 `https://<username>.github.io/<repository>/`，請替換為自己的 GitHub 用户名和倉庫名。當前演示入口見倉庫右側 About。

詳細步驟見 [部署說明](doc/zh-HK/deployment.md)。GitHub Free 支持公開倉庫的 Pages；參見 [GitHub 官方說明](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)。

## 本地運行

網站無需安裝 JavaScript 依賴：

```bash
npm start
npm test
npm run check:docs
```

也可僅用 Python 預覽同一套網站：

```bash
python run_web.py
# Mac 使用 python3 run_web.py
```

默認端口為 8765。端口被佔用時使用 `python run_web.py --port 8766`。瀏覽器數據按網站來源隔離，換端口會使用另一份數據。啓動終端需要保持運行。

Qt 桌面版源碼運行與打包：

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.venv\Scripts\python.exe run_desktop.py
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe scripts\build_windows.py
.venv\Scripts\python.exe scripts\package_releases.py
```

Windows EXE 在 Windows x64 上構建。Mac 可直接使用在線網站；本地預覽腳本無需 Qt。沒有提供 macOS 原生安裝包。

## 目錄

```text
KETWordStudio/
├── site/                         # 可獨立部署的網站
│   ├── app.js / engine.js        # 頁面與業務規則
│   ├── i18n.js / locales/        # 共用 en、zh-CN、zh-HK 語言資源
│   ├── data/words.json          # 共用初始詞庫
│   └── index.html / style.css / icon.svg
├── ket_studio/                   # Qt 界面、SQLite 服務與本地網站啓動器
│   └── i18n.py                  # 讀取共用語言資源並儲存偏好
├── doc/
│   ├── en/                      # 英語文檔
│   ├── zh-CN/                   # 簡體中文文檔
│   ├── zh-HK/                   # 繁體中文文檔
│   └── badges/ / images/        # 各語言共用的徽章與截圖
├── scripts/                     # 預覽、構建、打包和文檔檢查
├── tests/                       # JavaScript、Python、Qt 與語言測試
├── launchers/                   # 在線快捷方式
├── releases/                    # 三語下載說明
│   ├── windows/                 # EXE、校驗值與第三方許可證
│   └── packages/                # 自動生成的壓縮包，不提交 Git
├── .github/workflows/pages.yml
├── run_desktop.py / run_web.py
├── Start-Desktop-Windows.bat / Start-Web-Windows.bat / Start-Web-Mac.command
├── package.json / pyproject.toml / requirements*.txt
├── THIRD_PARTY_NOTICES.md
└── README.md / README.zh-CN.md / README.zh-HK.md
```

網站與 Qt 共用一份初始詞庫和語言資源；不同語言的文檔共用圖片和徽章。構建結果、運行數據庫與緩存不進入 Git。參見[第三方說明](doc/zh-HK/third-party-notices.md)。
