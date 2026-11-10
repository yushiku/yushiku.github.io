# Source of index.html / index_ja.html

The two top pages are generated from the YAML files in `data/`. Edit `data/*.yaml`,
then run from this folder:

    uv run --with jinja2 --with pyyaml build.py --site

This writes `../index.html`, `../index_ja.html` (CRLF) and `../home.css`, and copies the
theme's icons from `themes/journal-sidebar/assets/`. `../style.css` is not touched; other
pages still use it.

Each item in `data/*.yaml` can carry `lang: both | en | ja` (default `both`) and either
`text` or `text_en` / `text_ja`.
