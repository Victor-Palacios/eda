"""Build a static GitHub Pages site from the day notebooks.

Renders the committed (already-executed) notebooks to self-contained HTML with
a large-code-font stylesheet so the code is readable on a projector — GitHub's
own .ipynb viewer renders code cells too small and strips injected CSS.

This does NOT re-execute or regenerate notebooks; it renders whatever outputs
are committed (we keep those fresh via notebooks/_build_notebooks.py + a local
execute pass). Output goes to _site/ which CI uploads to Pages.

Usage: python build_site.py
"""
from __future__ import annotations

import base64
import html as html_lib
import mimetypes
import re
from pathlib import Path

import nbformat
from nbconvert import HTMLExporter

ROOT = Path(__file__).resolve().parent
SITE = ROOT / "_site"

# (day folder name, human label) — add a tuple per future day.
DAYS = [
    ("Data Cleaning and Exploratory Data Analysis", "Data Cleaning & EDA"),
]

# External links to surface on the index right after a given notebook (keyed by
# notebook stem). Each entry is (link label, URL) and opens in a new tab.
EXTRA_LINKS = {
    "02_simpsons_paradox": [
        (
            "Simpson's Paradox Slides",
            "https://docs.google.com/presentation/d/1lhOHUUkFfWmnUTOGvgq7HLS0oOyRznayzgkHb8Jaafg/edit?slide=id.p1#slide=id.p1",
        ),
    ],
}

# Code (input + text output) is driven by --jp-code-font-size in the nbconvert
# `lab` template; we lift it to a 30px floor and scale prose/headers above it so
# the visual hierarchy stays headers > prose > code.
#
# Mobile: wide cells (code, text output, dataframes) scroll horizontally inside
# their own box instead of stretching the page (overflow-x: auto is inert on
# desktop where nothing overflows), images shrink to the screen, and a
# max-width media query steps every font size down so prose fits a phone. The
# in-notebook markdown wrapper divs carry inline font-size/margin styles, so
# the mobile overrides for those need !important.
CUSTOM_CSS = """
<style>
:root {
  --jp-code-font-size: 30px;
  --jp-code-presentation-font-size: 30px;
}
.jp-RenderedText pre,
.jp-OutputArea-output pre { font-size: 30px; line-height: 1.45; }
.jp-RenderedHTMLCommon p,
.jp-RenderedHTMLCommon li { font-size: 32px; line-height: 1.6; }
.jp-RenderedHTMLCommon h1 { font-size: 56px; }
.jp-RenderedHTMLCommon h2 { font-size: 46px; }
.jp-RenderedHTMLCommon h3 { font-size: 40px; }
.jp-RenderedHTMLCommon h4 { font-size: 36px; }
.jp-RenderedHTMLCommon table,
.dataframe, .dataframe th, .dataframe td { font-size: 30px; }
body { max-width: 1500px; margin: 0 auto; }

.jp-Cell-inputWrapper .highlight,
.jp-OutputArea-output,
.jp-RenderedHTMLCommon { overflow-x: auto; }
.jp-RenderedHTMLCommon img { max-width: 100%; height: auto; }

@media (max-width: 700px) {
  :root {
    --jp-code-font-size: 15px;
    --jp-code-presentation-font-size: 15px;
  }
  /* The lab theme wraps output text (white-space: pre-wrap), which mangles
     aligned tables on a narrow screen; keep output lines intact and let the
     overflow-x: auto container above make them swipeable instead. */
  .jp-RenderedText pre,
  .jp-OutputArea-output pre { font-size: 15px; white-space: pre; }
  .jp-RenderedHTMLCommon p,
  .jp-RenderedHTMLCommon li { font-size: 18px; }
  .jp-RenderedHTMLCommon h1 { font-size: 30px; }
  .jp-RenderedHTMLCommon h2 { font-size: 25px; }
  .jp-RenderedHTMLCommon h3 { font-size: 21px; }
  .jp-RenderedHTMLCommon h4 { font-size: 19px; }
  .jp-RenderedHTMLCommon table,
  .dataframe, .dataframe th, .dataframe td { font-size: 14px; }
  .jp-RenderedHTMLCommon div[style] { font-size: 18px !important; }
  .jp-RenderedHTMLCommon div[style*="margin-top"] {
    margin-top: 80px !important;
  }
}
</style>
"""


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def inline_local_images(html: str, nbdir: Path) -> str:
    """Replace `<img src="../images/foo.png">` with a base64 data URI.

    nbconvert's embed_images only inlines http/attachment images, not local
    file references, so we do it here to keep each page self-contained.
    """
    def repl(match: re.Match) -> str:
        rel = match.group(1)
        path = (nbdir / rel).resolve()
        if not path.is_file():
            return match.group(0)
        mime = mimetypes.guess_type(path.name)[0] or "image/png"
        data = base64.b64encode(path.read_bytes()).decode("ascii")
        return f'src="data:{mime};base64,{data}"'

    return re.sub(r'src="(\.\./images/[^"]+)"', repl, html)


def notebook_functions(nb) -> list[str]:
    """Function names credited in the notebook's Takeaway cell.

    Collects the backticked names from every 'Functions ...' / 'From the ...'
    line so the index can show what each notebook teaches.
    """
    for cell in nb.cells:
        if cell.cell_type != "markdown" or "## Takeaway" not in "".join(cell.source):
            continue
        names: list[str] = []
        for line in "".join(cell.source).splitlines():
            if re.match(r"\s*(Functions|From the)", line):
                names.extend(n for n in re.findall(r"`([^`]+)`", line)
                             if n not in names)
        return names
    return []


def notebook_title(nb) -> str:
    """First H1 in the notebook, falling back to the file stem."""
    for cell in nb.cells:
        if cell.cell_type == "markdown":
            for line in "".join(cell.source).splitlines():
                m = re.match(r"#\s+(.*)", line.strip())
                if m:
                    return m.group(1).strip()
    return ""


def build() -> None:
    exporter = HTMLExporter(embed_images=True)
    SITE.mkdir(exist_ok=True)
    sections = []

    for day_name, label in DAYS:
        day_dir = ROOT / day_name
        nbdir = day_dir / "notebooks"
        slug = slugify(label)
        out_dir = SITE / slug
        out_dir.mkdir(parents=True, exist_ok=True)

        items = []
        for ipynb in sorted(nbdir.glob("[0-9]*.ipynb")):
            nb = nbformat.read(ipynb, as_version=4)
            # resources path lets embed_images resolve ../images/... references.
            html, _ = exporter.from_notebook_node(
                nb, resources={"metadata": {"path": str(nbdir)}}
            )
            html = inline_local_images(html, nbdir)
            html = html.replace("</head>", CUSTOM_CSS + "</head>", 1)
            out = out_dir / f"{ipynb.stem}.html"
            out.write_text(html)
            title = notebook_title(nb) or ipynb.stem
            items.append((f"{slug}/{out.name}", title, notebook_functions(nb)))
            print(f"Wrote {out}")
            for label_text, url in EXTRA_LINKS.get(ipynb.stem, []):
                items.append((url, label_text, []))

        def render_link(href: str, title: str, fns: list[str]) -> str:
            attrs = ' target="_blank" rel="noopener"' if href.startswith("http") else ""
            line = f'    <li><a href="{href}"{attrs}>{html_lib.escape(title)}</a>'
            if fns:
                codes = " ".join(f"<code>{html_lib.escape(fn)}</code>" for fn in fns)
                line += f'\n      <div class="fns">{codes}</div>'
            return line + "</li>"

        links = "\n".join(render_link(href, title, fns) for href, title, fns in items)
        sections.append(f"  <h2>{html_lib.escape(label)}</h2>\n  <ul>\n{links}\n  </ul>")

    index = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pandas EDA Through Bias Stories</title>
<style>
  body {{ font-family: system-ui, sans-serif; max-width: 900px; margin: 40px auto;
          padding: 0 20px; font-size: 22px; line-height: 1.6; color: #222; }}
  h1 {{ font-size: 40px; }}
  h2 {{ font-size: 30px; margin-top: 1.4em; }}
  a {{ color: #1565c0; text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  ul {{ list-style: none; padding-left: 0; }}
  li {{ margin: 0.4em 0 1em; }}
  .fns {{ margin-top: 0.15em; line-height: 1.9; }}
  .fns code {{ font-size: 15px; color: #444; background: #f2f2f2;
               border-radius: 4px; padding: 1px 7px; white-space: nowrap; }}
</style>
</head>
<body>
  <h1>Pandas EDA Through Bias Stories</h1>
  <p>Beginner-friendly Pandas EDA taught through bias stories. Rendered with a
     large code font for classroom display.</p>
{chr(10).join(sections)}
</body>
</html>
"""
    (SITE / "index.html").write_text(index)
    print(f"Wrote {SITE / 'index.html'}")


if __name__ == "__main__":
    build()
