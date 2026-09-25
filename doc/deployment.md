# GitHub Pages 部署

GitHub Free 可为公开仓库免费托管静态网站。Pages 提供 HTTPS 和 `github.io` 地址；自定义域名是可选项。Pages 不执行 Python，所以线上发布的是 `site/` 中独立运行的 HTML、CSS、JavaScript 和词库文件。

## 发布步骤

1. 使用 GitHub 账号 `kriswang55` 创建公开仓库，例如 `ket-word-studio`。
2. 将本项目源码推送到 `main` 分支。`.gitignore` 已排除 EXE、运行数据库、虚拟环境和缓存；Windows 程序可以单独作为 Release 附件上传。
3. 在仓库 **Settings → Pages → Build and deployment → Source** 选择 **GitHub Actions**。
4. 打开 **Actions → Deploy website → Run workflow**；之后每次推送到 `main` 会自动触发。
5. 工作流成功后，在 Pages 设置或部署记录中复制实际网站地址。

示例命令，执行前确认远程仓库存在且没有需要保留的同名内容：

```bash
git init -b main
git add .
git commit -m "Add KET Word Studio demonstration"
git remote add origin https://github.com/kriswang55/ket-word-studio.git
git push -u origin main
```

该仓库名对应的预期地址是 `https://kriswang55.github.io/ket-word-studio/`。文档中的地址是配置示例，只有 Pages 部署成功后才可对外提交。

## 工作流

`pages.yml` 检出源码，使用 Node.js 运行网站单元测试，然后上传 `site/` 并部署。无需 `npm install` 或前端构建。只有部署任务具有 `pages: write` 与 `id-token: write` 权限。

## 发布后验收

用新的浏览器窗口访问实际 HTTPS 地址，确认默认学生页；完成一次练习后刷新，核对成绩保存；切换教师页添加词汇后，在学生页按新主题出题。检查浏览器控制台无加载错误，并确认 `site/data/words.json` 可通过相对路径加载。

Windows EXE 不属于 Pages 网站运行依赖，无需上传到 Pages 发布目录。

## 官方参考

- [GitHub Pages 与免费方案](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)
- [创建站点与静态语言限制](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site)
- [自定义 Actions 发布工作流](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
