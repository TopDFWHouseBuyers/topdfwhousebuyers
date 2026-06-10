#!/usr/bin/env python3
"""
Top DFW House Buyers - Blog Index Generator
Auto-scans all blog post folders and rebuilds the blog index page.
Extracts publish date from Article schema JSON inside each post.
Run: python scripts/generate_blog_index.py
"""

import re
import json
from pathlib import Path
from datetime import datetime


def get_post_meta(post_dir: Path) -> dict | None:
    index_file = post_dir / "index.html"
    if not index_file.exists():
        return None

    content = index_file.read_text(encoding="utf-8", errors="ignore")

    # Extract title
    title_match = re.search(r'<title>(.*?)</title>', content)
    title = title_match.group(1).strip() if title_match else post_dir.name.replace("-", " ").title()
    title = re.sub(r'\s*[\|·—]\s*Top DFW House Buyers.*$', '', title).strip()
    title = re.sub(r'\s*[\|·—]\s*topdfwhousebuyers.*$', '', title).strip()

    # Extract meta description
    desc_match = re.search(r'<meta name="description" content="(.*?)"', content)
    description = desc_match.group(1).strip() if desc_match else "Expert guide for DFW homeowners."

    # Extract publish date from Article schema JSON
    pub_date = None
    try:
        schema_matches = re.findall(r'<script type="application/ld\+json">(.*?)</script>', content, re.DOTALL)
        for schema_str in schema_matches:
            schema_str_clean = schema_str.strip()
            try:
                schema = json.loads(schema_str_clean)
                if schema.get('@type') == 'Article' and schema.get('datePublished'):
                    date_str = schema['datePublished']
                    # Parse ISO format date
                    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    pub_date = dt.strftime("%B %d, %Y")
                    break
            except (json.JSONDecodeError, ValueError):
                continue
    except Exception:
        pass

    # Fallback to hero-meta div date string
    if not pub_date:
        meta_match = re.search(r'class="hero-meta"[^>]*>Published ([^<·]+)', content)
        if meta_match:
            pub_date = meta_match.group(1).strip()

    # Final fallback to file modified time
    if not pub_date:
        mod_time = index_file.stat().st_mtime
        pub_date = datetime.fromtimestamp(mod_time).strftime("%B %d, %Y")

    # Detect category from slug
    slug = post_dir.name
    if any(w in slug for w in ['foreclosure', 'mortgage', 'pre-foreclosure']):
        category = "Foreclosure"
        cat_color = "#c0392b"
    elif any(w in slug for w in ['divorce', 'separation']):
        category = "Divorce"
        cat_color = "#8e44ad"
    elif any(w in slug for w in ['inherited', 'probate', 'estate']):
        category = "Inheritance"
        cat_color = "#d35400"
    elif any(w in slug for w in ['market', '2026', '2025']):
        category = "Market"
        cat_color = "#27ae60"
    elif any(w in slug for w in ['tenant', 'landlord', 'rental']):
        category = "Landlords"
        cat_color = "#2980b9"
    elif any(w in slug for w in ['sell-my-house-fast', 'we-buy-houses', 'cash-home-buyers']):
        category = "City Guide"
        cat_color = "#1a7a2a"
    else:
        category = "Education"
        cat_color = "#16a085"

    # Use schema date for sorting if available
    try:
        schema_matches = re.findall(r'<script type="application/ld\+json">(.*?)</script>', content, re.DOTALL)
        sort_time = index_file.stat().st_mtime
        for schema_str in schema_matches:
            try:
                schema = json.loads(schema_str.strip())
                if schema.get('@type') == 'Article' and schema.get('datePublished'):
                    dt = datetime.fromisoformat(schema['datePublished'].replace('Z', '+00:00'))
                    sort_time = dt.timestamp()
                    break
            except Exception:
                continue
    except Exception:
        sort_time = index_file.stat().st_mtime

    return {
        "slug": slug,
        "title": title,
        "description": description,
        "category": category,
        "cat_color": cat_color,
        "pub_date": pub_date,
        "sort_time": sort_time,
    }


def build_post_card(post: dict) -> str:
    return f'''    <article class="post-card">
      <div class="post-meta">
        <span class="post-cat" style="background:{post['cat_color']}15;color:{post['cat_color']};border-color:{post['cat_color']}40">{post['category']}</span>
        <span class="post-date">{post['pub_date']}</span>
      </div>
      <h2 class="post-title"><a href="/blog/{post['slug']}/">{post['title']}</a></h2>
      <p class="post-excerpt">{post['description'][:160]}</p>
      <a href="/blog/{post['slug']}/" class="post-read-more">Read Article →</a>
    </article>'''


def build_blog_index(posts: list) -> str:
    year = datetime.now().year
    post_cards = "\n".join([build_post_card(p) for p in posts])
    total = len(posts)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Blog — Top DFW House Buyers | Sell Your House Fast in DFW</title>
<meta name="description" content="Expert guides for DFW homeowners — how to sell fast, avoid foreclosure, handle inherited properties, divorce sales, and more. Top DFW House Buyers.">
<link rel="canonical" href="https://www.topdfwhousebuyers.com/blog/">
<script async src="https://www.googletagmanager.com/gtag/js?id=G-QSBN8EDR9Z"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-QSBN8EDR9Z');</script>
<script type="text/javascript">(function(c,l,a,r,i,t,y){{c[a]=c[a]||function(){{(c[a].q=c[a].q||[]).push(arguments)}};t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);}})(window,document,"clarity","script","wiurnc9zu7");</script>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Montserrat:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#f8faf8;color:#1a1f1a;font-family:'Montserrat',sans-serif;font-weight:300}}
.site-nav{{background:#0a0a0a;padding:14px 32px;display:flex;align-items:center;justify-content:space-between;border-bottom:3px solid #4ab840;position:sticky;top:0;z-index:100}}
.nav-logo{{color:#4ab840;font-family:'Playfair Display',serif;font-weight:700;font-size:18px;text-decoration:none}}
.nav-links{{display:flex;align-items:center;gap:20px}}
.nav-links a{{color:rgba(255,255,255,0.7);font-size:12px;font-weight:600;text-decoration:none;text-transform:uppercase;letter-spacing:0.05em}}
.nav-cta{{background:#4ab840;color:#fff !important;padding:9px 18px;border-radius:2px}}
.blog-hero{{background:#0a0a0a;padding:56px 40px;text-align:center;border-bottom:1px solid #1a1a1a}}
.blog-hero h1{{font-family:'Playfair Display',serif;font-size:clamp(28px,4vw,48px);color:#fff;font-weight:900;margin-bottom:12px}}
.blog-hero p{{font-size:15px;color:rgba(255,255,255,0.6);max-width:600px;margin:0 auto 20px}}
.blog-hero .count{{font-size:12px;color:#4ab840;font-weight:600;letter-spacing:0.1em;text-transform:uppercase}}
.blog-wrap{{max-width:1100px;margin:0 auto;padding:48px 24px}}
.posts-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:24px}}
@media(max-width:900px){{.posts-grid{{grid-template-columns:repeat(2,1fr)}}}}
@media(max-width:600px){{.posts-grid{{grid-template-columns:1fr}}}}
.post-card{{background:#fff;border:1px solid #d4e4d2;padding:24px;transition:transform .15s,box-shadow .15s;display:flex;flex-direction:column}}
.post-card:hover{{transform:translateY(-3px);box-shadow:0 8px 24px rgba(0,0,0,0.08)}}
.post-meta{{display:flex;align-items:center;gap:10px;margin-bottom:12px}}
.post-cat{{font-size:10px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;padding:3px 10px;border-radius:2px;border:1px solid}}
.post-date{{font-size:11px;color:#7a8a7a}}
.post-title{{font-family:'Playfair Display',serif;font-size:17px;font-weight:700;color:#1a1f1a;line-height:1.3;margin-bottom:10px}}
.post-title a{{color:inherit;text-decoration:none}}
.post-title a:hover{{color:#4ab840}}
.post-excerpt{{font-size:13px;color:#52675f;line-height:1.7;margin-bottom:16px;flex:1}}
.post-read-more{{font-size:12px;font-weight:700;color:#4ab840;text-decoration:none;letter-spacing:0.05em;text-transform:uppercase;margin-top:auto}}
.cta-band{{background:#1a1f1a;padding:48px 24px;text-align:center;margin-top:48px}}
.cta-band h2{{font-family:'Playfair Display',serif;font-size:28px;color:#fff;margin-bottom:12px}}
.cta-band p{{color:rgba(255,255,255,0.6);font-size:15px;margin-bottom:24px}}
.cta-band a{{display:inline-block;background:#4ab840;color:#fff;padding:14px 32px;font-weight:700;font-size:13px;text-decoration:none;border-radius:2px;letter-spacing:0.05em;text-transform:uppercase}}
footer{{background:#0a0a0a;color:rgba(255,255,255,0.4);text-align:center;padding:24px;font-size:11px;border-top:3px solid #4ab840}}
footer a{{color:#4ab840;text-decoration:none}}
</style>
</head>
<body>
<nav class="site-nav">
  <a href="/" class="nav-logo">Top DFW House Buyers</a>
  <div class="nav-links">
    <a href="/">Home</a>
    <a href="/blog/">Blog</a>
    <a href="tel:9722849713">972-284-9713</a>
    <a href="/#offer" class="nav-cta">Get Cash Offer</a>
  </div>
</nav>
<div class="blog-hero">
  <h1>Seller Resources &amp; Guides</h1>
  <p>Expert articles to help DFW homeowners navigate every situation — from foreclosure to inheritance to fast sales.</p>
  <div class="count">{total} Articles · Updated Regularly</div>
</div>
<div class="blog-wrap">
  <div class="posts-grid">
{post_cards}
  </div>
  <div class="cta-band">
    <h2>Ready to Sell Your DFW Home?</h2>
    <p>Get a fair cash offer in 24 hours. No fees, no repairs, no commissions. Close in as few as 7 days.</p>
    <a href="/#offer">Get My Free Cash Offer →</a>
  </div>
</div>
<footer>
  © {year} Top DFW House Buyers · <a href="/">topdfwhousebuyers.com</a> · 972-284-9713 · TX License #0657354
</footer>
</body>
</html>"""


def main():
    blog_dir = Path("blog")
    if not blog_dir.exists():
        print("No blog directory found.")
        return

    post_dirs = [d for d in blog_dir.iterdir() if d.is_dir() and (d / "index.html").exists()]

    posts = []
    for post_dir in post_dirs:
        meta = get_post_meta(post_dir)
        if meta:
            posts.append(meta)

    # Sort by actual publish date, newest first
    posts.sort(key=lambda x: x['sort_time'], reverse=True)

    print(f"Found {len(posts)} blog posts")

    html = build_blog_index(posts)
    output_file = blog_dir / "index.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Blog index rebuilt: {output_file}")
    print(f"Total posts shown: {len(posts)}")


if __name__ == "__main__":
    main()
