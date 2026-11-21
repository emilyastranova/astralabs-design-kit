"""Publish the web kit, motion lab and brand guide to astralabs.dev/design.

Copies the three pages into the astralabs.github.io repo as
  design/web-kit/index.html
  design/motion-lab/index.html
  design/brand-guide/index.html

The web kit and motion lab are written as page fragments (no doctype or <head>), which is
fine for artifacts but renders in quirks mode as a plain page, so each gets a proper document
head with the site's favicons. Links to private claude.ai artifacts become plain text.

  python3 tools/publish_to_site.py [path/to/astralabs.github.io]
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT.parent / 'astralabs.github.io'

PAGES = [
    # source file, folder under /design, page title, description
    ('web-kit.html', 'web-kit', 'AstraLabs Web Kit',
     'Interface components for AstraLabs services: login and SSO, terminal, app shell, forms, tables, live logs and graphs.'),
    ('motion-lab.html', 'motion-lab', 'AstraLabs Motion Lab',
     'How AstraLabs moves: speeds and easing, the reboot intro, the dot field, the idle glitch and motion concepts.'),
    ('design-system.html', 'brand-guide', 'AstraLabs Brand Guide',
     'The AstraLabs brand guide: logo, color, type, geometry, line work, components and motion.'),
]


def head_tags(title, desc, path):
    url = f'https://astralabs.dev/design/{path}/'
    return f'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#0a0909">
<meta name="color-scheme" content="dark">
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="AstraLabs">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="https://astralabs.dev/images/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="https://astralabs.dev/images/og.png">
<link rel="icon" type="image/svg+xml" href="/favicon/favicon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon/favicon-32x32.png">
<link rel="apple-touch-icon" sizes="180x180" href="/favicon/apple-touch-icon.png">
'''


def strip_private_links(html):
    # <a href="https://claude.ai/...">text</a>  ->  text
    return re.sub(r'<a [^>]*href="https://claude\.ai/[^"]*"[^>]*>(.*?)</a>', r'\1', html, flags=re.S)


def publish(src, folder, title, desc):
    html = (ROOT / src).read_text(encoding='utf-8')
    html = strip_private_links(html)
    head = head_tags(title, desc, folder)
    if html.lstrip().lower().startswith('<!doctype'):
        # full document: swap the title and add the site tags after <head>
        html = re.sub(r'<title>.*?</title>', f'<title>{title}</title>', html, count=1, flags=re.S)
        html = re.sub(r'<meta charset="[^"]*">\s*', '', html, count=1)
        html = re.sub(r'<meta name="viewport"[^>]*>\s*', '', html, count=1)
        html = re.sub(r'(<head[^>]*>)', r'\1\n' + head, html, count=1)
    else:
        # fragment: wrap it; the browser places <title>, <link> and <style> in the head
        html = re.sub(r'<title>.*?</title>', '', html, count=1, flags=re.S)
        html = f'<!doctype html>\n<html lang="en">\n<head>\n{head}<title>{title}</title>\n{html}'
    out = SITE / 'design' / folder / 'index.html'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding='utf-8')
    print(f'{src} -> {out.relative_to(SITE)} ({len(html) // 1024} KB)')


if __name__ == '__main__':
    if not (SITE / 'CNAME').exists():
        sys.exit(f'{SITE} does not look like the astralabs.github.io repo')
    for page in PAGES:
        publish(*page)
