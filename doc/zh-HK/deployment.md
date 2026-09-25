# 部署說明

[English](../en/deployment.md) | [简体中文](../zh-CN/deployment.md) | **繁体中文**

GitHub Pages 為 `site/` 中的靜態網站提供 HTTPS 和 `github.io` 地址。自定義域名為可選項。Pages 不運行 Python；線上應用由 HTML、CSS、JavaScript、詞庫和三種語言資源組成。

## 發佈到 GitHub Pages

1. 創建公開倉庫，例如 `ket-word-studio`。
2. 將源碼推送到 `main`。`.gitignore` 排除 EXE、運行數據庫、虛擬環境、緩存及生成的壓縮包；Windows 程序作為 Release 附件上傳。
3. 在 **Settings → Pages → Build and deployment → Source** 選擇 **GitHub Actions**。
4. 在 **Actions → Deploy website → Run workflow** 啓動工作流；後續推送 `main` 會自動觸發。
5. 成功後從 Pages 設置或部署記錄複製實際地址。

以下命令僅用於新倉庫，執行前應確認遠程存在且沒有衝突內容：

```bash
git init -b main
git add .
git commit -m "Add KET Word Studio demonstration"
git remote add origin https://github.com/<username>/<repository>.git
git push -u origin main
```

當前演示入口見倉庫 About。自行部署的地址格式為 `https://<username>.github.io/<repository>/`。

## 工作流

`pages.yml` 檢出源碼，用 Node.js 檢查文檔鏈接並運行網站測試，再上傳及部署 `site/`。無需 `npm install` 或前端構建。只有部署任務具備 `pages: write` 和 `id-token: write` 權限。

## 發佈後檢查

在新的瀏覽器配置中訪問 HTTPS 地址，確認默認英語和學生頁面。點擊三個語言按鈕，切換後刷新確認偏好保留；完成練習並確認成績儲存；在教師頁面新增詞彙，然後從學生頁面按新主題練習。檢查控制枱沒有錯誤，`data/words.json` 和三份 `locales/*.json` 均能通過相對路徑加載。

Windows EXE 不屬於網站運行依賴，不應上傳到 Pages 發佈目錄。

## 構建發佈包

Windows 安裝 `requirements-dev.txt` 後執行：

```bash
python scripts/build_windows.py
python scripts/package_releases.py
```

構建腳本生成 `releases/windows/` 中的 Qt 和本地網站 EXE，並更新 SHA-256 清單。打包腳本核對 EXE 校驗值、檢查 ZIP 完整性並生成下載清單。默認輸出 `releases/packages/`，可用 `--output 路徑` 指定其他目錄。Git 源碼清單使用 `git ls-files`，打包前應暫存新增源碼及文檔。

各平台壓縮包默認打開英語 README，並提供兩種中文的切換鏈接。源碼包與完整包包含全部三語文檔。

## 官方參考

- [GitHub Pages 與支持的方案](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)
- [創建 Pages 網站](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site)
- [自定義 Actions 工作流](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)

[返回 README](../../README.zh-HK.md)
