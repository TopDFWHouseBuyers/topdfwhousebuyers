#!/usr/bin/env python3
"""
Top DFW House Buyers — Sitemap Generator
Auto-detects all city folders dynamically — no hardcoded list needed.
Run: python scripts/generate_sitemap.py
"""
from pathlib import Path
from datetime import datetime

BASE_URL = "https://www.topdfwhousebuyers.com"

# Pages to exclude from city auto-detection
EXCLUDED_DIRS = {
    "blog", "scripts", ".github", "node_modules",
    ".git", "assets", "images", "css", "js"
}

def generate_sitemap():
    urls = []
    today = datetime.now().strftime("%Y-%m-%d")

    # ── Home page ──────────────────────────────────────────────────────────
    urls.append(f"""  <url>
    <loc>{BASE_URL}/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>""")

    # ── Blog index ─────────────────────────────────────────────────────────
    urls.append(f"""  <url>
    <loc>{BASE_URL}/blog/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.9</priority>
  </url>""")

    # ── City pages — auto-detected ─────────────────────────────────────────
    root = Path(".")
    city_dirs = sorted([
        d for d in root.iterdir()
        if d.is_dir()
        and d.name not in EXCLUDED_DIRS
        and not d.name.startswith(".")
        and (d / "index.html").exists()
    ])

    for city_dir in city_dirs:
        city_file = city_dir / "index.html"
        mod_date = datetime.fromtimestamp(city_file.stat().st_mtime).strftime("%Y-%m-%d")
        urls.append(f"""  <url>
    <loc>{BASE_URL}/{city_dir.name}/</loc>
    <lastmod>{mod_date}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.9</priority>
  </url>""")

    # ── Blog posts — auto-detected ─────────────────────────────────────────
    blog_dir = Path("blog")
    if blog_dir.exists():
        for post_dir in sorted(blog_dir.iterdir()):
            if post_dir.is_dir() and (post_dir / "index.html").exists():
                mod_date = datetime.fromtimestamp(
                    (post_dir / "index.html").stat().st_mtime
                ).strftime("%Y-%m-%d")
                urls.append(f"""  <url>
    <loc>{BASE_URL}/blog/{post_dir.name}/</loc>
    <lastmod>{mod_date}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>""")

    sitemap = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>'''

    with open("sitemap.xml", "w") as f:
        f.write(sitemap)

    print(f"Sitemap generated: {len(urls)} URLs")
    print(f"  - City pages: {len(city_dirs)}")

if __name__ == "__main__":
    generate_sitemap()
