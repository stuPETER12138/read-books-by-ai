# read-books-by-ai 站点

<https://stuPETER12138.github.io/read-books-by-ai/>

一本书 = 一个分支。`main` 分支只放站点首页与构建脚本，书本内容在各自的书籍分支里。

```
main
├── tools/build_site.py        # 生成首页 + 用 mdBook 构建所有书籍分支
├── .github/workflows/site.yml # 构建并部署到 GitHub Pages
└── README.md

<书籍分支>
├── book.toml                  # mdBook 配置（title / description 会显示在首页）
├── src/SUMMARY.md
└── src/*.md
```

## 构建流程

`site.yml` 在以下情况运行：

- `main` 分支有推送；
- 任意书籍分支通过 `repository_dispatch`（`book-updated`）通知；
- 每 6 小时定时检查一次；
- 手动 `workflow_dispatch`。

执行内容：

1. 检出 `main`，拉取全部 `origin/*` 分支；
2. `tools/build_site.py` 对每个含 `book.toml` 的分支执行 `mdbook build`，输出到 `_site/<分支名>/`；
3. 生成 `_site/index.html` 汇总首页；
4. `upload-pages-artifact` + `deploy-pages` 发布到 GitHub Pages。

## 新增一本书

```bash
git switch -c my-new-book main
# 放入 book.toml 与 src/，并设置 [output.html] site-url = "/read-books-by-ai/my-new-book/"
git push -u origin my-new-book
```

书籍分支里带上 `.github/workflows/notify-site.yml`，推送后会触发 `main` 重新构建整站。

## 仓库设置（一次性）

- **Settings → General → Default branch**：设为 `main`（定时任务与 `repository_dispatch` 只认默认分支的工作流）。
- **Settings → Pages → Build and deployment → Source**：选 **GitHub Actions**（不再使用 `gh-pages` 分支）。
