#!/usr/bin/env python3
"""生成 GitHub Pages 站点根目录的书籍汇总首页。

每本书位于独立分支（分支名即 URL 子路径），本脚本扫描所有含 book.toml 的分支，
读取书名、简介、章节数和最近提交日期，输出一个静态 index.html。
"""

from __future__ import annotations

import argparse
import html
import subprocess
import tomllib
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

SKIP_BRANCHES = {"gh-pages", "main", "master"}
CST = timezone(timedelta(hours=8))


def git(*args: str) -> bytes:
    proc = subprocess.run(["git", *args], capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.decode("utf-8", "replace").strip())
    return proc.stdout


def list_branches() -> list[str]:
    raw = git("ls-remote", "--heads", "origin").decode()
    names = []
    for line in raw.splitlines():
        ref = line.split("\t")[-1].strip()
        if ref.startswith("refs/heads/"):
            names.append(ref[len("refs/heads/"):])
    return sorted(names)


@dataclass
class Book:
    branch: str
    title: str
    description: str
    chapters: int
    updated: str

    @property
    def sort_key(self) -> tuple[str, str]:
        return (self.updated, self.title)


def read_book(branch: str) -> Book | None:
    try:
        git("fetch", "--depth=1", "origin", f"refs/heads/{branch}")
        config = tomllib.loads(git("show", "FETCH_HEAD:book.toml").decode("utf-8"))
    except Exception:
        return None

    book = config.get("book", {})
    title = str(book.get("title") or branch).strip()
    description = str(book.get("description") or "").strip()

    chapters = 0
    try:
        summary = git("show", "FETCH_HEAD:src/SUMMARY.md").decode("utf-8")
        chapters = sum(
            1 for line in summary.splitlines() if line.lstrip().startswith("- [")
        )
    except Exception:
        pass

    try:
        updated = git("log", "-1", "--format=%cs", "FETCH_HEAD").decode().strip()
    except Exception:
        updated = ""

    return Book(branch, title, description, chapters, updated)


def render(books: list[Book], repo: str, base_url: str) -> str:
    cards = []
    for book in books:
        href = f"{base_url}{book.branch}/"
        meta = []
        if book.chapters:
            meta.append(f"{book.chapters} 个章节")
        if book.updated:
            meta.append(f"更新于 {book.updated}")
        meta_html = " · ".join(html.escape(m) for m in meta)
        desc = html.escape(book.description) if book.description else ""
        cards.append(
            f"""      <a class="card" href="{html.escape(href)}">
        <h2>{html.escape(book.title)}</h2>
        <p class="desc">{desc}</p>
        <p class="meta">{meta_html}</p>
        <span class="branch">{html.escape(book.branch)}</span>
      </a>"""
        )

    body = "\n".join(cards) if cards else (
        '      <p class="empty">还没有可展示的书籍分支。</p>'
    )
    latest = max((b.updated for b in books if b.updated), default="")
    updated_at = (
        f"最近更新 {html.escape(latest)}" if latest else datetime.now(CST).strftime("%Y-%m-%d")
    )
    count = len(books)

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>读书记录 · {html.escape(repo)}</title>
<style>
  :root {{
    color-scheme: light dark;
    --bg: #f7f7f5;
    --fg: #1f2328;
    --muted: #6b7280;
    --card: #ffffff;
    --line: #e5e7eb;
    --accent: #2563eb;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{
      --bg: #16181d;
      --fg: #e6e6e6;
      --muted: #9aa4b2;
      --card: #1e2228;
      --line: #2c313a;
      --accent: #7aa2ff;
    }}
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    background: var(--bg);
    color: var(--fg);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
                 "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    line-height: 1.6;
  }}
  main {{ max-width: 880px; margin: 0 auto; padding: 56px 20px 72px; }}
  header h1 {{ font-size: 1.9rem; margin: 0 0 8px; letter-spacing: .01em; }}
  header p {{ margin: 0; color: var(--muted); }}
  .grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 16px;
    margin-top: 32px;
  }}
  .card {{
    display: flex;
    flex-direction: column;
    gap: 6px;
    padding: 18px 20px 16px;
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 12px;
    text-decoration: none;
    color: inherit;
    transition: transform .12s ease, border-color .12s ease, box-shadow .12s ease;
  }}
  .card:hover {{
    transform: translateY(-2px);
    border-color: var(--accent);
    box-shadow: 0 6px 20px rgba(0, 0, 0, .08);
  }}
  .card h2 {{ font-size: 1.05rem; margin: 0; color: var(--accent); }}
  .card .desc {{ margin: 0; color: var(--muted); font-size: .9rem; }}
  .card .meta {{ margin: 4px 0 0; font-size: .8rem; color: var(--muted); }}
  .card .branch {{
    margin-top: 8px;
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    font-size: .75rem;
    color: var(--muted);
    opacity: .8;
  }}
  .empty {{ color: var(--muted); }}
  footer {{
    margin-top: 48px;
    padding-top: 16px;
    border-top: 1px solid var(--line);
    color: var(--muted);
    font-size: .85rem;
    display: flex;
    justify-content: space-between;
    gap: 12px;
    flex-wrap: wrap;
  }}
  footer a {{ color: var(--muted); }}
</style>
</head>
<body>
<main>
  <header>
    <h1>读书记录</h1>
    <p>共 {count} 本书 · {updated_at}</p>
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

    books = []
    for branch in list_branches():
        if branch in SKIP_BRANCHES:
            continue
        book = read_book(branch)
        if book is not None:
            books.append(book)

    books.sort(key=lambda b: b.sort_key, reverse=True)

    base = args.base_url
    if not base.endswith("/"):
        base += "/"

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(books, args.repo, base), encoding="utf-8")
    print(f"generated {out} with {len(books)} book(s): {[b.branch for b in books]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
