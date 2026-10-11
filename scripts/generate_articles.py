import json
import html
import re
from pathlib import Path
from urllib.parse import quote
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "מאמרים"
OUTPUT = ROOT / "articles"
SITE = "https://isragays.github.io"

OUTPUT.mkdir(exist_ok=True)


def escape(value):
    return html.escape(str(value or ""), quote=True)


def clean_html(value):
    """Remove potentially unsafe elements and attributes."""
    text = str(value or "")

    text = re.sub(
        r"<(script|style|iframe|object|embed|form|svg)\b[^>]*>.*?</\1\s*>",
        "",
        text,
        flags=re.I | re.S,
    )
    text = re.sub(
        r"<(script|style|iframe|object|embed|form|svg)\b[^>]*\/?>",
        "",
        text,
        flags=re.I | re.S,
    )
    text = re.sub(r"\s+on[a-z]+\s*=\s*(\"[^\"]*\"|'[^']*'|[^\s>]+)", "", text, flags=re.I)
    text = re.sub(r"\s+(href|src)\s*=\s*(['\"])\s*(?:javascript|data):.*?\2", "", text, flags=re.I | re.S)

    return text


def article_html(data, filename):
    title = escape(data.get("title", "כתבה"))
    description = escape(data.get("description", ""))
    date = escape(data.get("date", ""))
    category = escape(data.get("category", ""))
    body = clean_html(data.get("body", ""))

    image = str(data.get("image") or "")
    if image.startswith("/") and not image.startswith("//"):
        image = SITE + image
    if not image.startswith(("https://", "http://")):
        image = ""

    image_tag = (
        f'<img class="cover" src="{escape(image)}" alt="{title}">'
        if image else ""
    )
    og_image = (
        f'<meta property="og:image" content="{escape(image)}">'
        if image else ""
    )

    url = f"{SITE}/articles/{quote(filename)}.html"

    return f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} | ישראגייז</title>
<meta name="description" content="{description}">
<meta name="robots" content="index,follow">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{url}">
{og_image}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Assistant:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box}}
body{{margin:0;background:#091322;color:#f5f6fa;font-family:Assistant,Arial,sans-serif;line-height:1.85}}
header{{background:#101e33;padding:22px;text-align:center;border-bottom:1px solid #a88b52}}
header a{{color:#e4c789;text-decoration:none;font-size:27px;font-weight:800}}
main{{max-width:820px;margin:35px auto;padding:0 20px}}
h1{{font-size:clamp(30px,6vw,48px);line-height:1.3;margin:16px 0}}
.subtitle{{font-size:21px;color:#cbd3df}}
.meta{{color:#d7bd85;margin:18px 0}}
.cover{{width:100%;max-height:470px;object-fit:cover;border-radius:16px;margin:20px 0}}
.content{{font-size:20px;overflow-wrap:anywhere}}
.content img{{max-width:100%;height:auto}}
.content a{{color:#e4c789}}
.content h2,.content h3{{color:#e4c789;line-height:1.4}}
.back{{display:inline-block;margin:35px 0;color:#e4c789}}
footer{{text-align:center;padding:30px;color:#aab5c5}}
</style>
</head>
<body>
<header><a href="/">ישראגייז 🇮🇱 🏳️‍🌈</a></header>
<main>
<article>
<div class="meta">{category} {date}</div>
<h1>{title}</h1>
<p class="subtitle">{description}</p>
{image_tag}
<div class="content">{body}</div>
</article>
<a class="back" href="/magazine.html">← חזרה למגזין</a>
</main>
<footer>ישראגייז — הבית של הגייז בישראל</footer>
</body>
</html>"""


urls = [SITE + "/", SITE + "/magazine.html"]

for source in sorted(SOURCE.glob("*.json")):
    try:
        data = json.loads(source.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            continue

        filename = source.stem
        output = OUTPUT / f"{filename}.html"
        output.write_text(article_html(data, filename), encoding="utf-8")

        urls.append(f"{SITE}/articles/{quote(filename)}.html")
        print(f"Generated: {output.name}")

    except (OSError, ValueError, TypeError) as error:
        print(f"Error processing {source.name}: {error}")
        raise

ET.register_namespace("", "http://www.sitemaps.org/schemas/sitemap/0.9")
namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"
root = ET.Element(f"{{{namespace}}}urlset")

for url in urls:
    item = ET.SubElement(root, f"{{{namespace}}}url")
    ET.SubElement(item, f"{{{namespace}}}loc").text = url

tree = ET.ElementTree(root)
ET.indent(tree, space="  ")
tree.write(ROOT / "sitemap.xml", encoding="utf-8", xml_declaration=True)

print(f"Done! Generated {len(urls) - 2} articles.")
