#!/usr/bin/env python3
"""
Golden Coast Cash Offer - Automated Blog Generator
Southern California market - OC, San Diego, LA
Runs Mon/Wed/Fri/Sat at 8am CT
"""

import os
import json
import re
import anthropic
import time
from datetime import datetime
from pathlib import Path

CITIES = [
    # Orange County
    "Irvine", "Anaheim", "Santa Ana", "Huntington Beach", "Newport Beach",
    "Mission Viejo", "Laguna Hills", "Laguna Niguel", "Lake Forest",
    "San Clemente", "San Juan Capistrano", "Aliso Viejo", "Costa Mesa",
    "Tustin", "Fountain Valley", "Garden Grove", "Fullerton", "Orange",
    "Yorba Linda", "Dana Point", "Laguna Beach", "Brea", "Placentia",
    "Buena Park", "La Habra", "Stanton", "Westminster", "Seal Beach",
    # San Diego
    "San Diego", "Chula Vista", "Oceanside", "Escondido", "El Cajon",
    "Vista", "Carlsbad", "San Marcos", "Santee", "La Mesa",
    "Poway", "National City", "El Cajon", "Spring Valley", "Lemon Grove",
    # Los Angeles
    "Los Angeles", "Long Beach", "Santa Monica", "Pasadena", "Torrance",
    "Malibu", "Beverly Hills", "Glendale", "Burbank", "Pomona",
    "Whittier", "Downey", "Compton", "Inglewood", "Hawthorne",
]

CITY_TOPICS = [
    "How to Sell Your House Fast in {city}, CA - No Fees, No Repairs",
    "We Buy Houses in {city}, CA - Get a Cash Offer in 24 Hours",
    "Sell My House Fast {city} CA - The Complete Guide",
    "Cash Home Buyers in {city}, CA - What You Need to Know",
    "Selling Your {city} Home As-Is - Everything You Need to Know",
    "How to Avoid Foreclosure in {city}, CA",
    "Selling an Inherited Property in {city}, CA - Step-by-Step Guide",
    "Selling a House During Divorce in {city}, CA",
    "Tired Landlord? Sell Your Rental Property in {city}, CA Fast",
    "Relocating from {city}, CA? How to Sell Your Home Fast",
]

EVERGREEN_TOPICS = [
    # DIVORCE
    {"title": "Selling a House During Divorce in California - Complete Guide", "slug": "selling-house-during-divorce-california", "keyword": "selling house during divorce California", "category": "divorce"},
    {"title": "California Community Property Laws and Selling Your Home", "slug": "california-community-property-selling-home", "keyword": "California community property selling home", "category": "divorce"},
    {"title": "How to Sell Your Orange County Home Fast During Divorce", "slug": "sell-home-fast-divorce-orange-county", "keyword": "sell home fast divorce Orange County", "category": "divorce"},
    # FORECLOSURE
    {"title": "How to Stop Foreclosure in California - Your Options", "slug": "stop-foreclosure-california", "keyword": "stop foreclosure California", "category": "foreclosure"},
    {"title": "Pre-Foreclosure in Southern California - What It Means", "slug": "pre-foreclosure-southern-california", "keyword": "pre-foreclosure Southern California", "category": "foreclosure"},
    {"title": "Selling Your SoCal Home Before Foreclosure", "slug": "sell-home-before-foreclosure-california", "keyword": "sell home before foreclosure California", "category": "foreclosure"},
    {"title": "Behind on Mortgage Payments in California? Your Options", "slug": "behind-on-mortgage-payments-california", "keyword": "behind on mortgage payments California", "category": "foreclosure"},
    # INHERITANCE
    {"title": "Selling an Inherited House in California - Complete Guide", "slug": "selling-inherited-house-california", "keyword": "selling inherited house California", "category": "inheritance"},
    {"title": "California Probate Process for Selling a House", "slug": "california-probate-process-selling-house", "keyword": "California probate selling house", "category": "inheritance"},
    {"title": "Selling an Inherited Property in Orange County", "slug": "selling-inherited-property-orange-county", "keyword": "selling inherited property Orange County", "category": "inheritance"},
    # EDUCATION
    {"title": "What Is a Cash Home Buyer? How It Works in California", "slug": "what-is-cash-home-buyer-california", "keyword": "what is a cash home buyer California", "category": "education"},
    {"title": "Cash Offer vs Traditional Sale in California - Which Is Better?", "slug": "cash-offer-vs-traditional-sale-california", "keyword": "cash offer vs traditional sale California", "category": "education"},
    {"title": "The Real Cost of Selling a House in California", "slug": "real-cost-selling-house-california", "keyword": "cost of selling a house California", "category": "education"},
    {"title": "How Fast Can You Sell a House in California?", "slug": "how-fast-sell-house-california", "keyword": "how fast sell house California", "category": "education"},
    {"title": "Selling a House As-Is in California - What Sellers Need to Know", "slug": "selling-house-as-is-california", "keyword": "selling house as-is California", "category": "education"},
    {"title": "California Capital Gains Tax When Selling Your Home", "slug": "california-capital-gains-tax-selling-home", "keyword": "California capital gains tax selling home", "category": "education"},
    {"title": "Is It Better to Sell to a Cash Buyer or Agent in California?", "slug": "cash-buyer-vs-agent-california", "keyword": "cash buyer vs agent California", "category": "education"},
    {"title": "How to Get a Fair Cash Offer on Your California Home", "slug": "fair-cash-offer-california-home", "keyword": "fair cash offer California home", "category": "education"},
    # SITUATIONS
    {"title": "Selling a House With Tenants in California - Landlord Guide", "slug": "selling-house-with-tenants-california", "keyword": "selling house with tenants California", "category": "situations"},
    {"title": "California Tenant Protection Laws - What Landlords Need to Know", "slug": "california-tenant-protection-laws-landlords", "keyword": "California tenant protection laws landlords selling", "category": "situations"},
    {"title": "Selling a Fire-Damaged Home in Southern California", "slug": "sell-fire-damaged-home-southern-california", "keyword": "sell fire damaged home Southern California", "category": "situations"},
    {"title": "Selling a House With Foundation Problems in California", "slug": "selling-house-foundation-problems-california", "keyword": "selling house foundation problems California", "category": "situations"},
    {"title": "How to Sell a Vacant Home in Orange County", "slug": "sell-vacant-home-orange-county", "keyword": "sell vacant home Orange County", "category": "situations"},
    {"title": "Selling a House With Mold in Southern California", "slug": "sell-house-mold-southern-california", "keyword": "sell house mold Southern California", "category": "situations"},
    {"title": "Selling a House With Code Violations in California", "slug": "selling-house-code-violations-california", "keyword": "selling house code violations California", "category": "situations"},
    {"title": "How to Sell a House With a Lien in California", "slug": "sell-house-lien-california", "keyword": "sell house lien California", "category": "situations"},
    {"title": "Downsizing in Orange County - How to Sell Fast", "slug": "downsizing-orange-county-sell-fast", "keyword": "downsizing Orange County sell home", "category": "situations"},
    {"title": "Selling a Rental Property in California - Cash vs 1031", "slug": "selling-rental-property-california", "keyword": "selling rental property California", "category": "situations"},
    {"title": "How to Sell Your California Home When Relocating", "slug": "sell-home-relocating-california", "keyword": "sell home relocating California", "category": "situations"},
    # OC MARKET
    {"title": "Orange County Real Estate Market 2025 - What Sellers Need to Know", "slug": "orange-county-real-estate-market-2025", "keyword": "Orange County real estate market 2025", "category": "market"},
    {"title": "Is Now a Good Time to Sell Your OC Home?", "slug": "good-time-sell-orange-county-home", "keyword": "good time sell Orange County home", "category": "market"},
    {"title": "San Diego Real Estate Market 2025 - Seller Guide", "slug": "san-diego-real-estate-market-2025", "keyword": "San Diego real estate market 2025", "category": "market"},
    {"title": "Southern California Home Prices - What Sellers Need to Know", "slug": "southern-california-home-prices-sellers", "keyword": "Southern California home prices sellers", "category": "market"},
]


def get_next_topic():
    tracking_file = Path("blog/tracking.json")
    if tracking_file.exists():
        with open(tracking_file) as f:
            tracking = json.load(f)
    else:
        tracking = {"posts_written": 0, "city_index": 0, "evergreen_index": 0, "last_post": None}

    posts_written = tracking.get("posts_written", 0)

    if posts_written % 2 == 0:
        city_idx = tracking.get("city_index", 0) % len(CITIES)
        topic_template = CITY_TOPICS[posts_written % len(CITY_TOPICS)]
        city = CITIES[city_idx]
        title = topic_template.format(city=city)
        slug = f"sell-my-house-fast-{city.lower().replace(' ', '-')}-ca-{posts_written}"
        keyword = f"sell my house fast {city} CA"
        post_type = "city"
        tracking["city_index"] = (city_idx + 1) % len(CITIES)
        extra_context = f"Target city: {city}, California (Southern California). Include local context about {city} neighborhoods, the local real estate market, California-specific considerations like tenant laws, high property values, and why sellers in {city} benefit from working with a cash buyer."
    else:
        ev_idx = tracking.get("evergreen_index", 0) % len(EVERGREEN_TOPICS)
        topic = EVERGREEN_TOPICS[ev_idx]
        title = topic["title"]
        slug = topic["slug"]
        keyword = topic["keyword"]
        post_type = "evergreen"
        tracking["evergreen_index"] = (ev_idx + 1) % len(EVERGREEN_TOPICS)
        extra_context = f"Category: {topic['category']}. Write from perspective of someone in this situation in Southern California/Orange County area. Include California-specific laws, costs, and market context."

    tracking["posts_written"] = posts_written + 1
    tracking["last_post"] = datetime.now().isoformat()
    tracking_file.parent.mkdir(exist_ok=True)
    with open(tracking_file, "w") as f:
        json.dump(tracking, f, indent=2)

    return {"title": title, "slug": slug, "keyword": keyword, "post_type": post_type, "extra_context": extra_context}


def generate_post(topic: dict) -> dict:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    prompt = f"""You are an expert real estate SEO content writer for Golden Coast Cash Offer, a cash home buying company serving Southern California.

COMPANY INFO:
- Name: Golden Coast Cash Offer
- Phone: 949-280-5139
- Website: https://www.goldencoastcashoffer.com
- Service area: Orange County (Irvine, Mission Viejo, Newport Beach, Laguna Hills, Lake Forest, San Clemente, San Juan Capistrano, Aliso Viejo, Huntington Beach, Tustin, Fountain Valley, Costa Mesa, Garden Grove, Fullerton, Anaheim, Santa Ana, Orange, Yorba Linda, Dana Point, Laguna Beach, Brea), San Diego, Los Angeles and all of Southern California

ASSIGNMENT:
- Title: {topic['title']}
- Primary keyword: {topic['keyword']}
- Additional context: {topic['extra_context']}
- Word count: 1,200-1,500 words
- Include 3 call-to-action sections
- Tone: Warm, helpful, California casual but professional

REQUIREMENTS:
1. Write genuinely helpful content for Southern California homeowners
2. Use H2 and H3 subheadings naturally
3. Each CTA mentions 949-280-5139 and links to /#offer
4. Include California-specific context - tenant laws, high home values, escrow process, property taxes
5. Meta title under 60 characters
6. Meta description under 160 characters

Return ONLY valid JSON (no markdown, no backticks):
{{
  "meta_title": "...",
  "meta_description": "...",
  "h1": "...",
  "intro": "...(2-3 sentence intro)...",
  "content_html": "...(HTML using only h2, h3, p, ul, ol, li tags)...",
  "word_count": 0,
  "secondary_keywords": ["...", "...", "..."]
}}"""

    prompt_safe = prompt.encode('ascii', errors='replace').decode('ascii')
    # Retry up to 3 times on overload
    for attempt in range(3):
        try:
            message = client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=6000,
                messages=[{"role": "user", "content": prompt_safe}]
            )
            break
        except Exception as e:
            if 'overloaded' in str(e).lower() and attempt < 2:
                print(f"API overloaded - waiting 30 seconds before retry {attempt + 2}/3...")
                time.sleep(30)
            else:
                raise
    raw = message.content[0].text.strip()
    raw = re.sub(r'^```json\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)
    # Try to parse - if it fails, retry with shorter word count
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        print("JSON parse failed - retrying with shorter word count...")
        prompt_short = prompt_safe.replace('1,200-1,500 words', '800-1,000 words')
        message2 = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=6000,
            messages=[{"role": "user", "content": prompt_short}]
        )
        raw2 = message2.content[0].text.strip()
        raw2 = re.sub(r'^```json\s*', '', raw2)
        raw2 = re.sub(r'\s*```$', '', raw2)
        return json.loads(raw2)


def build_html_page(post: dict, topic: dict) -> str:
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
<link rel="canonical" href="https://www.goldencoastcashoffer.com/blog/{topic['slug']}/">
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{post['h1']}",
  "datePublished": "{datetime.now().isoformat()}",
  "publisher": {{
    "@type": "Organization",
    "name": "Golden Coast Cash Offer",
    "telephone": "949-280-5139",
    "url": "https://www.goldencoastcashoffer.com"
  }}
}}
</script>
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {{"@type": "Question","name": "How fast can Golden Coast Cash Offer close on my home?","acceptedAnswer": {{"@type": "Answer","text": "We can close in as few as 7 days anywhere in Southern California. Call us at 949-280-5139."}}}},
    {{"@type": "Question","name": "Do I need to make repairs before selling?","acceptedAnswer": {{"@type": "Answer","text": "Never. We buy houses in any condition - no repairs, no cleaning, no staging required."}}}},
    {{"@type": "Question","name": "Are there any fees or commissions?","acceptedAnswer": {{"@type": "Answer","text": "Zero fees, zero commissions, zero closing costs. What we offer is exactly what you receive."}}}},
    {{"@type": "Question","name": "Do you buy homes with tenants in California?","acceptedAnswer": {{"@type": "Answer","text": "Yes. We buy California properties with tenants in place. You don't need to navigate California's complex tenant protection laws - we handle that after closing."}}}}
  ]
}}
</script>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400&family=Nunito:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#fdfaf5;color:#2a2018;font-family:'Nunito',sans-serif;font-weight:300;line-height:1.6}}
.site-nav{{background:#0f4a63;padding:16px 32px;display:flex;align-items:center;justify-content:space-between;border-bottom:3px solid #e8823a;position:sticky;top:0;z-index:100}}
.nav-logo{{color:#f8d264;font-family:'Cormorant Garamond',serif;font-weight:700;font-size:20px;text-decoration:none}}
.nav-links{{display:flex;align-items:center;gap:20px}}
.nav-links a{{color:rgba(255,255,255,0.7);font-size:12px;font-weight:600;text-decoration:none;letter-spacing:0.05em;text-transform:uppercase}}
.nav-cta{{background:#e8823a;color:#fff !important;padding:9px 18px;border-radius:20px}}
.hero-blog{{background:linear-gradient(160deg,#0f4a63 0%,#1a6b8a 100%);padding:64px 40px;text-align:center;position:relative;overflow:hidden}}
.hero-blog::before{{content:'';position:absolute;inset:0;background:url('https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1200&q=60') center/cover;opacity:0.12}}
.hero-blog-inner{{position:relative;z-index:1;max-width:800px;margin:0 auto}}
.hero-cat{{display:inline-block;background:rgba(232,130,58,0.2);border:1px solid rgba(232,130,58,0.4);color:#f8d264;font-size:10px;font-weight:700;letter-spacing:0.2em;text-transform:uppercase;padding:5px 14px;border-radius:20px;margin-bottom:16px}}
.hero-blog h1{{font-family:'Cormorant Garamond',serif;font-size:clamp(26px,4vw,46px);color:#fff;font-weight:700;line-height:1.15;margin-bottom:16px}}
.hero-meta{{font-size:11px;color:rgba(255,255,255,0.5);letter-spacing:0.1em;text-transform:uppercase}}
.content-layout{{max-width:1100px;margin:0 auto;padding:48px 24px;display:grid;grid-template-columns:1fr 300px;gap:48px;align-items:start}}
@media(max-width:768px){{.content-layout{{grid-template-columns:1fr}}}}
.article-body h2{{font-family:'Cormorant Garamond',serif;font-size:28px;font-weight:700;color:#0f4a63;margin:36px 0 14px;line-height:1.2}}
.article-body h3{{font-size:18px;font-weight:700;color:#1a6b8a;margin:24px 0 10px}}
.article-body p{{font-size:15px;line-height:1.9;color:#4a3a28;margin-bottom:16px}}
.article-body ul,.article-body ol{{padding-left:22px;margin-bottom:16px}}
.article-body li{{font-size:15px;line-height:1.8;color:#4a3a28;margin:6px 0}}
.cta-inline{{background:linear-gradient(135deg,#0f4a63,#1a6b8a);border-left:4px solid #e8823a;padding:24px 28px;margin:32px 0;border-radius:0 12px 12px 0}}
.cta-inline h3{{color:#f8d264;font-size:16px;font-weight:700;margin-bottom:8px;font-family:'Cormorant Garamond',serif}}
.cta-inline p{{color:rgba(255,255,255,0.8);font-size:14px;margin-bottom:16px;line-height:1.7}}
.cta-inline a{{display:inline-block;background:#e8823a;color:#fff;padding:12px 24px;font-weight:700;font-size:13px;text-decoration:none;border-radius:20px}}
.sidebar{{position:sticky;top:80px}}
.sidebar-card{{background:#fff;border:1px solid #ddd5c0;border-top:3px solid #e8823a;padding:24px;margin-bottom:20px;border-radius:0 0 12px 12px}}
.sidebar-card h3{{font-size:15px;font-weight:700;color:#0f4a63;margin-bottom:8px;font-family:'Cormorant Garamond',serif}}
.sidebar-card p{{font-size:13px;color:#7a6a52;line-height:1.6;margin-bottom:16px}}
.sidebar-phone{{font-size:20px;font-weight:700;color:#e8823a;text-decoration:none;display:block;margin-bottom:12px}}
.sidebar-btn{{display:block;background:#0f4a63;color:#fff;padding:12px;font-weight:700;font-size:11px;text-decoration:none;border-radius:20px;letter-spacing:0.06em;text-transform:uppercase;text-align:center;margin-bottom:8px}}
.sidebar-btn.orange{{background:#e8823a}}
.back-link{{display:inline-flex;align-items:center;gap:6px;color:#e8823a;text-decoration:none;font-size:12px;font-weight:600;margin-bottom:28px;letter-spacing:0.05em;text-transform:uppercase}}
footer{{background:#0f4a63;color:rgba(255,255,255,0.5);text-align:center;padding:28px;font-size:12px;border-top:3px solid #e8823a}}
footer a{{color:#f8d264;text-decoration:none}}
</style>
</head>
<body>

<nav class="site-nav">
  <a href="/" class="nav-logo">Golden Coast Cash Offer</a>
  <div class="nav-links">
    <a href="/">Home</a>
    <a href="/blog/">Blog</a>
    <a href="tel:9492805139">949-280-5139</a>
    <a href="/#offer" class="nav-cta">Get Cash Offer</a>
  </div>
</nav>

<div class="hero-blog">
  <div class="hero-blog-inner">
    <div class="hero-cat">Golden Coast Cash Offer · SoCal Resource Guide</div>
    <h1>{post['h1']}</h1>
    <div class="hero-meta">Published {date_str} · Southern California</div>
  </div>
</div>

<div class="content-layout">
  <div class="article-body">
    <a href="/blog/" class="back-link">Back to All Articles</a>
    <p style="font-size:16px;line-height:1.9;color:#3a2a18;margin-bottom:24px;font-weight:400">{post['intro']}</p>
    {post['content_html']}
    <div class="cta-inline" style="margin-top:40px">
      <h3>Ready to Get Your Cash Offer?</h3>
      <p>We buy houses anywhere in Southern California - any condition, any situation. No fees, no repairs, no commissions. Get a fair cash offer within 24 hours.</p>
      <a href="/#offer">Get My Free Cash Offer</a>
    </div>
  </div>

  <div class="sidebar">
    <div class="sidebar-card">
      <h3>Get Your Free Cash Offer</h3>
      <p>No fees, no repairs. Close in 7 days or on your schedule.</p>
      <a href="tel:9492805139" class="sidebar-phone">949-280-5139</a>
      <a href="/#offer" class="sidebar-btn orange">Get Cash Offer</a>
      <a href="tel:9492805139" class="sidebar-btn">Call Us Now</a>
    </div>
    <div class="sidebar-card">
      <h3>How It Works</h3>
      <p style="font-size:12px;color:#7a6a52;line-height:1.8;margin:0">
        <strong>1.</strong> Tell us about your property<br>
        <strong>2.</strong> Get a cash offer in 24 hours<br>
        <strong>3.</strong> Choose your closing date<br>
        <strong>4.</strong> Walk away with cash
      </p>
    </div>
  </div>
</div>

<footer>
  {year} Golden Coast Cash Offer · <a href="/">goldencoastcashoffer.com</a> · 949-280-5139<br>
  Serving Orange County, San Diego, Los Angeles and all of Southern California
</footer>

</body>
</html>"""


def main():
    print(f"Starting blog generation - {datetime.now().isoformat()}")
    topic = get_next_topic()
    print(f"Topic: {topic['title']}")
    print(f"Slug: {topic['slug']}")
    print(f"Type: {topic['post_type']}")
    print("Calling Claude API...")
    post = generate_post(topic)
    print(f"Generated: {post['word_count']} words")
    html = build_html_page(post, topic)
    output_dir = Path(f"blog/{topic['slug']}")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "index.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Saved: {output_file}")
    print(f"URL: https://www.goldencoastcashoffer.com/blog/{topic['slug']}/")
    print("Done!")


if __name__ == "__main__":
    main()
