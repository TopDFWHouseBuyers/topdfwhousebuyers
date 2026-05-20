#!/usr/bin/env python3
"""
Internal Linking Script
Adds blog → city links and city → blog links across both sites.
Run from the ROOT of each repo:
  python scripts/add_internal_links.py

Safe to re-run — checks if links already injected before modifying.
"""

import os
import re
from pathlib import Path

# ── CONFIGURATION — set SITE before running ───────────────────────────────
# Change to 'socal' when running on coastalcashoffer repo
SITE = os.environ.get("SITE", "dfw")  # 'dfw' or 'socal'

# ── DFW CONFIG ─────────────────────────────────────────────────────────────
DFW_CONFIG = {
    "base_url": "https://www.topdfwhousebuyers.com",
    "brand": "Top DFW House Buyers",
    "phone": "972-284-9713",
    "accent_color": "#4ab840",
    "bg_color": "#0a0a0a",
    "text_color": "#fff",
    "link_color": "#4ab840",
    "cities": [
        "plano","frisco","allen","richardson","mckinney","the-colony","prosper",
        "celina","wylie","lewisville","carrollton","coppell","flower-mound",
        "little-elm","denton","dallas","garland","irving","grand-prairie",
        "mesquite","desoto","duncanville","cedar-hill","lancaster",
        "farmers-branch","rowlett","fort-worth","arlington","north-richland-hills",
        "mansfield","grapevine","colleyville","southlake","keller","hurst",
        "euless","bedford","burleson","rockwall","waxahachie","midlothian",
    ],
    "blog_topics": {
        # slug keyword → relevant city slugs
        "foreclosure": ["dallas","fort-worth","arlington","grand-prairie","mesquite"],
        "inherited":   ["plano","frisco","mckinney","allen","richardson"],
        "divorce":     ["carrollton","lewisville","irving","garland","rowlett"],
        "landlord":    ["dallas","garland","irving","mesquite","grand-prairie"],
        "repair":      ["desoto","duncanville","cedar-hill","lancaster","wylie"],
        "relocat":     ["frisco","mckinney","allen","prosper","celina"],
        "cash":        ["plano","frisco","allen","mckinney","dallas"],
        "tax":         ["dallas","fort-worth","arlington","grand-prairie","irving"],
        "probate":     ["plano","richardson","garland","mesquite","carrollton"],
        "tenant":      ["dallas","irving","garland","grand-prairie","arlington"],
        "fast":        ["dallas","fort-worth","arlington","plano","frisco"],
        "traditional": ["plano","frisco","southlake","colleyville","keller"],
        "market":      ["frisco","mckinney","celina","prosper","allen"],
        "hoa":         ["frisco","allen","prosper","celina","flower-mound"],
        "foundation":  ["dallas","fort-worth","arlington","grand-prairie","mesquite"],
    }
}

# ── SOCAL CONFIG ───────────────────────────────────────────────────────────
SOCAL_CONFIG = {
    "base_url": "https://www.goldencoastcashoffer.com",
    "brand": "Golden Coast Cash Offer",
    "phone": "949-280-5139",
    "accent_color": "#e8823a",
    "bg_color": "#0f4a63",
    "text_color": "#fff",
    "link_color": "#f8d264",
    "cities": [
        "irvine","anaheim","santa-ana","huntington-beach","newport-beach",
        "mission-viejo","laguna-hills","laguna-niguel","lake-forest",
        "san-clemente","san-juan-capistrano","aliso-viejo","costa-mesa",
        "tustin","fountain-valley","garden-grove","fullerton","orange",
        "yorba-linda","dana-point","laguna-beach","brea","placentia",
        "buena-park","westminster","seal-beach","stanton",
        "san-diego","chula-vista","oceanside","escondido","el-cajon",
        "vista","carlsbad","san-marcos","santee","la-mesa","poway",
        "lemon-grove","national-city","coronado","imperial-beach",
        "solana-beach","del-mar","encinitas","la-jolla",
        "long-beach","torrance","pasadena","burbank","glendale",
        "whittier","downey","norwalk","cerritos","lakewood",
        "bellflower","paramount","el-monte","west-covina","alhambra",
        "monterey-park","arcadia","santa-clarita","pomona",
        "malibu","santa-monica","los-angeles","beverly-hills","west-hollywood",
        "culver-city","inglewood","hawthorne","gardena","compton","carson",
        "el-segundo","manhattan-beach","hermosa-beach","redondo-beach",
        "ventura","oxnard","port-hueneme","camarillo","thousand-oaks",
        "simi-valley","ojai",
        "riverside","corona","murrieta","temecula","menifee",
        "lake-elsinore","ontario","rancho-cucamonga",
        "laguna-woods","rancho-santa-margarita","trabuco-canyon","foothill-ranch",
        "laguna-hills","laguna-niguel",
    ],
    "blog_topics": {
        "foreclosure": ["san-diego","los-angeles","anaheim","santa-ana","long-beach"],
        "inherited":   ["irvine","newport-beach","laguna-beach","pasadena","glendale"],
        "divorce":     ["irvine","anaheim","long-beach","burbank","torrance"],
        "landlord":    ["los-angeles","santa-ana","anaheim","long-beach","inglewood"],
        "repair":      ["compton","inglewood","el-cajon","national-city","santa-ana"],
        "relocat":     ["irvine","newport-beach","laguna-niguel","carlsbad","san-diego"],
        "cash":        ["irvine","newport-beach","laguna-beach","los-angeles","san-diego"],
        "tax":         ["los-angeles","san-diego","irvine","anaheim","long-beach"],
        "probate":     ["pasadena","glendale","burbank","irvine","newport-beach"],
        "tenant":      ["los-angeles","santa-ana","anaheim","long-beach","san-diego"],
        "fast":        ["los-angeles","san-diego","irvine","anaheim","long-beach"],
        "traditional": ["irvine","newport-beach","laguna-beach","manhattan-beach","pasadena"],
        "market":      ["irvine","newport-beach","laguna-niguel","carlsbad","encinitas"],
        "mortgage":    ["san-diego","los-angeles","anaheim","santa-ana","riverside"],
        "california":  ["los-angeles","san-diego","irvine","long-beach","anaheim"],
        "hoa":         ["irvine","mission-viejo","aliso-viejo","rancho-santa-margarita","temecula"],
        "coastal":     ["malibu","laguna-beach","newport-beach","santa-monica","del-mar"],
    }
}

SENTINEL = "<!-- internal-links-injected -->"


def get_config():
    return DFW_CONFIG if SITE == "dfw" else SOCAL_CONFIG


def get_city_name(slug):
    return slug.replace("-", " ").title()


def get_blog_posts():
    blog_dir = Path("blog")
    posts = []
    if blog_dir.exists():
        for post_dir in sorted(blog_dir.iterdir()):
            if post_dir.is_dir() and (post_dir / "index.html").exists():
                posts.append(post_dir.name)
    return posts


def get_blog_title(slug):
    path = Path(f"blog/{slug}/index.html")
    if not path.exists():
        return slug.replace("-", " ").title()
    content = path.read_text(encoding="utf-8")
    m = re.search(r'<title>(.*?)</title>', content)
    if m:
        title = m.group(1)
        title = re.sub(r'\s*[\|·]\s*.*$', '', title).strip()
        return title
    return slug.replace("-", " ").title()


def match_cities_for_blog(blog_slug, config, count=3):
    """Find the most relevant city slugs for a blog post."""
    topics = config["blog_topics"]
    matched = []
    for keyword, cities in topics.items():
        if keyword in blog_slug:
            for c in cities:
                if c not in matched and c in config["cities"]:
                    matched.append(c)
    # If no match, use top cities
    if not matched:
        matched = config["cities"][:5]
    return matched[:count]


def match_blogs_for_city(city_slug, blog_slugs, config, count=3):
    """Find the most relevant blog posts for a city page."""
    topics = config["blog_topics"]
    scored = {}
    for blog_slug in blog_slugs:
        score = 0
        for keyword, cities in topics.items():
            if city_slug in cities and keyword in blog_slug:
                score += 2
            elif keyword in blog_slug:
                score += 1
        scored[blog_slug] = score
    sorted_blogs = sorted(scored.keys(), key=lambda x: scored[x], reverse=True)
    return sorted_blogs[:count]


def build_city_links_html(city_slugs, config):
    accent = config["accent_color"]
    bg = config["bg_color"]
    base = config["base_url"]
    items = ""
    for slug in city_slugs:
        name = get_city_name(slug)
        items += f'''
      <a href="{base}/{slug}/" style="display:inline-block;padding:8px 16px;background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.2);color:rgba(255,255,255,0.85);font-size:12px;font-weight:600;text-decoration:none;border-radius:4px;transition:all .15s" onmouseover="this.style.background='{accent}';this.style.color='#fff'" onmouseout="this.style.background='rgba(255,255,255,0.08)';this.style.color='rgba(255,255,255,0.85)'">{name}</a>'''
    return f'''
{SENTINEL}
<div style="background:{bg};padding:28px 32px;margin:32px 0;border-left:4px solid {accent}">
  <p style="font-size:11px;font-weight:700;letter-spacing:0.15em;text-transform:uppercase;color:{accent};margin-bottom:12px">We Buy Houses In These Cities</p>
  <div style="display:flex;flex-wrap:wrap;gap:8px">{items}
  </div>
</div>'''


def build_blog_links_html(blog_slugs, config):
    accent = config["accent_color"]
    base = config["base_url"]
    items = ""
    for slug in blog_slugs:
        title = get_blog_title(slug)
        items += f'''
      <a href="{base}/blog/{slug}/" style="display:block;padding:12px 16px;background:#fff;border:1px solid #e0d8cc;border-left:3px solid {accent};color:#2a2018;font-size:13px;font-weight:600;text-decoration:none;margin-bottom:8px;border-radius:0 6px 6px 0;line-height:1.4">{title} →</a>'''
    return f'''
{SENTINEL}
<div style="background:#f5f0e8;padding:24px 28px;margin:32px 0;border-radius:8px">
  <p style="font-size:11px;font-weight:700;letter-spacing:0.15em;text-transform:uppercase;color:{accent};margin-bottom:14px">Helpful Resources</p>{items}
</div>'''


def inject_into_blog_post(blog_slug, config):
    path = Path(f"blog/{blog_slug}/index.html")
    if not path.exists():
        return False

    content = path.read_text(encoding="utf-8")

    # Skip if already injected
    if SENTINEL in content:
        return False

    city_slugs = match_cities_for_blog(blog_slug, config)
    links_html = build_city_links_html(city_slugs, config)

    # Inject before the closing CTA inline block or before </div> of article-body
    injection_markers = [
        '<div class="cta-inline"',
        '<div class="review-cta"',
        '</div>\n\n  <div class="sidebar"',
    ]

    injected = False
    for marker in injection_markers:
        if marker in content:
            content = content.replace(marker, links_html + "\n    " + marker, 1)
            injected = True
            break

    if not injected:
        # Fallback: inject before closing article div
        content = content.replace('</div>\n\n  <div class="sidebar"',
                                   links_html + '\n</div>\n\n  <div class="sidebar"', 1)
        injected = True

    if injected:
        path.write_text(content, encoding="utf-8")
        return True
    return False


def inject_into_city_page(city_slug, blog_slugs, config):
    path = Path(f"{city_slug}/index.html")
    if not path.exists():
        return False

    content = path.read_text(encoding="utf-8")

    # Skip if already injected
    if SENTINEL in content:
        return False

    matched_blogs = match_blogs_for_city(city_slug, blog_slugs, config)
    if not matched_blogs:
        return False

    links_html = build_blog_links_html(matched_blogs, config)

    # Inject before the why-box or cta-box in main content
    injection_markers = [
        '<div class="why-box"',
        '<div class="cta-box"',
    ]

    injected = False
    for marker in injection_markers:
        if marker in content:
            content = content.replace(marker, links_html + "\n    " + marker, 1)
            injected = True
            break

    if injected:
        path.write_text(content, encoding="utf-8")
        return True
    return False


def main():
    config = get_config()
    print(f"Internal Linking Script — Site: {SITE.upper()}")
    print(f"Base URL: {config['base_url']}")
    print()

    blog_slugs = get_blog_posts()
    print(f"Found {len(blog_slugs)} blog posts")
    print(f"Found {len(config['cities'])} cities")
    print()

    # ── Blog posts → City links ────────────────────────────────────────────
    print("Adding city links to blog posts...")
    blog_updated = 0
    for slug in blog_slugs:
        result = inject_into_blog_post(slug, config)
        status = "✓ Updated" if result else "  Skipped (already done)"
        print(f"  {status}: blog/{slug}/")
        if result:
            blog_updated += 1

    print(f"\n  {blog_updated}/{len(blog_slugs)} blog posts updated")
    print()

    # ── City pages → Blog links ────────────────────────────────────────────
    print("Adding blog links to city pages...")
    city_updated = 0
    for city_slug in config["cities"]:
        result = inject_into_city_page(city_slug, blog_slugs, config)
        status = "✓ Updated" if result else "  Skipped"
        if result:
            print(f"  {status}: {city_slug}/")
            city_updated += 1

    print(f"\n  {city_updated}/{len(config['cities'])} city pages updated")
    print()
    print("Done! Commit all changes to GitHub — Netlify will auto-deploy.")
    print()
    print("Next: run generate_sitemap.py to update lastmod dates.")


if __name__ == "__main__":
    main()
