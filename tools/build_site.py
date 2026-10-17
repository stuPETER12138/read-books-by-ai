#!/usr/bin/env python3
"""把整个仓库组装成一个 GitHub Pages 站点。

结构：
    站点根 index.html      —— 书籍汇总首页（本脚本生成）
    <分支名>/              —— 每个书籍分支用 mdBook 构建出的网页

约定：一个分支 = 一本书；分支根目录里有 book.toml 才算书籍。
`gh-pages`、`main` 以及没有 book.toml 的分支会被跳过。
"""

from __future__ import annotations

import argparse
import html
import shutil
import subprocess
import tempfile
import tomllib
from dataclasses import dataclass, field
from datetime import timedelta, timezone
from pathlib import Path

SKIP_BRANCHES = {"gh-pages", "main", "master"}
CST = timezone(timedelta(hours=8))


def git(*args: str, cwd: Path | None = None) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or f"git {' '.join(args)} failed")
    return proc.stdout


def remote_branches() -> list[str]:
    names = []
    for line in git("ls-remote", "--heads", "origin").splitlines():
        ref = line.split("\t")[-1].strip()
        if ref.startswith("refs/heads/"):
            names.append(ref[len("refs/heads/"):])
    return sorted(names)


@dataclass
class Book:
    branch: str
    title: str
    description: str = ""
    chapters: int = 0
    updated: str = ""
    error: str = ""
    extras: dict = field(default_factory=dict)


def build_book(branch: str, workdir: Path, out_root: Path) -> Book | None:
    worktree = workdir / branch
    git("worktree", "add", "--detach", "--force", str(worktree), f"origin/{branch}")

    try:
        config_path = worktree / "book.toml"
        if not config_path.is_file():
            print(f"[skip] {branch}: 没有 book.toml")
            return None

        config = tomllib.loads(config_path.read_text(encoding="utf-8"))
        meta = config.get("book", {})
        book = Book(
            branch=branch,
            title=str(meta.get("title") or branch).strip(),
            description=str(meta.get("description") or "").strip(),
        )

        summary = worktree / "src" / "SUMMARY.md"
        if summary.is_file():
            book.chapters = sum(
                1
                for line in summary.read_text(encoding="utf-8").splitlines()
                if line.lstrip().startswith("- [")
            )

        try:
            book.updated = git("log", "-1", "--format=%cs", cwd=worktree).strip()
        except RuntimeError:
            pass

        proc = subprocess.run(
            ["mdbook", "build"],
            cwd=worktree,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if proc.returncode != 0:
            lines = (proc.stderr or proc.stdout).strip().splitlines()
            book.error = lines[-1] if lines else "mdbook build 失败"
            print(f"[fail] {branch}: {book.error}")
            return book

        target = out_root / branch
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(worktree / "book", target)
        print(f"[ok]   {branch}: {book.title} ({book.chapters} 章) -> {target}")
        return book
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", str(worktree)],
                       capture_output=True, text=True)


def render(books: list[Book], repo: str, base_url: str) -> str:
    cards = []
    for book in books:
        classes = "card"
        meta = []
        if book.error:
            classes += " broken"
            meta.append("构建失败")
        if book.chapters:
            meta.append(f"{book.chapters} 个章节")
        if book.updated:
            meta.append(f"更新于 {book.updated}")

        href = f"{base_url}{book.branch}/" if not book.error else ""
        tag_open = (
            f'<a class="{classes}" href="{html.escape(href)}">'
            if href
            else f'<div class="{classes}">'
        )
        tag_close = "</a>" if href else "</div>"
        cards.append(
            f"""      {tag_open}
        <h2>{html.escape(book.title)}</h2>
        <p class="desc">{html.escape(book.description)}</p>
        <p class="meta">{' · '.join(html.escape(m) for m in meta)}</p>
        <span class="branch">{html.escape(book.branch)}</span>
      {tag_close}"""
        )

    body = "\n".join(cards) if cards else '      <p class="empty">还没有书籍分支。</p>'
    latest = max((b.updated for b in books if b.updated), default="")
    footer_note = f"最近更新 {html.escape(latest)}" if latest else "尚未发布"

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>读书记录 · {html.escape(repo)}</title>
<style>
  :root {{
    color-scheme: light dark;
    --bg: #f7f7f5; --fg: #1f2328; --muted: #6b7280;
    --card: #ffffff; --line: #e5e7eb; --accent: #2563eb;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{
      --bg: #16181d; --fg: #e6e6e6; --muted: #9aa4b2;
      --card: #1e2228; --line: #2c313a; --accent: #7aa2ff;
    }}
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; background: var(--bg); color: var(--fg);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
                 "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    line-height: 1.6;
  }}
  main {{ max-width: 920px; margin: 0 auto; padding: 56px 20px 72px; }}
  header h1 {{ font-size: 1.9rem; margin: 0 0 8px; letter-spacing: .01em; }}
  header p {{ margin: 0; color: var(--muted); }}
  .grid {{
    display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 16px; margin-top: 32px;
  }}
  .card {{
    display: flex; flex-direction: column; gap: 6px;
    padding: 18px 20px 16px; background: var(--card);
    border: 1px solid var(--line); border-radius: 12px;
    text-decoration: none; color: inherit;
    transition: transform .12s ease, border-color .12s ease, box-shadow .12s ease;
  }}
  a.card:hover {{
    transform: translateY(-2px); border-color: var(--accent);
    box-shadow: 0 6px 20px rgba(0, 0, 0, .08);
  }}
  .card h2 {{ font-size: 1.05rem; margin: 0; color: var(--accent); }}
  .card.broken h2 {{ color: #b91c1c; }}
  .card .desc {{ margin: 0; color: var(--muted); font-size: .9rem; }}
  .card .meta {{ margin: 4px 0 0; font-size: .8rem; color: var(--muted); }}
  .card .branch {{
    margin-top: 8px; font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    font-size: .75rem; color: var(--muted); opacity: .8;
  }}
  .empty {{ color: var(--muted); }}
  footer {{
    margin-top: 48px; padding-top: 16px; border-top: 1px solid var(--line);
    color: var(--muted); font-size: .85rem;
    display: flex; justify-content: space-between; gap: 12px; flex-wrap: wrap;
  }}
  footer a {{ color: var(--muted); }}
</style>
</head>
<body>
<main>
  <header>
    <h1>读书记录</h1>
    <p>共 {len(books)} 本书 · {footer_note}</p>
  </header>
  <div class="grid">
{body}
  </div>
  <footer>
    <span>由 GitHub Actions 自动生成</span>
    <a href="https://github.com/{html.escape(repo)}">github.com/{html.escape(repo)}</a>
  </footer>
</main>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default="")
    parser.add_argument("--base-url", default="/")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    if shutil.which("mdbook") is None:
        raise SystemExit("找不到 mdbook，请先安装（cargo install mdbook 或 actions-mdbook）")

    base = args.base_url if args.base_url.endswith("/") else args.base_url + "/"
    out_root = Path(args.out).resolve()
    out_root.mkdir(parents=True, exist_ok=True)

    books: list[Book] = []
    with tempfile.TemporaryDirectory(prefix="books-") as tmp:
        workdir = Path(tmp)
        for branch in remote_branches():
            if branch in SKIP_BRANCHES:
                continue
            book = build_book(branch, workdir, out_root)
            if book is not None:
                books.append(book)

    books.sort(key=lambda b: (b.updated, b.title), reverse=True)
    (out_root / "index.html").write_text(render(books, args.repo, base), encoding="utf-8")
    print(f"\n生成 {out_root / 'index.html'}，共 {len(books)} 本书")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
