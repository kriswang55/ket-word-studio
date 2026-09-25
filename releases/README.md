# 发布包选择

当前发布版本：**v3.0.0**。在仓库的 **Releases** 页面下载对应文件，解压后使用。

| 文件 | 用途 | 运行条件 |
| --- | --- | --- |
| `KETWordStudio-Online-3.0.0.zip` | 在线启动快捷方式，双击进入 GitHub Pages | Windows 用 `.url`，Mac 用 `.webloc`；联网即可 |
| `Open-KET-Online.url` / `Open-KET-Online.webloc` | 可单独下载的在线快捷方式 | 浏览器，无需 Python |
| `KETWordStudio-3.0.0.zip` | 完整项目，含源码、文档和两种 Windows EXE | Windows 可直接运行；其他平台可用网站源码 |
| `KETWordStudio-Source-3.0.0.zip` | 开发、评审与重新构建 | 网站 Node.js 20+ 或 Python 3.10+；Qt 需安装依赖 |
| `KETWordStudio-Windows-Qt-3.0.0.zip` | 原生 Qt 桌面程序 | Windows x64，无需安装 Python |
| `KETWordStudio-Windows-Web-3.0.0.zip` | 双击启动本地网站 | Windows x64，无需安装 Python |
| `KETWordStudio-Mac-Web-3.0.0.zip` | Mac 本地浏览器演示 | Python 3.10+；不需要 Qt |
| `KETWordStudio-Website-3.0.0.zip` | 独立静态网站，用于托管或本地 HTTP 预览 | 现代浏览器；不能直接双击 HTML |
| `KETWordStudio.exe` | 单文件桌面入口 | Windows x64 |
| `KETWordStudioWeb.exe` | 单文件本地网站入口 | Windows x64 |
| `SHA256SUMS-v3.0.0.txt` | 下载完整性校验 | 可用系统 SHA-256 工具核对 |

Mac 浏览器包是 Python 静态预览启动器和网站文件，不是原生 `.app`。访问已部署网站无需下载或安装任何程序。

网站与桌面均免登录，可切换学生与教师页面，分别使用浏览器本地存储和桌面 SQLite 数据库。

## 重建发布包

先在 Windows 中执行 `python scripts/build_windows.py` 生成 EXE，再执行 `python scripts/package_releases.py`。默认输出至 `releases/packages/`，可用 `--output 路径` 指定目标目录。打包脚本验证 ZIP 完整性，并生成 SHA-256 清单。
