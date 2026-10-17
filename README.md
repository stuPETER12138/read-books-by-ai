# 燃气轮机发电机组控制系统

《燃气轮机发电机组控制系统》学习笔记，使用 [mdBook](https://rust-lang.github.io/mdBook/) 构建。

在线阅读：<https://stuPETER12138.github.io/read-books-by-ai/gas-turbine-generator-control/>

## 目录结构

```
book.toml                  # mdBook 配置
src/SUMMARY.md             # 目录
src/*.md                   # 各章正文
.github/workflows/deploy.yml  # 推送到本分支后自动构建并发布到 gh-pages
```

## 本地构建

```bash
cargo install mdbook --version 0.4.40
mdbook serve --open   # 或 mdbook build
```

## 发布方式

推送到 `gas-turbine-generator-control` 分支后，GitHub Actions 会：

1. 安装 mdBook 0.4.40；
2. 执行 `mdbook build`；
3. 将 `book/` 发布到 `gh-pages` 分支的 `gas-turbine-generator-control/` 目录，并保留其他书籍目录。

> 仓库需在 Settings → Pages 中把源设置为 `gh-pages` 分支的 `/ (root)` 目录。
> 每本书使用「仓库内一个分支 + gh-pages 下一个子目录」的方式共存。

## 内容说明

本笔记用于学习控制原理，不替代具体机型的运行规程、制造商逻辑图、保护定值和现场安全管理制度。
