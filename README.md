# read-books-by-ai 站点

<https://stuPETER12138.github.io/read-books-by-ai/>

一本书 = 一个分支。`main` 只放站点首页与构建脚本，书本内容在各自的书籍分支里。

```
main
├── tools/build_site.py        # 生成首页 + 用 mdBook 构建所有书籍分支
├── .github/workflows/site.yml # 构建并部署到 GitHub Pages
└── README.md

<书籍分支>
├── book.toml                  # mdBook 配置（title / description 显示在首页）
├── src/SUMMARY.md
├── src/*.md
└── .github/workflows/notify-site.yml   # 推送后复用 main 的工作流重建整站
```

## 构建流程

`site.yml` 在以下情况运行：

- `main` 分支有推送；
- 书籍分支通过 `workflow_call` 复用（`notify-site.yml` 里 `uses: .../site.yml@main`）；
- 每 6 小时定时检查（仅默认分支生效）；
- 手动 `workflow_dispatch`。

执行内容：

1. 检出 `main`，拉取全部 `origin/*` 分支；
2. `tools/build_site.py` 对每个含 `book.toml` 的分支执行 `mdbook build`，输出到 `_site/<分支名>/`；
3. 生成 `_site/index.html` 汇总首页；
4. `upload-pages-artifact` + `deploy-pages` 发布到 GitHub Pages。

部署任务没有绑定 `github-pages` 环境：该环境的部署分支白名单只允许旧默认分支，
会把 `main` 挡在发布之外；解绑后任何触发该工作流的 ref 都能发布。

## 新增一本书

```bash
git switch -c my-new-book main
# 放入 book.toml 与 src/，设置 [output.html] site-url = "/read-books-by-ai/my-new-book/"
# 从别的书籍分支拷贝 .github/workflows/notify-site.yml
git push -u origin my-new-book
```

## 仓库设置

- **Settings → Pages → Build and deployment → Source**：**GitHub Actions**（已设置，不再使用 `gh-pages`）。
- **Settings → General → Default branch**：`main`（已设置）。定时任务、`workflow_dispatch` 都从默认分支运行。
- 如果以后想把部署重新绑定到 `github-pages` 环境做审批/分支保护，记得同时把 `main`
  加入该环境的 *Deployment branches*，否则发布会被拦截。
