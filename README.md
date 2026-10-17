# 燃气轮机发电机组控制系统

《燃气轮机发电机组控制系统》学习笔记，使用 [mdBook](https://rust-lang.github.io/mdBook/) 构建。

在线阅读：<https://stuPETER12138.github.io/read-books-by-ai/gas-turbine-generator-control/>

站点首页（全部书籍）：<https://stuPETER12138.github.io/read-books-by-ai/>

## 目录结构

```
book.toml                      # mdBook 配置（title / description 会显示在站点首页）
src/SUMMARY.md                 # 目录
src/*.md                       # 各章正文
.github/workflows/notify-site.yml   # 推送本分支后通知 main 重建整站
```

## 本地构建

```bash
cargo install mdbook --version 0.4.40
mdbook serve --open   # 或 mdbook build
```

## 发布方式

整站由 `main` 分支的 `Build and deploy site` 工作流统一构建：

1. 检出 `main`，拉取所有 `origin/*` 分支；
2. `tools/build_site.py` 对每个含 `book.toml` 的分支执行 `mdbook build`，输出到 `_site/<分支名>/`；
3. 生成 `_site/index.html` 汇总首页；
4. 通过 `upload-pages-artifact` + `deploy-pages` 发布到 GitHub Pages。

本分支（`gas-turbine-generator-control`）只负责内容；推送后 `notify-site.yml` 发出
`repository_dispatch`（`book-updated`），触发 `main` 重新构建整站。

> 新增书籍时，`[output.html] site-url` 要写成 `/read-books-by-ai/<分支名>/`，
> 并用 `git switch -c <分支名> main` 从 `main` 创建分支，才能自动带上通知工作流。

## 内容说明

本笔记用于学习控制原理，不替代具体机型的运行规程、制造商逻辑图、保护定值和现场安全管理制度。
