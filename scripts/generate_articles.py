import json
import html
import re
from pathlib import Path
from urllib.parse import quote
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "מאמרים"
OUTPUT = ROOT / "magazine-articles"
SITE = "https://isragays.github.io"

OUTPUT.mkdir(parents=True, exist_ok=True)

CATEGORIES = {
    "community": "חברה וקהילה",
    "news": "חדשות",
    "relationships": "היכרויות וזוגיות",
    "guides": "מדריכים",
    "events": "אירועים",
}


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

    text = re.sub(
        r"\s+on[a-z]+\s*=\s*(\"[^\"]*\"|'[^']*'|[^\s>]+)",
        "",
        text,
        flags=re.I,
    )

    text = re.sub(
        r"\s+(href|src)\s*=\s*(['\"])\s*(?:javascript|data):.*?\2",
        "",
        text,
        flags=re.I | re.S,
    )

    return text


def format_date(value):
    value = str(value or "").strip()

    match = re.match(
        r"^(\d{4})-(\d{2})-(\d{2})",
        value,
    )

    if match:
        year, month, day = match.groups()
        return f"{day}.{month}.{year}"

    return value


def article_html(data, filename):
    title = escape(data.get("title", "כתבה"))
    description = escape(data.get("description", ""))

    raw_category = str(data.get("category") or "")
    category = escape(
        CATEGORIES.get(raw_category, raw_category)
    )

    date = escape(format_date(data.get("date", "")))
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

    url = f"{SITE}/magazine-articles/{quote(filename)}.html"

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
* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    background: #091322;
    color: #f5f6fa;
    font-family: Assistant, Arial, sans-serif;
    line-height: 1.85;
}}

header {{
    background: #101e33;
    padding: 25px 15px;
    text-align: center;
    border-bottom: 1px solid #a88b52;
}}

.logo-link {{
    display: inline-block;
    text-decoration: none;
}}

.site-logo {{
    display: block;
    width: auto;
    max-width: min(85vw, 320px);
    max-height: 110px;
    height: auto;
    object-fit: contain;
    margin: 0 auto;
}}

main {{
    max-width: 820px;
    margin: 35px auto;
    padding: 0 20px;
}}

h1 {{
    font-size: clamp(30px, 6vw, 48px);
    line-height: 1.3;
    margin: 16px 0;
}}

.subtitle {{
    font-size: 21px;
    color: #cbd3df;
    margin: 22px 0;
}}

.meta {{
    color: #d7bd85;
    margin: 18px 0;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 12px;
    font-size: 16px;
}}

.category {{
    display: inline-block;
    border: 1px solid #a88b52;
    border-radius: 20px;
    padding: 2px 14px;
    color: #e4c789;
    font-weight: 700;
}}

.date {{
    color: #b8c2d0;
}}

.cover {{
    display: block;
    width: 100%;
    max-height: 470px;
    object-fit: cover;
    border-radius: 16px;
    margin: 25px 0;
}}

.content {{
    font-size: 20px;
    line-height: 1.9;
    overflow-wrap: anywhere;
}}

.content p {{
    margin: 0 0 20px;
}}

.content img {{
    max-width: 100%;
    height: auto;
    border-radius: 12px;
}}

.content a {{
    color: #e4c789;
}}

.content h2,
.content h3 {{
    color: #e4c789;
    line-height: 1.4;
    margin-top: 35px;
}}

.content blockquote {{
    margin: 25px 0;
    padding: 10px 20px;
    border-right: 3px solid #d7bd85;
    background: #101e33;
}}

.back {{
    display: inline-block;
    margin: 35px 0;
    color: #e4c789;
    font-size: 18px;
    text-decoration: none;
}}

.back:hover {{
    text-decoration: underline;
}}

footer {{
    text-align: center;
    padding: 30px 15px;
    color: #aab5c5;
    border-top: 1px solid #26344a;
}}

@media (max-width: 600px) {{
    header {{
        padding: 20px 12px;
    }}

    .site-logo {{
        max-width: 75vw;
        max-height: 85px;
    }}

    main {{
        margin: 25px auto;
        padding: 0 18px;
    }}

    .subtitle {{
        font-size: 19px;
    }}

    .content {{
        font-size: 18px;
    }}
}}
</style>
</head>

<body>

<header>
    <a class="logo-link" href="/" aria-label="ישראגייז - עמוד הבית">
        <img
            class="site-logo"
            src="/logo.png"
            alt="ישראגייז"
        >
    </a>
</header>

<main>

<article>

<div class="meta">
    <span class="category">{category}</span>
    <span class="date">{date}</span>
</div>

<h1>{title}</h1>

<p class="subtitle">{description}</p>

{image_tag}

<div class="content">
{body}
</div>

</article>

<a class="back" href="/magazine.html">
    → חזרה למגזין
</a>

</main>

<footer>
ישראגייז — הבית של הגייז בישראל
</footer>

</body>
</html>"""


urls = [
    SITE + "/",
    SITE + "/magazine.html",
]

for source in sorted(SOURCE.glob("*.json")):
    try:
        data = json.loads(
            source.read_text(encoding="utf-8")
        )

        if not isinstance(data, dict):
            continue

        filename = source.stem
        output = OUTPUT / f"{filename}.html"

        output.write_text(
            article_html(data, filename),
            encoding="utf-8",
        )

        urls.append(
            f"{SITE}/magazine-articles/{quote(filename)}.html"
        )

        print(f"Generated: {output.name}")

    except (OSError, ValueError, TypeError) as error:
        print(
            f"Error processing {source.name}: {error}"
        )
        raise


ET.register_namespace(
    "",
    "http://www.sitemaps.org/schemas/sitemap/0.9",
)

namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"

root = ET.Element(
    f"{{{namespace}}}urlset"
)

for url in urls:
    item = ET.SubElement(
        root,
        f"{{{namespace}}}url",
    )

    ET.SubElement(
        item,
        f"{{{namespace}}}loc",
    ).text = url


tree = ET.ElementTree(root)

ET.indent(tree, space="  ")

tree.write(
    ROOT / "sitemap.xml",
    encoding="utf-8",
    xml_declaration=True,
)

print(
    f"Done! Generated {len(urls) - 2} articles."
)
