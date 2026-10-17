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

发布前会查询 `github-pages` 环境的部署分支白名单：当前 ref 不在名单内时只构建、不发布，
并以 warning 提示——这样分支切换期间也不会出现红色失败。

## 新增一本书

```bash
git switch -c my-new-book main
# 放入 book.toml 与 src/，设置 [output.html] site-url = "/read-books-by-ai/my-new-book/"
# 从别的书籍分支拷贝 .github/workflows/notify-site.yml
git push -u origin my-new-book
```

## 仓库设置

- **Settings → Pages → Build and deployment → Source**：**GitHub Actions**（已设置，不再使用 `gh-pages`）。
- **Settings → General → Default branch**：建议设为 `main`。默认分支会自动加入
  `github-pages` 环境的部署白名单，`main` 的构建就能直接发布、定时任务也才会生效。
  目前默认分支仍是 `gas-turbine-generator-control`，所以 `main` 的推送只构建不发布，
  由书籍分支的推送或手动运行来触发发布。
