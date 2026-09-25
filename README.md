# KET Word Studio

[![version: 3.0.0](doc/badges/version.svg)](#体验方式)
[![web: HTML + CSS + JavaScript](doc/badges/web.svg)](#本地运行)
[![desktop: Python + PySide6](doc/badges/desktop.svg)](#本地运行)
[![deploy: GitHub Pages](doc/badges/deploy.svg)](#github-pages-部署)
[![access: No login](doc/badges/access.svg)](#功能)

**[它做什么](#功能) · [快速体验](#体验方式) · [在线部署](#github-pages-部署) · [本地启动](#本地运行) · [目录结构](#目录) · [项目文档](#文档)**

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

在仓库 **Releases** 中选择在线快捷方式、完整包、源码包、Windows Qt 桌面包、Windows 浏览器包、Mac 浏览器包或静态网站包。各包用途和运行要求见 [下载说明](releases/README.md)。

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

工作流先执行网站逻辑测试，再仅发布 `site/`。Python 源码、桌面程序、测试文件和文档不会进入网站发布目录。无需服务器、付费域名或环境密钥。

发布后的地址格式为 `https://<username>.github.io/<repository>/`，请替换为自己的 GitHub 用户名和仓库名。这是地址示例，不表示已经发布。

详细步骤见 [部署说明](doc/deployment.md)。GitHub Free 支持公开仓库的 Pages；参见 [GitHub 官方说明](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)。

## 本地运行

网站无需安装 JavaScript 依赖：

```bash
npm start
npm test
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
├── site/                         # 独立、可直接发布的网站
│   ├── index.html
│   ├── app.js                    # 页面与交互
│   ├── engine.js                 # 练习、词库、统计、浏览器持久化
│   ├── style.css
│   ├── icon.svg
│   └── data/words.json           # 两端共享的初始词库
├── ket_studio/                   # Python 桌面应用
│   ├── desktop.py               # Qt 界面
│   ├── service.py               # 练习与词库规则
│   ├── storage.py               # SQLite 事务与表结构
│   ├── vocabulary.py            # 词库校验与归一化
│   ├── paths.py                 # 数据目录
│   ├── web_server.py            # 静态网站本地预览
│   └── assets/app.ico
├── scripts/                     # 预览、构建、打包
├── launchers/                   # Windows / Mac 在线网站快捷方式
├── tests/                       # JavaScript / Python / Qt 测试
├── doc/                         # 项目、操作、架构、部署与验收文档
├── .github/workflows/pages.yml   # GitHub Pages 自动发布
├── releases/windows/            # Windows EXE、校验值、第三方许可证
├── run_desktop.py
├── run_web.py
├── Start-Desktop-Windows.bat
├── Start-Web-Windows.bat
├── Start-Web-Mac.command
├── package.json
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── THIRD_PARTY_NOTICES.md
└── README.md
```

## 文档

源码可直接从目录运行。文档入口：[项目说明](doc/project-overview.md) · [使用说明](doc/user-guide.md) · [架构设计](doc/architecture.md) · [验收记录](doc/verification.md)。
