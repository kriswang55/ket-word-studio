# 發佈包選擇

[English](README.md) | [简体中文](README.zh-CN.md) | **繁体中文**

當前發佈版本：**v3.1.0**。在倉庫的 **Releases** 頁面下載對應文件，解壓後使用。

| 文件 | 用途 | 運行條件 |
| --- | --- | --- |
| `KETWordStudio-Online-3.1.0.zip` | 在線啓動快捷方式，雙擊進入 GitHub Pages | Windows 用 `.url`，Mac 用 `.webloc`；聯網即可 |
| `Open-KET-Online.url` / `Open-KET-Online.webloc` | 可單獨下載的在線快捷方式 | 瀏覽器，無需 Python |
| `KETWordStudio-3.1.0.zip` | 完整項目，含源碼、文檔和兩種 Windows EXE | Windows 可直接運行；其他平台可用網站源碼 |
| `KETWordStudio-Source-3.1.0.zip` | 開發、評審與重新構建 | 網站 Node.js 20+ 或 Python 3.10+；Qt 需安裝依賴 |
| `KETWordStudio-Windows-Qt-3.1.0.zip` | 原生 Qt 桌面程序 | Windows x64，無需安裝 Python |
| `KETWordStudio-Windows-Web-3.1.0.zip` | 雙擊啓動本地網站 | Windows x64，無需安裝 Python |
| `KETWordStudio-Mac-Web-3.1.0.zip` | Mac 本地瀏覽器演示 | Python 3.10+；不需要 Qt |
| `KETWordStudio-Website-3.1.0.zip` | 獨立靜態網站，用於託管或本地 HTTP 預覽 | 現代瀏覽器；不能直接雙擊 HTML |
| `KETWordStudio.exe` | 單文件桌面入口 | Windows x64 |
| `KETWordStudioWeb.exe` | 單文件本地網站入口 | Windows x64 |
| `SHA256SUMS-v3.1.0.txt` | 下載完整性校驗 | 可用系統 SHA-256 工具核對 |

Mac 瀏覽器包是 Python 靜態預覽啓動器和網站文件，不是原生 `.app`。訪問已部署網站無需下載或安裝任何程序。

網站與桌面均免登錄，可切換學生與教師頁面，分別使用瀏覽器本地存儲和桌面 SQLite 數據庫。

## 重建發佈包

先在 Windows 中執行 `python scripts/build_windows.py` 生成 EXE，再執行 `python scripts/package_releases.py`。默認輸出至 `releases/packages/`，可用 `--output 路徑` 指定目標目錄。打包腳本驗證 ZIP 完整性，並生成 SHA-256 清單。

網站和桌面首次打開默認英語，使用三個按鈕切換語言。每個壓縮包包含英語 README 和兩種中文說明。

[返回 README](../README.zh-HK.md)
