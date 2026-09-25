# 部署说明

[English](../en/deployment.md) | **简体中文** | [繁体中文](../zh-HK/deployment.md)

GitHub Pages 为 `site/` 中的静态网站提供 HTTPS 和 `github.io` 地址。自定义域名为可选项。Pages 不运行 Python；线上应用由 HTML、CSS、JavaScript、词库和三种语言资源组成。

## 发布到 GitHub Pages

1. 创建公开仓库，例如 `ket-word-studio`。
2. 将源码推送到 `main`。`.gitignore` 排除 EXE、运行数据库、虚拟环境、缓存及生成的压缩包；Windows 程序作为 Release 附件上传。
3. 在 **Settings → Pages → Build and deployment → Source** 选择 **GitHub Actions**。
4. 在 **Actions → Deploy website → Run workflow** 启动工作流；后续推送 `main` 会自动触发。
5. 成功后从 Pages 设置或部署记录复制实际地址。

以下命令仅用于新仓库，执行前应确认远程存在且没有冲突内容：

```bash
git init -b main
git add .
git commit -m "Add KET Word Studio demonstration"
git remote add origin https://github.com/<username>/<repository>.git
git push -u origin main
```

当前演示入口见仓库 About。自行部署的地址格式为 `https://<username>.github.io/<repository>/`。

## 工作流

`pages.yml` 检出源码，用 Node.js 检查文档链接并运行网站测试，再上传及部署 `site/`。无需 `npm install` 或前端构建。只有部署任务具备 `pages: write` 和 `id-token: write` 权限。

## 发布后检查

在新的浏览器配置中访问 HTTPS 地址，确认默认英语和学生页面。点击三个语言按钮，切换后刷新确认偏好保留；完成练习并确认成绩保存；在教师页面添加词汇，然后从学生页面按新主题练习。检查控制台没有错误，`data/words.json` 和三份 `locales/*.json` 均能通过相对路径加载。

Windows EXE 不属于网站运行依赖，不应上传到 Pages 发布目录。

## 构建发布包

Windows 安装 `requirements-dev.txt` 后执行：

```bash
python scripts/build_windows.py
python scripts/package_releases.py
```

构建脚本生成 `releases/windows/` 中的 Qt 和本地网站 EXE，并更新 SHA-256 清单。打包脚本核对 EXE 校验值、检查 ZIP 完整性并生成下载清单。默认输出 `releases/packages/`，可用 `--output 路径` 指定其他目录。Git 源码清单使用 `git ls-files`，打包前应暂存新增源码及文档。

各平台压缩包默认打开英语 README，并提供两种中文的切换链接。源码包与完整包包含全部三语文档。

## 官方参考

- [GitHub Pages 与支持的方案](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)
- [创建 Pages 网站](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site)
- [自定义 Actions 工作流](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)

[返回 README](../../README.zh-CN.md)
