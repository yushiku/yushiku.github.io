"""Build preview/index.html and preview/index_ja.html from data/*.yaml.

    uv run --with jinja2 --with pyyaml build.py                  # default -> preview/
    uv run --with jinja2 --with pyyaml build.py --theme journal  # -> preview_journal/
    uv run --with jinja2 --with pyyaml build.py --theme all      # default + every theme
    uv run --with jinja2 --with pyyaml build.py --site           # publish: write into the site root

--site writes index.html / index_ja.html (CRLF, as the published files are) and
home.css into the site root, with the journal-sidebar theme. style.css in the site
root is left alone because job.html and other pages still use it.

A theme is themes/<name>/style.css plus an optional themes/<name>/page.html.j2.
A theme template extends "base/page.html.j2" (= templates/page.html.j2) and
overrides its blocks; without one, templates/page.html.j2 is used as is.

data/*.yaml is the single source of content. Every item can carry
  lang: both | en | ja      (default: both)
and either `text` (same on both pages) or `text_en` / `text_ja`.
"""
from __future__ import annotations

import argparse
import shutil
from itertools import groupby
from pathlib import Path

import yaml
from jinja2 import (ChoiceLoader, Environment, FileSystemLoader, PrefixLoader,
                    StrictUndefined)

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUT = ROOT / "preview"
THEMES = ROOT / "themes"
# In the repository this folder is <site>/_src; in the work tree it sits three levels
# below homepage/ next to site/. Images are read from SITE.
SITE = ROOT.parent if ROOT.name == "_src" else ROOT.parent.parent.parent / "site"
SITE_THEME = "journal-sidebar"
SITE_CSS = "home.css"

ASSETS = ["20250327_full.jpg", "mailaddr.png",
          "tw.png", "fb.png", "li.png", "ss.png", "sd.png", "gs.png", "oi.png"]


def load(name: str):
    return yaml.safe_load((DATA / f"{name}.yaml").read_text(encoding="utf-8"))


def make_env(lang: str, theme: str | None = None) -> Environment:
    base = FileSystemLoader(ROOT / "templates")
    loaders = [FileSystemLoader(THEMES / theme)] if theme else []
    loaders += [base, PrefixLoader({"base": base})]
    env = Environment(loader=ChoiceLoader(loaders),
                      autoescape=False,  # data holds trusted HTML fragments
                      undefined=StrictUndefined,
                      trim_blocks=True, lstrip_blocks=True,
                      keep_trailing_newline=True)

    def shown(items):
        return [i for i in items if i.get("lang", "both") in ("both", lang)]

    def pick(item, field="text"):
        if isinstance(item, dict):
            if f"{field}_{lang}" in item:
                return item[f"{field}_{lang}"]
            if field in item:
                return item[field]
            if lang in item:
                return item[lang]
        return item

    def by_year(items, key="year"):
        """Stable sort by year (newest first), then group. Returns
        [(year, start_number, [items])] so <ol start=..> keeps one running count."""
        def y(i):
            v = i[key]
            return int(str(v)[:4])
        ordered = sorted(items, key=lambda i: -y(i))
        groups, n = [], 1
        for year, grp in groupby(ordered, key=y):
            grp = list(grp)
            groups.append((year, n, grp))
            n += len(grp)
        return groups

    env.filters.update(shown=shown, pick=pick, by_year=by_year)
    env.globals.update(lang=lang)
    return env


def stats(ctx, lang: str):
    """Counts for the highlights strip, computed from the data (not hardcoded)."""
    def n(items):
        return len([i for i in items if i.get("lang", "both") in ("both", lang)])
    secs = {s["id"]: s for s in ctx["publications"]["sections"]}
    labels = {
        "en": ["Journal papers", "Intl. conference papers", "Invited talks", "Awards"],
        "ja": ["論文誌（査読付き）", "国際会議（査読付き）", "講演・講師", "受賞"],
    }[lang]
    nums = [n(secs["journal"]["items"]), n(secs["intl_conf"]["items"]),
            n(ctx["talks"]["items"]), n(ctx["awards"]["items"])]
    anchors = ["papers", "papers", "talks", "awards"]
    return [dict(num=a, label=b, anchor=c) for a, b, c in zip(nums, labels, anchors)]


def build(ctx, theme: str | None, site: bool = False) -> None:
    if site:
        theme, out = SITE_THEME, SITE
    else:
        out = ROOT / f"preview_{theme}" if theme else OUT
    css = THEMES / theme / "style.css" if theme else ROOT / "static" / "style.css"
    if not css.exists():
        raise SystemExit(f"no such theme: {theme} ({css})")
    out.mkdir(exist_ok=True)
    for lang, fname in (("en", "index.html"), ("ja", "index_ja.html")):
        html = make_env(lang, theme).get_template("page.html.j2").render(
            **ctx, stats=stats(ctx, lang), theme=theme or "default",
            css=SITE_CSS if site else "style.css")
        (out / fname).write_text(html, encoding="utf-8",
                                 newline="\r\n" if site else "\n")
        print("wrote", out / fname)
    css_name = SITE_CSS if site else "style.css"
    shutil.copy2(css, out / css_name)
    theme_assets = (css.parent / "assets") if theme else None
    n = 0
    for a in ASSETS:
        src = theme_assets / a if theme_assets and (theme_assets / a).exists() else SITE / a
        if src.resolve() != (out / a).resolve():
            shutil.copy2(src, out / a)
            n += 1
    print("copied", css_name, "and", n, "images")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--theme", help="themes/<name> to use; 'all' = default + every theme")
    ap.add_argument("--site", action="store_true",
                    help=f"write the published pages into {SITE} with the {SITE_THEME} theme")
    args = ap.parse_args()
    ctx = {name: load(name) for name in
           ["profile", "slides", "education", "positions", "roles", "society",
            "reviewer", "publications", "books", "talks", "grants", "awards", "media"]}
    if args.site:
        build(ctx, None, site=True)
        return
    if args.theme == "all":
        themes = [None] + sorted(d.name for d in THEMES.iterdir() if (d / "style.css").exists())
    else:
        themes = [args.theme]
    for t in themes:
        build(ctx, t)


if __name__ == "__main__":
    main()
