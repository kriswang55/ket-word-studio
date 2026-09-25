# Deployment

**English** | [简体中文](../zh-CN/deployment.md) | [繁体中文](../zh-HK/deployment.md)

GitHub Pages hosts the static files in `site/` with HTTPS and a `github.io` URL. A custom domain is optional. Pages does not execute Python. The online application consists of HTML, CSS, JavaScript, the word bank and three local language catalogues.

## Publish with GitHub Pages

1. Create a public GitHub repository, for example `ket-word-studio`.
2. Push this project's source to `main`. `.gitignore` excludes executables, runtime databases, virtual environments, caches and generated archives. Upload Windows programs as Release assets.
3. Select **Settings → Pages → Build and deployment → Source → GitHub Actions**.
4. Open **Actions → Deploy website → Run workflow**. Later pushes to `main` trigger the workflow automatically.
5. After success, copy the actual URL from Pages settings or the deployment record.

For a new repository only, after confirming that the remote exists and contains no conflicting content:

```bash
git init -b main
git add .
git commit -m "Add KET Word Studio demonstration"
git remote add origin https://github.com/<username>/<repository>.git
git push -u origin main
```

The current demonstration is available from the website link in the repository's About section. Your own URL follows `https://<username>.github.io/<repository>/`.

## Workflow

`pages.yml` checks out the source, runs documentation-link checks and JavaScript tests with Node.js, uploads `site/`, and deploys it. No `npm install` or frontend build is required. Only the deployment job has `pages: write` and `id-token: write` permissions.

## Verify the deployment

Open the HTTPS URL in a fresh browser profile and confirm English and Student are the defaults. Switch to Simplified Chinese and Traditional Chinese, then refresh and verify that the selected language remains. Complete a practice and check its saved result. Add a teacher word and practise its topic from Student. Check for console errors and verify that `data/words.json` and all three `locales/*.json` files load through relative URLs.

Windows executables are not website dependencies and should not be uploaded to the Pages directory.

## Build releases

On Windows, install `requirements-dev.txt`, then run:

```bash
python scripts/build_windows.py
python scripts/package_releases.py
```

The builder produces the Qt desktop and local-browser executables in `releases/windows/` and updates their SHA-256 manifest. The packager checks those hashes, verifies ZIP integrity, and generates download checksums. Its default output is `releases/packages/`; use `--output PATH` for another directory. Stage newly added source files before packaging from a Git checkout, because the source inventory uses `git ls-files`.

Each platform package opens with an English README and links to Simplified and Traditional Chinese instructions. The source and full packages include the complete three-language documentation.

## Official references

- [GitHub Pages and supported plans](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)
- [Creating a Pages site](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site)
- [Custom Actions workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)

[Back to README](../../README.md)
