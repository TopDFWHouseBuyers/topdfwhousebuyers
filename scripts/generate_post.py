#!/usr/bin/env python3
"""
Top DFW House Buyers - Automated Blog Generator
Dallas-Fort Worth market
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
    "Plano", "Frisco", "Allen", "Richardson", "McKinney",
    "The Colony", "Prosper", "Lewisville", "Flower Mound", "Keller",
    "Grapevine", "Colleyville", "Southlake", "North Richland Hills",
    "Arlington", "Garland", "Mesquite", "Grand Prairie", "Carrollton",
    "Euless", "Hurst", "Bedford", "Coppell", "Celina",
    "Forney", "Rockwall", "Rowlett", "Wylie", "Sachse",
    "Fate", "Royse City", "Little Elm", "Aubrey", "Denton",
    "Irving", "Farmers Branch", "Duncanville", "DeSoto", "Cedar Hill",
]

CITY_TOPICS = [
    "How to Sell Your House Fast in {city}, TX - No Fees, No Repairs",
    "We Buy Houses in {city}, TX - Get a Cash Offer in 24 Hours",
    "Sell My House Fast {city} TX - The Complete Guide",
    "Cash Home Buyers in {city}, TX - What You Need to Know",
    "Selling Your {city} Home As-Is - Everything You Need to Know",
    "How to Avoid Foreclosure in {city}, TX",
    "Selling an Inherited Property in {city}, TX - Step-by-Step Guide",
    "Selling a House During Divorce in {city}, TX",
    "Tired Landlord? Sell Your Rental Property in {city}, TX Fast",
    "Relocating from {city}, TX? How to Sell Your Home Fast",
]

EVERGREEN_TOPICS = [
    {"title": "Selling a House During Divorce in Texas - Complete Guide", "slug": "selling-house-during-divorce-texas", "keyword": "selling house during divorce Texas", "category": "divorce"},
    {"title": "Texas Community Property Laws and Selling Your Home", "slug": "texas-community-property-selling-home", "keyword": "Texas community property selling home", "category": "divorce"},
    {"title": "How to Sell Your DFW Home Fast During Divorce", "slug": "sell-home-fast-divorce-dfw", "keyword": "sell home fast divorce DFW", "category": "divorce"},
    {"title": "How to Stop Foreclosure in Texas - Your Options", "slug": "stop-foreclosure-texas", "keyword": "stop foreclosure Texas", "category": "foreclosure"},
    {"title": "Pre-Foreclosure in DFW - What It Means for Homeowners", "slug": "pre-foreclosure-dfw-texas", "keyword": "pre-foreclosure DFW Texas", "category": "foreclosure"},
    {"title": "Selling Your DFW Home Before Foreclosure", "slug": "sell-home-before-foreclosure-texas", "keyword": "sell home before foreclosure Texas", "category": "foreclosure"},
    {"title": "Behind on Mortgage Payments in Texas? Your Options", "slug": "behind-on-mortgage-payments-texas", "keyword": "behind on mortgage payments Texas", "category": "foreclosure"},
    {"title": "Selling an Inherited House in Texas - Complete Guide", "slug": "selling-inherited-house-texas", "keyword": "selling inherited house Texas", "category": "inheritance"},
    {"title": "Texas Probate Process for Selling a House", "slug": "texas-probate-process-selling-house", "keyword": "Texas probate selling house", "category": "inheritance"},
    {"title": "Selling an Inherited Property in DFW - Step by Step", "slug": "selling-inherited-property-dfw", "keyword": "selling inherited property DFW", "category": "inheritance"},
    {"title": "What Is a Cash Home Buyer? How It Works in DFW", "slug": "what-is-cash-home-buyer-dfw", "keyword": "what is a cash home buyer DFW", "category": "education"},
    {"title": "Cash Offer vs Traditional Sale in Texas - Which Is Better?", "slug": "cash-offer-vs-traditional-sale-texas", "keyword": "cash offer vs traditional sale Texas", "category": "education"},
    {"title": "The Real Cost of Selling a House in Texas", "slug": "real-cost-selling-house-texas", "keyword": "cost of selling a house Texas", "category": "education"},
    {"title": "How Fast Can You Sell a House in DFW?", "slug": "how-fast-sell-house-dfw", "keyword": "how fast sell house DFW", "category": "education"},
    {"title": "Selling a House As-Is in Texas - What Sellers Need to Know", "slug": "selling-house-as-is-texas", "keyword": "selling house as-is Texas", "category": "education"},
    {"title": "Is It Better to Sell to a Cash Buyer or Agent in Texas?", "slug": "cash-buyer-vs-agent-texas", "keyword": "cash buyer vs agent Texas", "category": "education"},
    {"title": "How to Get a Fair Cash Offer on Your DFW Home", "slug": "fair-cash-offer-dfw-home", "keyword": "fair cash offer DFW home", "category": "education"},
    {"title": "What Happens at a Cash Home Sale Closing in Texas?", "slug": "cash-home-sale-closing-texas", "keyword": "cash home sale closing Texas", "category": "education"},
    {"title": "Texas Capital Gains Tax When Selling Your Home", "slug": "texas-capital-gains-tax-selling-home", "keyword": "Texas capital gains tax selling home", "category": "education"},
    {"title": "What DFW Homeowners Need to Know About Cash Buyers in 2026", "slug": "dfw-homeowners-cash-buyers-2026", "keyword": "DFW cash buyers 2026", "category": "education"},
    {"title": "Selling a House With Tenants in Texas - Landlord Guide", "slug": "selling-house-with-tenants-texas", "keyword": "selling house with tenants Texas", "category": "situations"},
    {"title": "Selling a Fire-Damaged Home in DFW", "slug": "sell-fire-damaged-home-dfw", "keyword": "sell fire damaged home DFW", "category": "situations"},
    {"title": "Selling a House With Foundation Problems in Texas", "slug": "selling-house-foundation-problems-texas", "keyword": "selling house foundation problems Texas", "category": "situations"},
    {"title": "How to Sell a Vacant Home in DFW", "slug": "sell-vacant-home-dfw", "keyword": "sell vacant home DFW", "category": "situations"},
    {"title": "Selling a House With Mold in Texas", "slug": "sell-house-mold-texas", "keyword": "sell house mold Texas", "category": "situations"},
    {"title": "How to Sell a House With a Lien in Texas", "slug": "sell-house-lien-texas", "keyword": "sell house lien Texas", "category": "situations"},
    {"title": "Downsizing in DFW - How to Sell Your Home Fast", "slug": "downsizing-dfw-sell-fast", "keyword": "downsizing DFW sell home", "category": "situations"},
    {"title": "Selling a Rental Property in Texas - Cash vs 1031", "slug": "selling-rental-property-texas", "keyword": "selling rental property Texas", "category": "situations"},
    {"title": "How to Sell Your Texas Home When Relocating", "slug": "sell-home-relocating-texas", "keyword": "sell home relocating Texas", "category": "situations"},
    {"title": "Selling a House With Code Violations in Texas", "slug": "selling-house-code-violations-texas", "keyword": "selling house code violations Texas", "category": "situations"},
    {"title": "How to Sell a House With Back Taxes in Texas", "slug": "sell-house-back-taxes-texas", "keyword": "sell house back taxes Texas", "category": "situations"},
    {"title": "Selling a House in an HOA Community in DFW", "slug": "selling-house-hoa-dfw", "keyword": "selling house HOA DFW", "category": "situations"},
    {"title": "DFW Real Estate Market 2026 - What Sellers Need to Know", "slug": "dfw-real-estate-market-2026", "keyword": "DFW real estate market 2026", "category": "market"},
    {"title": "Is Now a Good Time to Sell Your DFW Home in 2026?", "slug": "good-time-sell-dfw-home-2026", "keyword": "good time sell DFW home 2026", "category": "market"},
    {"title": "North Texas Home Prices 2026 - What Sellers Need to Know", "slug": "north-texas-home-prices-2026", "keyword": "North Texas home prices 2026", "category": "market"},
    {"title": "Why DFW Cash Home Sales Are Rising in 2026", "slug": "dfw-cash-home-sales-rising-2026", "keyword": "DFW cash home sales 2026", "category": "market"},
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
        slug = f"sell-my-house-fast-{city.lower().replace(' ', '-')}-tx-{posts_written}"
        keyword = f"sell my house fast {city} TX"
        post_type = "city"
        tracking["city_index"] = (city_idx + 1) % len(CITIES)
        extra_context = f"Target city: {city}, Texas (Dallas-Fort Worth). Include local context about {city} neighborhoods, the local real estate market, Texas-specific considerations, and why sellers in {city} benefit from working with a cash buyer."
    else:
        ev_idx = tracking.get("evergreen_index", 0) % len(EVERGREEN_TOPICS)
        topic = EVERGREEN_TOPICS[ev_idx]
        title = topic["title"]
        slug = topic["slug"]
        keyword = topic["keyword"]
        post_type = "evergreen"
        tracking["evergreen_index"] = (ev_idx + 1) % len(EVERGREEN_TOPICS)
        extra_context = f"Category: {topic['category']}. Write from perspective of someone in this situation in the Dallas-Fort Worth area. Include Texas-specific laws, costs, and market context."

    tracking["posts_written"] = posts_written + 1
    tracking["last_post"] = datetime.now().isoformat()
    tracking_file.parent.mkdir(exist_ok=True)
    with open(tracking_file, "w") as f:
        json.dump(tracking, f, indent=2)

    return {"title": title, "slug": slug, "keyword": keyword, "post_type": post_type, "extra_context": extra_context}


def clean_json(text):
    """Strip markdown fences and extract JSON object."""
    text = re.sub(r'^```json\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    text = text.strip()
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1:
        text = text[start:end+1]
    return text


def repair_json(text):
    """
    Attempt to fix common JSON breakage caused by unescaped double quotes
    inside HTML attribute values within the content_html field.
    Replaces any double-quoted HTML attributes with single-quoted ones.
    """
    text = re.sub(r'(?<=\s)(href|src|class|id|style|rel|target)="([^"]*)"', r"\1='\2'", text)
    return text


def generate_post(topic: dict) -> dict:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    prompt = f"""You are an expert real estate SEO content writer for Top DFW House Buyers, a cash home buying company in Dallas-Fort Worth, Texas.

COMPANY INFO:
- Name: Top DFW House Buyers
- Phone: 972-284-9713
- Website: https://www.topdfwhousebuyers.com
- Service area: Plano, Frisco, Allen, Richardson, McKinney, The Colony, Lewisville, Flower Mound, Keller, Grapevine, Colleyville, Southlake, North Richland Hills, Arlington, Garland, Mesquite, Grand Prairie, Carrollton, Euless, Hurst, Bedford, Coppell, Celina, Prosper and all DFW cities
- TX Real Estate License #0657354

ASSIGNMENT:
- Title: {topic['title']}
- Primary keyword: {topic['keyword']}
- Additional context: {topic['extra_context']}
- Word count: 1,200-1,500 words
- Include 3 call-to-action sections
- Tone: Warm, helpful, professional but conversational

REQUIREMENTS:
1. Write genuinely helpful content for Dallas-Fort Worth homeowners
2. Use H2 and H3 subheadings naturally
3. Each CTA mentions 972-284-9713 and links to /#offer
4. Include Texas-specific context - community property laws, homestead exemption, no state income tax, Texas foreclosure timeline, HOA rules
5. Meta title under 60 characters
6. Meta description under 160 characters
7. CRITICAL: In content_html, use single quotes for ALL HTML attributes (e.g. href='/#offer' not href="/#offer"). This is required so the JSON stays valid.

Return ONLY valid JSON (no markdown, no backticks):
{{
  "meta_title": "...",
  "meta_description": "...",
  "h1": "...",
  "intro": "...(2-3 sentence intro)...",
  "content_html": "...(HTML using only h2, h3, p, ul, ol, li, a tags — single quotes on all attributes)...",
  "word_count": 0,
  "secondary_keywords": ["...", "...", "..."]
}}"""

    prompt_safe = prompt.encode('ascii', errors='replace').decode('ascii')

    for attempt in range(3):
        try:
            message = client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=8000,
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

    try:
        return json.loads(clean_json(raw))
    except json.JSONDecodeError:
        print("JSON parse failed - attempting repair...")
        try:
            return json.loads(repair_json(clean_json(raw)))
        except json.JSONDecodeError:
            print("Repair failed - retrying API with shorter word count...")
            prompt_short = prompt_safe.replace('1,200-1,500 words', '700-900 words')
            message2 = client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=6000,
                messages=[{"role": "user", "content": prompt_short}]
            )
            raw2 = message2.content[0].text.strip()
            try:
                return json.loads(clean_json(raw2))
            except json.JSONDecodeError:
                return json.loads(repair_json(clean_json(raw2)))


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
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {{"@type": "Question","name": "How fast can Top DFW House Buyers close on my home?","acceptedAnswer": {{"@type": "Answer","text": "We can close in as few as 7 days anywhere in DFW. Call us at 972-284-9713."}}}},
    {{"@type": "Question","name": "Do I need to make repairs before selling?","acceptedAnswer": {{"@type": "Answer","text": "Never. We buy houses in any condition - no repairs, no cleaning required."}}}},
    {{"@type": "Question","name": "Are there any fees or commissions?","acceptedAnswer": {{"@type": "Answer","text": "Zero fees, zero commissions, zero closing costs. What we offer is exactly what you receive."}}}},
    {{"@type": "Question","name": "What areas of DFW do you buy houses in?","acceptedAnswer": {{"@type": "Answer","text": "We buy houses throughout Dallas-Fort Worth including Plano, Frisco, Allen, McKinney, Richardson, Keller, Arlington, Garland, Mesquite, Grand Prairie and all surrounding cities."}}}}
  ]
}}
</script>
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-QSBN8EDR9Z"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', 'G-QSBN8EDR9Z');
</script>
<!-- Microsoft Clarity -->
<script type="text/javascript">
    (function(c,l,a,r,i,t,y){{
        c[a]=c[a]||function(){{(c[a].q=c[a].q||[]).push(arguments)}};
        t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
        y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
    }})(window, document, "clarity", "script", "wiurnc9zu7");
</script>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Montserrat:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#f8faf8;color:#1a1f1a;font-family:'Montserrat',sans-serif;font-weight:300;line-height:1.6}}
.site-nav{{background:#0a0a0a;padding:16px 32px;display:flex;align-items:center;justify-content:space-between;border-bottom:3px solid #4ab840;position:sticky;top:0;z-index:100}}
.nav-logo{{color:#4ab840;font-family:'Playfair Display',serif;font-weight:700;font-size:18px;text-decoration:none}}
.nav-links{{display:flex;align-items:center;gap:20px}}
.nav-links a{{color:rgba(255,255,255,0.7);font-size:12px;font-weight:600;text-decoration:none;letter-spacing:0.05em;text-transform:uppercase}}
.nav-cta{{background:#4ab840;color:#fff !important;padding:9px 18px;border-radius:2px}}
.hero-blog{{background:#0a0a0a;padding:64px 40px;text-align:center;position:relative;overflow:hidden}}
.hero-blog::before{{content:'';position:absolute;inset:0;background:url('https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=1200&q=60') center/cover;opacity:0.1}}
.hero-blog-inner{{position:relative;z-index:1;max-width:800px;margin:0 auto}}
.hero-cat{{display:inline-block;background:rgba(74,184,64,0.15);border:1px solid rgba(74,184,64,0.35);color:#6dd962;font-size:10px;font-weight:700;letter-spacing:0.2em;text-transform:uppercase;padding:5px 14px;border-radius:2px;margin-bottom:16px}}
.hero-blog h1{{font-family:'Playfair Display',serif;font-size:clamp(26px,4vw,46px);color:#fff;font-weight:700;line-height:1.15;margin-bottom:16px}}
.hero-meta{{font-size:11px;color:rgba(255,255,255,0.4);letter-spacing:0.1em;text-transform:uppercase}}
.content-layout{{max-width:1100px;margin:0 auto;padding:48px 24px;display:grid;grid-template-columns:1fr 300px;gap:48px;align-items:start}}
@media(max-width:768px){{.content-layout{{grid-template-columns:1fr}}}}
.article-body h2{{font-family:'Playfair Display',serif;font-size:28px;font-weight:700;color:#1a1f1a;margin:36px 0 14px;line-height:1.2}}
.article-body h3{{font-size:18px;font-weight:700;color:#2d402d;margin:24px 0 10px}}
.article-body p{{font-size:15px;line-height:1.9;color:#3a4a3a;margin-bottom:16px}}
.article-body ul,.article-body ol{{padding-left:22px;margin-bottom:16px}}
.article-body li{{font-size:15px;line-height:1.8;color:#3a4a3a;margin:6px 0}}
.cta-inline{{background:#0a0a0a;border-left:4px solid #4ab840;padding:24px 28px;margin:32px 0}}
.cta-inline h3{{color:#4ab840;font-size:16px;font-weight:700;margin-bottom:8px;font-family:'Playfair Display',serif}}
.cta-inline p{{color:rgba(255,255,255,0.7);font-size:14px;margin-bottom:16px;line-height:1.7}}
.cta-inline a{{display:inline-block;background:#4ab840;color:#fff;padding:12px 24px;font-weight:700;font-size:13px;text-decoration:none;border-radius:2px}}
.sidebar{{position:sticky;top:80px}}
.sidebar-card{{background:#fff;border:1px solid #d4e4d2;border-top:3px solid #4ab840;padding:24px;margin-bottom:20px}}
.sidebar-card h3{{font-size:15px;font-weight:700;color:#1a1f1a;margin-bottom:8px;font-family:'Playfair Display',serif}}
.sidebar-card p{{font-size:13px;color:#52675f;line-height:1.6;margin-bottom:16px}}
.sidebar-phone{{font-size:20px;font-weight:700;color:#4ab840;text-decoration:none;display:block;margin-bottom:12px}}
.sidebar-btn{{display:block;background:#0a0a0a;color:#fff;padding:12px;font-weight:700;font-size:11px;text-decoration:none;border-radius:2px;letter-spacing:0.06em;text-transform:uppercase;text-align:center;margin-bottom:8px}}
.sidebar-btn.green{{background:#4ab840}}
.back-link{{display:inline-flex;align-items:center;gap:6px;color:#4ab840;text-decoration:none;font-size:12px;font-weight:600;margin-bottom:28px;letter-spacing:0.05em;text-transform:uppercase}}
.review-cta{{background:#f8faf8;border:1px solid #d4e4d2;padding:20px;margin-top:32px;text-align:center}}
.review-cta p{{font-size:13px;color:#52675f;margin-bottom:12px}}
.review-cta a{{display:inline-block;background:#4ab840;color:#fff;padding:10px 20px;font-weight:700;font-size:12px;text-decoration:none;border-radius:2px}}
footer{{background:#0a0a0a;color:rgba(255,255,255,0.4);text-align:center;padding:28px;font-size:12px;border-top:3px solid #4ab840}}
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

<div class="hero-blog">
  <div class="hero-blog-inner">
    <div class="hero-cat">Top DFW House Buyers · DFW Resource Guide</div>
    <h1>{post['h1']}</h1>
    <div class="hero-meta">Published {date_str} · Dallas-Fort Worth, Texas</div>
  </div>
</div>

<div class="content-layout">
  <div class="article-body">
    <a href="/blog/" class="back-link">Back to All Articles</a>
    <p style="font-size:16px;line-height:1.9;color:#2a3a2a;margin-bottom:24px;font-weight:400">{post['intro']}</p>
    {post['content_html']}
    <div class="cta-inline" style="margin-top:40px">
      <h3>Ready to Get Your Cash Offer?</h3>
      <p>We buy houses anywhere in DFW - any condition, any situation. No fees, no repairs, no commissions. Get a fair cash offer within 24 hours.</p>
      <a href="/#offer">Get My Free Cash Offer</a>
    </div>
    <div class="review-cta">
      <p>Happy with your experience? We would love a Google review.</p>
      <a href="https://share.google/vGlYZ46PBCsE6BPhz" target="_blank" rel="noopener">Leave Us a Google Review</a>
    </div>
  </div>

  <div class="sidebar">
    <div class="sidebar-card">
      <h3>Get Your Free Cash Offer</h3>
      <p>No fees, no repairs. Close in 7 days or on your schedule.</p>
      <a href="tel:9722849713" class="sidebar-phone">972-284-9713</a>
      <a href="/#offer" class="sidebar-btn green">Get Cash Offer</a>
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
    <div class="sidebar-card">
      <h3>Happy With Your Sale?</h3>
      <p style="font-size:12px;color:#52675f;line-height:1.6;margin-bottom:12px">Leave us a Google review.</p>
      <a href="https://share.google/vGlYZ46PBCsE6BPhz" target="_blank" rel="noopener" style="display:block;background:#4ab840;color:#fff;padding:10px;font-weight:700;font-size:11px;text-decoration:none;border-radius:2px;letter-spacing:0.06em;text-transform:uppercase;text-align:center">Leave a Google Review</a>
    </div>
  </div>
</div>

<footer>
  {year} Top DFW House Buyers · <a href="/">topdfwhousebuyers.com</a> · 972-284-9713 · TX License #0657354<br>
  Serving Plano, Frisco, Allen, McKinney, Richardson, The Colony, Lewisville, Flower Mound, Keller, Grapevine, Colleyville, Southlake and all DFW cities<br><br>
  <a href="https://share.google/vGlYZ46PBCsE6BPhz" target="_blank" rel="noopener" style="color:#4ab840">Leave us a Google Review</a>
  &nbsp;·&nbsp;
  <a href="https://www.facebook.com/TopDFWHouseBuyers/" target="_blank" rel="noopener" style="color:#4ab840">Facebook</a>
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
    print(f"URL: https://www.topdfwhousebuyers.com/blog/{topic['slug']}/")
    print("Done!")


if __name__ == "__main__":
    main()
