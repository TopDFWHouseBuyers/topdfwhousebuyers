#!/usr/bin/env python3
"""
Top DFW House Buyers  -  Automated Blog Generator
Runs on GitHub Actions every Monday and Thursday at 8am CT
Generates SEO-optimized blog posts using Claude API
"""

import os
import json
import random
import re
import anthropic
from datetime import datetime
from pathlib import Path

# ── TOPIC DATABASE ─────────────────────────────────────────────────────────

CITIES = [
    "Plano", "Frisco", "Allen", "McKinney", "Richardson", "The Colony",
    "Lewisville", "Flower Mound", "Keller", "Grapevine", "Colleyville",
    "Southlake", "North Richland Hills", "Hurst", "Euless", "Bedford",
    "Watauga", "Prosper", "Celina", "Anna", "Melissa", "Dallas",
    "Arlington", "Garland", "Irving", "Carrollton", "Mesquite",
    "Grand Prairie", "Denton", "Fort Worth", "Wylie", "Sachse",
    "Rowlett", "Rockwall", "Little Elm", "Coppell", "Addison"
]

CITY_TOPICS = [
    "How to Sell Your House Fast in {city}, TX  -  No Fees, No Repairs",
    "We Buy Houses in {city}, TX  -  Get a Cash Offer in 24 Hours",
    "Sell My House Fast {city} TX  -  The Complete Guide",
    "Cash Home Buyers in {city}, TX  -  What You Need to Know",
    "Selling Your {city} Home As-Is  -  Everything You Need to Know",
    "How to Avoid Foreclosure in {city}, TX",
    "Selling an Inherited Property in {city}, TX  -  A Step-by-Step Guide",
    "Selling a House During Divorce in {city}, TX",
    "Tired Landlord? How to Sell Your Rental Property in {city}, TX Fast",
    "Relocating from {city}, TX? How to Sell Your Home Fast",
    "What Is My {city} Home Worth to a Cash Buyer?",
    "Selling a Fire-Damaged or Flood-Damaged Home in {city}, TX",
]

EVERGREEN_TOPICS = [
    # DIVORCE
    {
        "title": "Selling a House During Divorce in Texas  -  Everything You Need to Know",
        "slug": "selling-house-during-divorce-texas",
        "keyword": "selling house during divorce Texas",
        "category": "divorce"
    },
    {
        "title": "How to Sell Your Texas Home Fast During a Divorce",
        "slug": "sell-home-fast-divorce-texas",
        "keyword": "sell home fast divorce Texas",
        "category": "divorce"
    },
    {
        "title": "Texas Community Property Laws and What They Mean When Selling Your Home",
        "slug": "texas-community-property-selling-home",
        "keyword": "Texas community property selling home",
        "category": "divorce"
    },
    # FORECLOSURE
    {
        "title": "How to Stop Foreclosure in Texas  -  Your Options Explained",
        "slug": "stop-foreclosure-texas",
        "keyword": "stop foreclosure Texas",
        "category": "foreclosure"
    },
    {
        "title": "Pre-Foreclosure in Texas  -  What It Means and What You Can Do",
        "slug": "pre-foreclosure-texas",
        "keyword": "pre-foreclosure Texas",
        "category": "foreclosure"
    },
    {
        "title": "Selling Your Home Before Foreclosure in Texas  -  Is It Possible?",
        "slug": "sell-home-before-foreclosure-texas",
        "keyword": "sell home before foreclosure Texas",
        "category": "foreclosure"
    },
    {
        "title": "Behind on Mortgage Payments in Texas? Here Are Your Options",
        "slug": "behind-on-mortgage-payments-texas",
        "keyword": "behind on mortgage payments Texas options",
        "category": "foreclosure"
    },
    {
        "title": "How Long Does Foreclosure Take in Texas?",
        "slug": "how-long-does-foreclosure-take-texas",
        "keyword": "how long does foreclosure take Texas",
        "category": "foreclosure"
    },
    # INHERITANCE
    {
        "title": "Selling an Inherited House in Texas  -  A Complete Guide",
        "slug": "selling-inherited-house-texas",
        "keyword": "selling inherited house Texas",
        "category": "inheritance"
    },
    {
        "title": "How to Sell an Inherited Property in Texas During Probate",
        "slug": "sell-inherited-property-probate-texas",
        "keyword": "sell inherited property probate Texas",
        "category": "inheritance"
    },
    {
        "title": "What to Do With an Inherited House in Texas You Don't Want",
        "slug": "inherited-house-texas-dont-want",
        "keyword": "inherited house Texas don't want",
        "category": "inheritance"
    },
    {
        "title": "Selling an Estate Property in Texas  -  Cash Sale vs. Traditional Listing",
        "slug": "selling-estate-property-texas",
        "keyword": "selling estate property Texas",
        "category": "inheritance"
    },
    {
        "title": "Texas Probate Process for Selling a House  -  What Heirs Need to Know",
        "slug": "texas-probate-process-selling-house",
        "keyword": "Texas probate process selling house",
        "category": "inheritance"
    },
    # CASH BUYER EDUCATION
    {
        "title": "What Is a Cash Home Buyer? How the Process Works in Texas",
        "slug": "what-is-cash-home-buyer-texas",
        "keyword": "what is a cash home buyer Texas",
        "category": "education"
    },
    {
        "title": "Cash Offer vs. Traditional Sale in Texas  -  Which Is Better for You?",
        "slug": "cash-offer-vs-traditional-sale-texas",
        "keyword": "cash offer vs traditional sale Texas",
        "category": "education"
    },
    {
        "title": "How Do Cash Home Buyers Make Money? The Truth Explained",
        "slug": "how-do-cash-home-buyers-make-money",
        "keyword": "how do cash home buyers make money",
        "category": "education"
    },
    {
        "title": "Is It Better to Sell to a Cash Buyer or List With an Agent in Texas?",
        "slug": "cash-buyer-vs-agent-texas",
        "keyword": "cash buyer vs agent Texas",
        "category": "education"
    },
    {
        "title": "The Real Cost of Selling a House in Texas  -  Fees, Commissions, and Hidden Costs",
        "slug": "real-cost-selling-house-texas",
        "keyword": "cost of selling a house Texas",
        "category": "education"
    },
    {
        "title": "How Fast Can You Sell a House in Texas? Timeline Explained",
        "slug": "how-fast-can-you-sell-house-texas",
        "keyword": "how fast can you sell a house Texas",
        "category": "education"
    },
    {
        "title": "Selling a House As-Is in Texas  -  What Sellers Need to Know",
        "slug": "selling-house-as-is-texas",
        "keyword": "selling house as-is Texas",
        "category": "education"
    },
    {
        "title": "Do You Have to Pay Taxes When You Sell Your House in Texas?",
        "slug": "taxes-selling-house-texas",
        "keyword": "taxes selling house Texas",
        "category": "education"
    },
    {
        "title": "What Happens at a Cash Home Sale Closing in Texas?",
        "slug": "cash-home-sale-closing-texas",
        "keyword": "cash home sale closing Texas",
        "category": "education"
    },
    {
        "title": "How to Get a Fair Cash Offer on Your Texas Home",
        "slug": "how-to-get-fair-cash-offer-texas",
        "keyword": "fair cash offer Texas home",
        "category": "education"
    },
    # SPECIFIC SITUATIONS
    {
        "title": "Selling a House With Tenants in Texas  -  Landlord's Complete Guide",
        "slug": "selling-house-with-tenants-texas",
        "keyword": "selling house with tenants Texas",
        "category": "situations"
    },
    {
        "title": "How to Sell a Hoarder House in Texas Fast",
        "slug": "sell-hoarder-house-texas",
        "keyword": "sell hoarder house Texas",
        "category": "situations"
    },
    {
        "title": "Selling a House With Foundation Problems in Texas",
        "slug": "selling-house-foundation-problems-texas",
        "keyword": "selling house foundation problems Texas",
        "category": "situations"
    },
    {
        "title": "How to Sell a Fire-Damaged Home in Texas",
        "slug": "sell-fire-damaged-home-texas",
        "keyword": "sell fire damaged home Texas",
        "category": "situations"
    },
    {
        "title": "Selling a Vacant or Abandoned House in Texas",
        "slug": "selling-vacant-house-texas",
        "keyword": "selling vacant house Texas",
        "category": "situations"
    },
    {
        "title": "How to Sell a House With Mold in Texas",
        "slug": "sell-house-with-mold-texas",
        "keyword": "sell house with mold Texas",
        "category": "situations"
    },
    {
        "title": "Selling a House With Code Violations in Texas",
        "slug": "selling-house-code-violations-texas",
        "keyword": "selling house code violations Texas",
        "category": "situations"
    },
    {
        "title": "How to Sell a House With a Lien in Texas",
        "slug": "sell-house-with-lien-texas",
        "keyword": "sell house with lien Texas",
        "category": "situations"
    },
    {
        "title": "Selling Your Texas Home During a Job Loss or Financial Hardship",
        "slug": "selling-home-financial-hardship-texas",
        "keyword": "selling home financial hardship Texas",
        "category": "situations"
    },
    {
        "title": "How to Sell Your Texas Home When You're Relocating for Work",
        "slug": "sell-home-relocating-texas",
        "keyword": "sell home relocating Texas",
        "category": "situations"
    },
    {
        "title": "Selling a Rental Property in Texas  -  Cash Sale vs. 1031 Exchange",
        "slug": "selling-rental-property-texas",
        "keyword": "selling rental property Texas",
        "category": "situations"
    },
    {
        "title": "Downsizing in Texas  -  How to Sell Your Family Home Fast",
        "slug": "downsizing-texas-sell-family-home",
        "keyword": "downsizing Texas sell home fast",
        "category": "situations"
    },
    # DFW MARKET
    {
        "title": "DFW Real Estate Market 2025  -  What Sellers Need to Know",
        "slug": "dfw-real-estate-market-2025-sellers",
        "keyword": "DFW real estate market 2025 sellers",
        "category": "market"
    },
    {
        "title": "Is Now a Good Time to Sell Your DFW Home?",
        "slug": "good-time-sell-dfw-home",
        "keyword": "good time to sell DFW home",
        "category": "market"
    },
    {
        "title": "Why DFW Home Prices Are Still Strong  -  And What It Means for Sellers",
        "slug": "dfw-home-prices-sellers",
        "keyword": "DFW home prices sellers",
        "category": "market"
    },
]

def get_next_topic():
    """Determine which topic to write based on current date/post count"""
    # Read tracking file
    tracking_file = Path("blog/tracking.json")
    if tracking_file.exists():
        with open(tracking_file) as f:
            tracking = json.load(f)
    else:
        tracking = {"posts_written": 0, "city_index": 0, "evergreen_index": 0, "last_post": None}

    posts_written = tracking.get("posts_written", 0)

    # Alternate: city post, evergreen post, city post, evergreen post...
    if posts_written % 2 == 0:
        # City-specific post
        city_idx = tracking.get("city_index", 0) % len(CITIES)
        topic_template = CITY_TOPICS[posts_written % len(CITY_TOPICS)]
        city = CITIES[city_idx]
        title = topic_template.format(city=city)
        slug = f"sell-my-house-fast-{city.lower().replace(' ', '-')}-tx-{posts_written}"
        keyword = f"sell my house fast {city} TX"
        post_type = "city"
        tracking["city_index"] = (city_idx + 1) % len(CITIES)
        extra_context = f"Target city: {city}, Texas. Include local context about {city} neighborhoods, the local real estate market, and why sellers in {city} specifically benefit from working with a cash buyer."
    else:
        # Evergreen/situation post
        ev_idx = tracking.get("evergreen_index", 0) % len(EVERGREEN_TOPICS)
        topic = EVERGREEN_TOPICS[ev_idx]
        title = topic["title"]
        slug = topic["slug"]
        keyword = topic["keyword"]
        post_type = "evergreen"
        tracking["evergreen_index"] = (ev_idx + 1) % len(EVERGREEN_TOPICS)
        extra_context = f"Category: {topic['category']}. Write from the perspective of someone in this specific situation in Texas/DFW area."

    tracking["posts_written"] = posts_written + 1
    tracking["last_post"] = datetime.now().isoformat()

    # Save tracking
    tracking_file.parent.mkdir(exist_ok=True)
    with open(tracking_file, "w") as f:
        json.dump(tracking, f, indent=2)

    return {
        "title": title,
        "slug": slug,
        "keyword": keyword,
        "post_type": post_type,
        "extra_context": extra_context
    }


def generate_post(topic: dict) -> dict:
    """Call Claude API to generate the blog post"""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    prompt = f"""You are an expert real estate SEO content writer for Top DFW House Buyers, a cash home buying company in Dallas-Fort Worth, Texas.

COMPANY INFO:
- Name: Top DFW House Buyers
- Phone: 972-284-9713
- Website: https://www.topdfwhousebuyers.com
- License: TX Real Estate License #0657354
- Service area: All of DFW  -  Plano, Frisco, Allen, McKinney, Richardson, The Colony, Lewisville, Flower Mound, Keller, Grapevine, Colleyville, Southlake, North Richland Hills, Hurst, Euless, Bedford, Watauga, Prosper, Celina, Anna, Melissa, Dallas and all surrounding areas

ASSIGNMENT:
- Title: {topic['title']}
- Primary keyword: {topic['keyword']}
- Additional context: {topic['extra_context']}
- Word count: 1,200-1,500 words
- Include 3 call-to-action sections throughout
- Tone: Helpful, knowledgeable, empathetic  -  like a trusted local expert

REQUIREMENTS:
1. Write genuinely helpful content that answers real questions people have
2. Use H2 and H3 subheadings naturally throughout
3. Each CTA should mention 972-284-9713 and link to /#offer
4. Natural conversational tone  -  not corporate or salesy
5. Include specific, practical advice relevant to Texas law/market where applicable
6. Meta title must be under 60 characters
7. Meta description must be under 160 characters

Return ONLY valid JSON (no markdown, no backticks, no explanation):
{{
  "meta_title": "...",
  "meta_description": "...",
  "h1": "...",
  "intro": "...(2-3 sentence intro paragraph)...",
  "content_html": "...(full HTML using only h2, h3, p, ul, ol, li tags  -  NO html/head/body tags)...",
  "word_count": 0,
  "secondary_keywords": ["...", "...", "..."]
}}"""

    # Ensure prompt is ASCII-safe
    prompt_safe = prompt.encode('ascii', errors='replace').decode('ascii')
    
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt_safe}]
    )

    raw = message.content[0].text.strip()
    # Clean any accidental markdown
    raw = re.sub(r'^```json\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)
    return json.loads(raw)


def build_html_page(post: dict, topic: dict) -> str:
    """Build a complete SEO-optimized HTML page"""
    date_str = datetime.now().strftime("%B %d, %Y")
    year = datetime.now().year

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{post['meta_title']}</title>
<meta name="description" content="{post['meta_description']}">
<meta property="og:title" content="{post['meta_title']}">
<meta property="og:description" content="{post['meta_description']}">
<meta property="og:type" content="article">
<meta property="og:url" content="https://www.topdfwhousebuyers.com/blog/{topic['slug']}/">
<link rel="canonical" href="https://www.topdfwhousebuyers.com/blog/{topic['slug']}/">
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{post['h1']}",
  "datePublished": "{datetime.now().isoformat()}",
  "publisher": {{
    "@type": "Organization",
    "name": "Top DFW House Buyers",
    "telephone": "972-284-9713",
    "url": "https://www.topdfwhousebuyers.com"
  }}
}}
</script>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Montserrat:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#f8faf8;color:#1a1f1a;font-family:'Montserrat',sans-serif;font-weight:300;line-height:1.6}}
.site-nav{{background:#0a0a0a;padding:16px 32px;display:flex;align-items:center;justify-content:space-between;border-bottom:3px solid #4ab840;position:sticky;top:0;z-index:100}}
.nav-logo{{color:#4ab840;font-weight:700;font-size:18px;text-decoration:none}}
.nav-logo span{{color:#fff}}
.nav-links{{display:flex;align-items:center;gap:20px}}
.nav-links a{{color:rgba(255,255,255,0.7);font-size:12px;font-weight:600;text-decoration:none;letter-spacing:0.05em;text-transform:uppercase}}
.nav-cta{{background:#4ab840;color:#fff !important;padding:9px 18px;border-radius:2px}}
.hero-blog{{background:#405440;padding:64px 40px;text-align:center;position:relative;overflow:hidden}}
.hero-blog::before{{content:'';position:absolute;inset:0;background:url('https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=1200&q=60') center/cover;opacity:0.15}}
.hero-blog-inner{{position:relative;z-index:1;max-width:800px;margin:0 auto}}
.hero-cat{{display:inline-block;background:rgba(74,184,64,0.2);border:1px solid rgba(74,184,64,0.4);color:#6dd962;font-size:10px;font-weight:700;letter-spacing:0.2em;text-transform:uppercase;padding:5px 12px;border-radius:2px;margin-bottom:16px}}
.hero-blog h1{{font-family:'Playfair Display',serif;font-size:clamp(26px,4vw,44px);color:#fff;font-weight:700;line-height:1.15;margin-bottom:16px}}
.hero-meta{{font-size:11px;color:rgba(255,255,255,0.5);letter-spacing:0.1em;text-transform:uppercase}}
.content-layout{{max-width:1100px;margin:0 auto;padding:48px 24px;display:grid;grid-template-columns:1fr 300px;gap:48px;align-items:start}}
@media(max-width:768px){{.content-layout{{grid-template-columns:1fr}}}}
.article-body h2{{font-family:'Playfair Display',serif;font-size:26px;font-weight:700;color:#1a1f1a;margin:36px 0 14px;line-height:1.2}}
.article-body h3{{font-size:18px;font-weight:700;color:#1a1f1a;margin:24px 0 10px}}
.article-body p{{font-size:15px;line-height:1.9;color:#3a4a3a;margin-bottom:16px}}
.article-body ul,.article-body ol{{padding-left:22px;margin-bottom:16px}}
.article-body li{{font-size:15px;line-height:1.8;color:#3a4a3a;margin:6px 0}}
.cta-inline{{background:#0a0a0a;border-left:4px solid #4ab840;padding:24px 28px;margin:32px 0;border-radius:0 4px 4px 0}}
.cta-inline h3{{color:#4ab840;font-size:16px;font-weight:700;margin-bottom:8px}}
.cta-inline p{{color:rgba(255,255,255,0.8);font-size:14px;margin-bottom:16px;line-height:1.7}}
.cta-inline a{{display:inline-block;background:#4ab840;color:#fff;padding:12px 24px;font-weight:700;font-size:13px;text-decoration:none;border-radius:2px;letter-spacing:0.05em;text-transform:uppercase}}
.sidebar{{position:sticky;top:80px}}
.sidebar-card{{background:#fff;border:1px solid #d4e4d2;border-top:3px solid #4ab840;padding:24px;margin-bottom:20px;border-radius:0 0 4px 4px}}
.sidebar-card h3{{font-size:15px;font-weight:700;color:#1a1f1a;margin-bottom:8px}}
.sidebar-card p{{font-size:13px;color:#52675f;line-height:1.6;margin-bottom:16px}}
.sidebar-card .phone{{font-size:20px;font-weight:700;color:#4ab840;text-decoration:none;display:block;margin-bottom:12px}}
.sidebar-btn{{display:block;background:#0a0a0a;color:#fff;padding:13px;font-weight:700;font-size:12px;text-decoration:none;border-radius:2px;letter-spacing:0.06em;text-transform:uppercase;text-align:center;margin-bottom:8px}}
.sidebar-btn.green{{background:#4ab840}}
.back-link{{display:inline-flex;align-items:center;gap:6px;color:#4ab840;text-decoration:none;font-size:12px;font-weight:600;margin-bottom:28px;letter-spacing:0.05em;text-transform:uppercase}}
.related-posts{{margin-top:48px;padding-top:32px;border-top:1px solid #d4e4d2}}
.related-posts h3{{font-family:'Playfair Display',serif;font-size:22px;font-weight:700;margin-bottom:20px}}
.related-grid{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px}}
@media(max-width:640px){{.related-grid{{grid-template-columns:1fr}}}}
.related-card{{background:#fff;border:1px solid #d4e4d2;padding:16px;border-radius:3px}}
.related-card a{{color:#1a1f1a;text-decoration:none;font-size:13px;font-weight:600;line-height:1.4}}
.related-card a:hover{{color:#4ab840}}
footer{{background:#0a0a0a;color:rgba(255,255,255,0.5);text-align:center;padding:28px;font-size:12px;margin-top:0;border-top:3px solid #4ab840}}
footer a{{color:#4ab840;text-decoration:none}}
</style>
</head>
<body>

<nav class="site-nav">
  <a href="/" class="nav-logo">Top<span>DFW</span> House Buyers</a>
  <div class="nav-links">
    <a href="/">Home</a>
    <a href="/blog/">Blog</a>
    <a href="tel:9722849713">📞 972-284-9713</a>
    <a href="/#offer" class="nav-cta">Get Cash Offer</a>
  </div>
</nav>

<div class="hero-blog">
  <div class="hero-blog-inner">
    <div class="hero-cat">Top DFW House Buyers · Resource Guide</div>
    <h1>{post['h1']}</h1>
    <div class="hero-meta">Published {date_str} · Dallas-Fort Worth, Texas</div>
  </div>
</div>

<div class="content-layout">
  <div class="article-body">
    <a href="/blog/" class="back-link">← All Articles</a>
    <p style="font-size:16px;line-height:1.9;color:#2a3a2a;margin-bottom:24px;font-weight:400">{post['intro']}</p>
    {post['content_html']}

    <div class="cta-inline" style="margin-top:40px">
      <h3>Ready to Get Your Cash Offer?</h3>
      <p>We buy houses anywhere in DFW  -  any condition, any situation. No fees, no repairs, no commissions. Get a fair cash offer within 24 hours and close on your timeline.</p>
      <a href="/#offer">Get My Free Cash Offer →</a>
    </div>

    <div class="related-posts">
      <h3>More Helpful Resources</h3>
      <div class="related-grid">
        <div class="related-card"><a href="/blog/what-is-cash-home-buyer-texas/">What Is a Cash Home Buyer? How the Process Works in Texas</a></div>
        <div class="related-card"><a href="/blog/cash-offer-vs-traditional-sale-texas/">Cash Offer vs. Traditional Sale  -  Which Is Better?</a></div>
        <div class="related-card"><a href="/blog/real-cost-selling-house-texas/">The Real Cost of Selling a House in Texas</a></div>
      </div>
    </div>
  </div>

  <div class="sidebar">
    <div class="sidebar-card">
      <h3>Get Your Free Cash Offer</h3>
      <p>No fees, no repairs, no commissions. We close in as few as 7 days.</p>
      <a href="tel:9722849713" class="phone">📞 972-284-9713</a>
      <a href="/#offer" class="sidebar-btn green">Get Cash Offer →</a>
      <a href="tel:9722849713" class="sidebar-btn">Call Us Now</a>
    </div>
    <div class="sidebar-card">
      <h3>How It Works</h3>
      <p style="font-size:12px;color:#52675f;line-height:1.8;margin:0">
        <strong>1.</strong> Tell us about your property<br>
        <strong>2.</strong> Get a cash offer in 24 hours<br>
        <strong>3.</strong> Choose your closing date<br>
        <strong>4.</strong> Walk away with cash
      </p>
    </div>
  </div>
</div>

<footer>
  © {year} Top DFW House Buyers · <a href="/">topdfwhousebuyers.com</a> · 972-284-9713 · TX License #0657354<br>
  Serving Plano, Frisco, Allen, McKinney, Richardson, The Colony, Lewisville, Flower Mound, Keller, Grapevine, Colleyville, Southlake and all DFW cities
</footer>

</body>
</html>"""


def main():
    print(f"Starting blog generation  -  {datetime.now().isoformat()}")

    # Get topic for this run
    topic = get_next_topic()
    print(f"Topic: {topic['title']}")
    print(f"Slug: {topic['slug']}")
    print(f"Type: {topic['post_type']}")

    # Generate post content
    print("Calling Claude API...")
    post = generate_post(topic)
    print(f"Generated: {post['word_count']} words")

    # Build HTML
    html = build_html_page(post, topic)

    # Save to blog directory
    output_dir = Path(f"blog/{topic['slug']}")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "index.html"

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Saved: {output_file}")
    print(f"URL: https://www.topdfwhousebuyers.com/blog/{topic['slug']}/")
    print("Done!")


if __name__ == "__main__":
    main()
