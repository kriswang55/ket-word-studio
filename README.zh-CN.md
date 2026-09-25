# KET Word Studio

[English](README.md) | **简体中文** | [繁体中文](README.zh-HK.md)

## 项目文档

| 文档入口 | 内容 |
| --- | --- |
| **[项目说明](doc/zh-CN/project-overview.md)** | 项目目标、功能范围与演示方式 |
| **[使用说明](doc/zh-CN/user-guide.md)** | 学生练习、教师词库管理与数据操作 |
| **[架构设计](doc/zh-CN/architecture.md)** | 网站与 Qt 桌面端的结构、数据与判分逻辑 |
| **[部署说明](doc/zh-CN/deployment.md)** | GitHub Pages 发布、本地启动与构建 |
| **[验收记录](doc/zh-CN/verification.md)** | 自动测试、运行验证与已知验证边界 |
| **[下载说明](releases/README.zh-CN.md)** | 在线快捷方式及各平台发布包的选择 |

[![version: 3.1.0](doc/badges/version.svg)](#体验方式)
[![web: HTML + CSS + JavaScript](doc/badges/web.svg)](#本地运行)
[![desktop: Python + PySide6](doc/badges/desktop.svg)](#本地运行)
[![deploy: GitHub Pages](doc/badges/deploy.svg)](#github-pages-部署)
[![access: No login](doc/badges/access.svg)](#功能)

**[它做什么](#功能) · [快速体验](#体验方式) · [在线部署](#github-pages-部署) · [本地启动](#本地运行) · [目录结构](#目录) · [项目文档](#项目文档)**

用于技术评审的单词学习演示项目，包含 **GitHub Pages 网站**和 **Python / Qt 桌面程序**。打开即进入学生页面，无需注册或登录，可随时切换教师页面。

## 体验方式

| 方式 | 启动方法 |
| --- | --- |
| 在线网站 | 从仓库右侧 About 中的网站入口访问，支持 Windows、Mac 和移动设备浏览器 |
| 在线快捷方式 | 下载 Release 中的在线启动包；Windows 双击 `.url`，Mac 双击 `.webloc` |
| Windows Qt 桌面版 | 双击 `releases/windows/KETWordStudio.exe` |
| Windows 本地网站 | 双击 `releases/windows/KETWordStudioWeb.exe` |
| Mac 本地网站 | 安装 Python 3.10+，执行 `python3 run_web.py` |
| 开发预览 | 安装 Node.js 20+，执行 `npm start`，打开终端显示的网址 |

网站与桌面版都内置 **178 个词汇、19 个主题和 3 条明确标注的示例成绩**。数据可通过界面的“重置演示数据”恢复。

在仓库 **Releases** 中选择在线快捷方式、完整包、源码包、Windows Qt 桌面包、Windows 浏览器包、Mac 浏览器包或静态网站包。各包用途和运行要求见 [下载说明](releases/README.zh-CN.md)。

## 语言切换

网站、Qt 桌面版与文档均提供 **English / 简体中文 / 繁体中文**，首次启动默认英语。点击侧边栏的三个语言按钮即可切换，当前语言会高亮；网站记住当前浏览器的选择，Qt 在数据库旁的 `preferences.json` 中保存选择。文档顶部的链接会切换到同一篇文档。

切换语言保留当前身份、练习进度、未提交的答案和判分结果。导航、内置主题、提示与 CSV 表头随语言变化，JSON 字段名保持稳定。这是根据中文释义填写英文的练习，繁体界面显示内置释义的繁体版本；教师自行输入的内容保持原样。

## 功能

- 学生：随机拼写测试、按主题抽题、错题复习、练习续接、词汇搜索、成绩趋势、逐题详情、JSON / CSV 导出。
- 教师：新增 / 编辑 / 停用词汇、设置其他可接受答案、查看学生页面产生的练习记录。
- 身份切换：学生与教师分别展示对应导航；切换不会中断未完成的练习。
- 判分：忽略大小写、多余空白和全角字符差异；采用词条及其别名的确定性匹配。
- 历史保护：练习保存题目快照，编辑词库不会改变已开始练习的题目与成绩。

此项目用于技术演示。学生和教师是界面模式，不是账户或安全权限系统。网站数据只保存在当前浏览器；桌面数据保存在本机 SQLite，两端不互相同步。初始词库为演示练习集，不代表完整官方考试词表。

## 三分钟评审路线

1. 学生页面 → 单词练习 → 选择 3 道题 → 提交或跳过 → 查看成绩。
2. 打开错题复习和学习记录，查看逐题判分与导出功能。
3. 切换教师页面 → 词库管理 → 添加 `robot / 机器人 / 科技`，填写其他可接受答案 `a robot`。
4. 返回学生页面，按“科技”主题练习，验证新增词条及别名判分。
5. 使用“重置演示数据”恢复初始状态。

## GitHub Pages 部署

项目已提供 `.github/workflows/pages.yml`。将源码推送至公开仓库的 `main` 分支，在 **Settings → Pages → Source** 中选择 **GitHub Actions**，然后在 Actions 页面运行 **Deploy website**。

工作流先检查文档链接并执行网站逻辑测试，再仅发布 `site/`。Python 源码、桌面程序、测试文件和文档不会进入网站发布目录。无需服务器、付费域名或环境密钥。

部署到自己的仓库时，地址格式为 `https://<username>.github.io/<repository>/`，请替换为自己的 GitHub 用户名和仓库名。当前演示入口见仓库右侧 About。

详细步骤见 [部署说明](doc/zh-CN/deployment.md)。GitHub Free 支持公开仓库的 Pages；参见 [GitHub 官方说明](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)。

## 本地运行

网站无需安装 JavaScript 依赖：

```bash
npm start
npm test
npm run check:docs
```

也可仅用 Python 预览同一套网站：

```bash
python run_web.py
# Mac 使用 python3 run_web.py
```

默认端口为 8765。端口被占用时使用 `python run_web.py --port 8766`。浏览器数据按网站来源隔离，换端口会使用另一份数据。启动终端需要保持运行。

Qt 桌面版源码运行与打包：

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.venv\Scripts\python.exe run_desktop.py
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe scripts\build_windows.py
.venv\Scripts\python.exe scripts\package_releases.py
```

Windows EXE 在 Windows x64 上构建。Mac 可直接使用在线网站；本地预览脚本无需 Qt。没有提供 macOS 原生安装包。

## 目录

```text
KETWordStudio/
├── site/                         # 可独立部署的网站
│   ├── app.js / engine.js        # 页面与业务规则
│   ├── i18n.js / locales/        # 共用 en、zh-CN、zh-HK 语言资源
│   ├── data/words.json          # 共用初始词库
│   └── index.html / style.css / icon.svg
├── ket_studio/                   # Qt 界面、SQLite 服务与本地网站启动器
│   └── i18n.py                  # 读取共用语言资源并保存偏好
├── doc/
│   ├── en/                      # 英语文档
│   ├── zh-CN/                   # 简体中文文档
│   ├── zh-HK/                   # 繁体中文文档
│   └── badges/ / images/        # 各语言共用的徽章与截图
├── scripts/                     # 预览、构建、打包和文档检查
├── tests/                       # JavaScript、Python、Qt 与语言测试
├── launchers/                   # 在线快捷方式
├── releases/                    # 三语下载说明
│   ├── windows/                 # EXE、校验值与第三方许可证
│   └── packages/                # 自动生成的压缩包，不提交 Git
├── .github/workflows/pages.yml
├── run_desktop.py / run_web.py
├── Start-Desktop-Windows.bat / Start-Web-Windows.bat / Start-Web-Mac.command
├── package.json / pyproject.toml / requirements*.txt
├── THIRD_PARTY_NOTICES.md
└── README.md / README.zh-CN.md / README.zh-HK.md
```

网站与 Qt 共用一份初始词库和语言资源；不同语言的文档共用图片和徽章。构建结果、运行数据库与缓存不进入 Git。参见[第三方说明](doc/zh-CN/third-party-notices.md)。
