#!/usr/bin/env python3
"""
Top DFW House Buyers — City Landing Page Generator
Generates dedicated SEO landing pages for each target city
Run once: python scripts/generate_cities.py
"""

import os
import json
import re
import anthropic
from datetime import datetime
from pathlib import Path

CITIES = [
    {"name": "Plano", "county": "Collin", "zip": "75023", "pop": "285,000", "notes": "one of the safest and most affluent cities in Texas"},
    {"name": "Frisco", "county": "Collin", "zip": "75034", "pop": "200,000", "notes": "one of the fastest-growing cities in the US"},
    {"name": "Allen", "county": "Collin", "zip": "75002", "pop": "105,000", "notes": "a thriving suburb known for top-rated schools"},
    {"name": "Richardson", "county": "Dallas", "zip": "75080", "pop": "120,000", "notes": "home to the Telecom Corridor and UT Dallas"},
    {"name": "The Colony", "county": "Denton", "zip": "75056", "pop": "42,000", "notes": "a lakeside community on Lewisville Lake"},
    {"name": "Prosper", "county": "Collin", "zip": "75078", "pop": "35,000", "notes": "one of the fastest-growing towns in North Texas"},
    {"name": "Lewisville", "county": "Denton", "zip": "75067", "pop": "110,000", "notes": "a diverse city with easy access to DFW airport"},
    {"name": "Carrollton", "county": "Dallas", "zip": "75006", "pop": "135,000", "notes": "a well-established suburb with strong community ties"},
    {"name": "Coppell", "county": "Dallas", "zip": "75019", "pop": "42,000", "notes": "an upscale community known for excellent schools"},
    {"name": "Celina", "county": "Collin", "zip": "75009", "pop": "30,000", "notes": "a rapidly growing small town in Collin County"},
    {"name": "McKinney", "county": "Collin", "zip": "75069", "pop": "200,000", "notes": "consistently rated one of the best places to live in America"},
    {"name": "Hurst", "county": "Tarrant", "zip": "76053", "pop": "40,000", "notes": "a Mid-Cities community conveniently located near DFW airport"},
    {"name": "Euless", "county": "Tarrant", "zip": "76039", "pop": "55,000", "notes": "a diverse Mid-Cities community in the heart of DFW"},
    {"name": "Bedford", "county": "Tarrant", "zip": "76021", "pop": "50,000", "notes": "a family-friendly Mid-Cities community"},
    {"name": "Arlington", "county": "Tarrant", "zip": "76010", "pop": "395,000", "notes": "home to the Dallas Cowboys and Texas Rangers"},
    {"name": "Grand Prairie", "county": "Dallas", "zip": "75050", "pop": "195,000", "notes": "a diverse city between Dallas and Fort Worth"},
    {"name": "Garland", "county": "Dallas", "zip": "75040", "pop": "240,000", "notes": "a large suburban city east of Dallas"},
    {"name": "Mesquite", "county": "Dallas", "zip": "75149", "pop": "145,000", "notes": "a working-class suburb southeast of Dallas"},
    {"name": "Keller", "county": "Tarrant", "zip": "76248", "pop": "48,000", "notes": "an affluent suburb in Tarrant County known for top schools"},
    {"name": "Southlake", "county": "Tarrant", "zip": "76092", "pop": "32,000", "notes": "one of the wealthiest cities in Texas with luxury homes"},
    {"name": "Grapevine", "county": "Tarrant", "zip": "76051", "pop": "55,000", "notes": "a historic city known for its wine country and Main Street"},
]

def generate_city_content(city: dict) -> dict:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    prompt = f"""You are an expert real estate SEO content writer for Top DFW House Buyers, a cash home buying company.

COMPANY INFO:
- Name: Top DFW House Buyers
- Phone: 972-284-9713
- Website: https://www.topdfwhousebuyers.com
- License: TX Real Estate License #0657354

ASSIGNMENT: Write a city-specific landing page for {city['name']}, Texas.

CITY DETAILS:
- City: {city['name']}, {city['county']} County, TX {city['zip']}
- Population: approximately {city['pop']}
- Local context: {city['notes']}

TARGET KEYWORD: "sell my house fast {city['name']} TX"

REQUIREMENTS:
1. Write 600-800 words of unique, helpful content
2. Include local {city['name']} context — neighborhoods, common seller situations in this area
3. 3 H2 sections with natural subheadings
4. 2 CTA sections mentioning 972-284-9713
5. Conversational, empathetic tone
6. Meta title under 60 chars
7. Meta description under 160 chars
8. DO NOT mention specific streets or addresses you're not sure about

Return ONLY valid JSON (no markdown, no backticks):
{{
  "meta_title": "...",
  "meta_description": "...",
  "h1": "We Buy Houses in {city['name']}, TX — Fast Cash Offers",
  "intro": "...(2-3 sentence intro)...",
  "content_html": "...(HTML using only h2, p, ul, li tags)...",
  "why_sellers_title": "Why {city['name']} Homeowners Choose Us",
  "why_sellers_points": ["...", "...", "...", "..."]
}}"""

    prompt_safe = prompt.encode('ascii', errors='replace').decode('ascii')

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt_safe}]
    )

    raw = message.content[0].text.strip()
    raw = re.sub(r'^```json\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)
    return json.loads(raw)


def build_city_page(content: dict, city: dict) -> str:
    slug = city['name'].lower().replace(' ', '-')
    year = datetime.now().year

    why_points = ''.join([f'<li style="font-size:15px;line-height:1.8;color:#3a4a3a;margin:8px 0">{p}</li>' for p in content.get('why_sellers_points', [])])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{content['meta_title']}</title>
<meta name="description" content="{content['meta_description']}">
<meta property="og:title" content="{content['meta_title']}">
<meta property="og:description" content="{content['meta_description']}">
<link rel="canonical" href="https://www.topdfwhousebuyers.com/{slug}/">
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "RealEstateAgent",
  "name": "Top DFW House Buyers",
  "telephone": "972-284-9713",
  "url": "https://www.topdfwhousebuyers.com",
  "areaServed": "{city['name']}, Texas"
}}
</script>
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {{
      "@type": "Question",
      "name": "How fast can you buy my house in {city['name']}, TX?",
      "acceptedAnswer": {{
        "@type": "Answer",
        "text": "We can close in as few as 7 days in {city['name']}. If you need more time, we work around your schedule. Call us at 972-284-9713 to discuss your timeline."
      }}
    }},
    {{
      "@type": "Question",
      "name": "Do I need to make repairs before selling my {city['name']} home?",
      "acceptedAnswer": {{
        "@type": "Answer",
        "text": "Never. We buy houses in {city['name']} in any condition — foundation issues, roof damage, outdated systems, or heavy wear. You don't spend a single dollar on repairs."
      }}
    }},
    {{
      "@type": "Question",
      "name": "Are there any fees or commissions when selling to Top DFW House Buyers?",
      "acceptedAnswer": {{
        "@type": "Answer",
        "text": "Zero fees. Zero commissions. Zero closing costs. We cover all closing costs. What we offer is exactly what you receive at closing — no deductions."
      }}
    }},
    {{
      "@type": "Question",
      "name": "How do you determine your cash offer for my {city['name']} property?",
      "acceptedAnswer": {{
        "@type": "Answer",
        "text": "We analyze the property's condition, location, and recent comparable sales in {city['name']}. We're transparent about how we arrive at our number and show you exactly how we calculated it."
      }}
    }},
    {{
      "@type": "Question",
      "name": "What types of {city['name']} properties do you buy?",
      "acceptedAnswer": {{
        "@type": "Answer",
        "text": "We buy all types of residential properties in {city['name']} — single family homes, townhouses, condos, duplexes, and multi-family properties. Any condition, any situation."
      }}
    }}
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
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Montserrat:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --navy:#1a1f1a;--gold:#4ab840;--gold-light:#6dd962;
  --cream:#f8faf8;--white:#fff;--border:#d4e4d2;--muted:#52675f;
}}
body{{background:var(--cream);color:#1a1f1a;font-family:'Montserrat',sans-serif;font-weight:300;line-height:1.6}}
.site-nav{{background:#0a0a0a;padding:14px 32px;display:flex;align-items:center;justify-content:space-between;border-bottom:3px solid #4ab840;position:sticky;top:0;z-index:100}}
.nav-logo{{color:#4ab840;font-weight:700;font-size:18px;text-decoration:none;font-family:'Playfair Display',serif}}
.nav-logo span{{color:#fff}}
.nav-links{{display:flex;align-items:center;gap:20px}}
.nav-links a{{color:rgba(255,255,255,0.7);font-size:12px;font-weight:600;text-decoration:none;letter-spacing:0.05em;text-transform:uppercase}}
.nav-cta{{background:#4ab840;color:#fff !important;padding:9px 18px;border-radius:2px}}
.hero{{background:#1a1f1a;padding:60px 40px;position:relative;overflow:hidden}}
.hero::before{{content:'';position:absolute;inset:0;background:url('https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=1400&q=70') center/cover;opacity:0.12}}
.hero-inner{{position:relative;z-index:1;max-width:1100px;margin:0 auto;display:grid;grid-template-columns:1fr 420px;gap:48px;align-items:center}}
@media(max-width:900px){{.hero-inner{{grid-template-columns:1fr}}}}
.hero-eyebrow{{display:inline-flex;align-items:center;gap:8px;background:rgba(74,184,64,0.15);border:1px solid rgba(74,184,64,0.35);padding:5px 12px;border-radius:2px;font-size:10px;font-weight:700;letter-spacing:0.2em;text-transform:uppercase;color:#6dd962;margin-bottom:20px}}
.hero h1{{font-family:'Playfair Display',serif;font-size:clamp(32px,4vw,52px);font-weight:900;color:#fff;line-height:1.05;letter-spacing:-0.02em;margin-bottom:20px}}
.hero h1 em{{font-style:italic;color:#6dd962;font-weight:400}}
.hero-sub{{font-size:16px;color:rgba(255,255,255,0.7);line-height:1.7;margin-bottom:28px}}
.hero-badges{{display:flex;gap:10px;flex-wrap:wrap}}
.badge{{display:flex;align-items:center;gap:6px;background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.15);padding:7px 12px;border-radius:2px;font-size:11px;color:rgba(255,255,255,0.8);font-weight:500}}
.badge::before{{content:'✓';color:#4ab840;font-weight:700}}
.hero-form{{background:#fff;border-top:4px solid #4ab840;padding:28px 24px;box-shadow:0 20px 60px rgba(0,0,0,0.4)}}
.form-headline{{font-family:'Playfair Display',serif;font-size:20px;font-weight:700;color:#1a1f1a;margin-bottom:4px}}
.form-sub{{font-size:12px;color:var(--muted);margin-bottom:20px}}
.field-group{{margin-bottom:12px}}
.field-group label{{display:block;font-size:10px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:var(--muted);margin-bottom:4px}}
.field-group input,.field-group select{{width:100%;padding:11px 13px;border:1.5px solid var(--border);border-radius:2px;font-family:'Montserrat',sans-serif;font-size:13px;color:#1a1f1a;outline:none;transition:border-color .15s}}
.field-group input:focus,.field-group select:focus{{border-color:#4ab840}}
.field-grid{{display:grid;grid-template-columns:1fr 1fr;gap:10px}}
.submit-btn{{width:100%;padding:14px;background:#000;border:none;color:#fff;font-family:'Montserrat',sans-serif;font-weight:700;font-size:13px;letter-spacing:0.05em;text-transform:uppercase;cursor:pointer;border-radius:2px;transition:all .2s;margin-top:4px}}
.submit-btn:hover{{background:#222;transform:translateY(-1px)}}
.form-guarantee{{text-align:center;font-size:10px;color:var(--muted);margin-top:10px}}
.form-success{{display:none;text-align:center;padding:24px 16px}}
.form-success .check{{font-size:40px;margin-bottom:10px}}
.form-success h3{{font-family:'Playfair Display',serif;font-size:20px;color:#1a1f1a;margin-bottom:8px}}
.form-success p{{font-size:13px;color:var(--muted);line-height:1.6}}
.content-wrap{{max-width:1100px;margin:0 auto;padding:56px 40px;display:grid;grid-template-columns:1fr 320px;gap:48px;align-items:start}}
@media(max-width:768px){{.content-wrap{{grid-template-columns:1fr;padding:40px 24px}}}}
.main-content h2{{font-family:'Playfair Display',serif;font-size:28px;font-weight:700;color:#1a1f1a;margin:32px 0 14px;line-height:1.2}}
.main-content p{{font-size:15px;line-height:1.9;color:#3a4a3a;margin-bottom:16px}}
.main-content ul{{padding-left:20px;margin-bottom:16px}}
.main-content li{{font-size:15px;line-height:1.8;color:#3a4a3a;margin:6px 0}}
.why-box{{background:#1a1f1a;padding:32px;margin:32px 0}}
.why-box h2{{font-family:'Playfair Display',serif;font-size:22px;color:#fff;margin-bottom:20px}}
.why-box ul{{list-style:none;padding:0}}
.why-box li{{padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.1);color:rgba(255,255,255,0.8);font-size:14px;display:flex;align-items:flex-start;gap:10px}}
.why-box li::before{{content:'✓';color:#4ab840;font-weight:700;flex-shrink:0;margin-top:2px}}
.why-box li:last-child{{border:none}}
.cta-box{{background:#f8faf8;border:1px solid var(--border);border-left:4px solid #4ab840;padding:24px 28px;margin:32px 0}}
.cta-box h3{{font-size:16px;font-weight:700;color:#1a1f1a;margin-bottom:8px}}
.cta-box p{{font-size:13px;color:var(--muted);margin-bottom:16px;line-height:1.7}}
.cta-box a{{display:inline-block;background:#1a1f1a;color:#fff;padding:12px 24px;font-weight:700;font-size:12px;text-decoration:none;border-radius:2px;letter-spacing:0.06em;text-transform:uppercase}}
.sidebar{{position:sticky;top:80px}}
.sidebar-card{{background:#fff;border:1px solid var(--border);border-top:3px solid #4ab840;padding:24px;margin-bottom:20px}}
.sidebar-card h3{{font-size:14px;font-weight:700;color:#1a1f1a;margin-bottom:8px}}
.sidebar-card p{{font-size:12px;color:var(--muted);line-height:1.6;margin-bottom:14px}}
.sidebar-phone{{font-size:22px;font-weight:700;color:#4ab840;text-decoration:none;display:block;margin-bottom:12px}}
.sidebar-btn{{display:block;background:#1a1f1a;color:#fff;padding:12px;font-weight:700;font-size:11px;text-decoration:none;border-radius:2px;letter-spacing:0.06em;text-transform:uppercase;text-align:center;margin-bottom:8px}}
.sidebar-btn.green{{background:#4ab840}}
.cities-strip{{background:#1a1f1a;padding:40px}}
.cities-strip h2{{font-family:'Playfair Display',serif;font-size:24px;color:#fff;margin-bottom:24px;text-align:center}}
.cities-grid{{display:grid;grid-template-columns:repeat(5,1fr);gap:8px;max-width:900px;margin:0 auto}}
@media(max-width:640px){{.cities-grid{{grid-template-columns:repeat(3,1fr)}}}}
.city-pill{{padding:10px;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);color:rgba(255,255,255,0.7);font-size:11px;font-weight:600;text-decoration:none;text-align:center;transition:all .15s;border-radius:2px;display:block}}
.city-pill:hover{{background:#4ab840;color:#fff;border-color:#4ab840}}
.city-pill.active{{background:#4ab840;color:#fff;border-color:#4ab840}}
footer{{background:#0a0a0a;color:rgba(255,255,255,0.4);text-align:center;padding:28px;font-size:11px;border-top:3px solid #4ab840}}
footer a{{color:#4ab840;text-decoration:none}}
.sticky-cta{{position:fixed;bottom:0;left:0;right:0;background:#1a1f1a;border-top:2px solid #4ab840;padding:12px 20px;display:none;align-items:center;justify-content:space-between;gap:12px;z-index:200}}
@media(max-width:640px){{.sticky-cta{{display:flex}}}}
.sticky-cta-text{{font-size:12px;color:rgba(255,255,255,0.7);font-weight:500}}
.sticky-cta-btn{{padding:10px 20px;background:#4ab840;border:none;color:#fff;font-weight:700;font-size:12px;letter-spacing:0.08em;text-transform:uppercase;cursor:pointer;border-radius:2px;white-space:nowrap;text-decoration:none}}
</style>
</head>
<body>

<nav class="site-nav">
  <a href="/" class="nav-logo">Top<span>DFW</span> House Buyers</a>
  <div class="nav-links">
    <a href="/">Home</a>
    <a href="/blog/">Blog</a>
    <a href="tel:9722849713">972-284-9713</a>
    <a href="/#offer" class="nav-cta">Get Cash Offer</a>
  </div>
</nav>

<section class="hero">
  <div class="hero-inner">
    <div>
      <div class="hero-eyebrow">{city['name']}, {city['county']} County, TX</div>
      <h1>{content['h1'].replace('Fast Cash Offers', '<em>Fast Cash Offers</em>')}</h1>
      <p class="hero-sub">No repairs. No agent fees. No commissions. Get a fair cash offer within 24 hours and close on your timeline — as fast as 7 days.</p>
      <div class="hero-badges">
        <div class="badge">No Repairs Needed</div>
        <div class="badge">No Agent Fees</div>
        <div class="badge">Close in 7 Days</div>
        <div class="badge">Any Condition</div>
      </div>
    </div>
    <div class="hero-form">
      <div class="form-headline">Get Your Cash Offer</div>
      <div class="form-sub">{city['name']} homeowners — no obligation, takes 60 seconds</div>
      <form id="city-form" name="contact" method="POST" data-netlify="true" netlify-honeypot="bot-field" onsubmit="submitForm(event)">
        <input type="hidden" name="form-name" value="contact">
        <input type="hidden" name="bot-field" style="display:none">
        <input type="hidden" name="city" value="{city['name']}">
        <div class="field-group">
          <label>Your Name *</label>
          <input type="text" id="fname" name="name" placeholder="John Smith" required>
        </div>
        <div class="field-group">
          <label>Property Address *</label>
          <input type="text" id="address" name="address" placeholder="{city['name']}, TX {city['zip']}" required>
        </div>
        <div class="field-grid">
          <div class="field-group">
            <label>Phone *</label>
            <input type="tel" id="phone" name="phone" placeholder="(972) 555-0000" required>
          </div>
          <div class="field-group">
            <label>Email</label>
            <input type="email" id="email" name="email" placeholder="john@email.com">
          </div>
        </div>
        <div class="field-group">
          <label>Situation</label>
          <select name="situation">
            <option value="">Select...</option>
            <option>Behind on mortgage / foreclosure</option>
            <option>Inherited property</option>
            <option>Divorce / separation</option>
            <option>Tired landlord</option>
            <option>Needs major repairs</option>
            <option>Relocating</option>
            <option>Downsizing</option>
            <option>Vacant property</option>
            <option>Just want to sell fast</option>
            <option>Other</option>
          </select>
        </div>
        <button type="submit" class="submit-btn">Get My Cash Offer →</button>
      </form>
      <div class="form-success" id="form-success">
        <div class="check">✅</div>
        <h3>Got It!</h3>
        <p>We'll call you within 30 minutes with your cash offer.<br><strong>972-284-9713</strong></p>
      </div>
      <div class="form-guarantee">100% confidential · No obligation · No spam</div>
    </div>
  </div>
</section>

<div class="content-wrap">
  <div class="main-content">
    <p style="font-size:16px;line-height:1.9;color:#2a3a2a;font-weight:400;margin-bottom:24px">{content['intro']}</p>

    {content['content_html']}

    <div class="why-box">
      <h2>{content['why_sellers_title']}</h2>
      <ul>
        {why_points}
      </ul>
    </div>

    <div class="cta-box">
      <h3>Ready to Sell Your {city['name']} Home?</h3>
      <p>Get a fair cash offer within 24 hours. No fees, no repairs, no commissions. Close in as few as 7 days or on your schedule.</p>
      <a href="tel:9722849713">Call 972-284-9713 Now</a>
    </div>
  </div>

  <div class="sidebar">
    <div class="sidebar-card">
      <h3>Get Your Free Cash Offer</h3>
      <p>No fees, no repairs. Close in 7 days or on your schedule.</p>
      <a href="tel:9722849713" class="sidebar-phone">972-284-9713</a>
      <a href="#" onclick="window.scrollTo({{top:0,behavior:'smooth'}});return false" class="sidebar-btn green">Get Cash Offer →</a>
      <a href="tel:9722849713" class="sidebar-btn">Call Now</a>
    </div>
    <div class="sidebar-card">
      <h3>How It Works</h3>
      <p style="font-size:12px;color:var(--muted);line-height:1.8;margin:0">
        <strong>1.</strong> Tell us about your property<br>
        <strong>2.</strong> Get a cash offer in 24 hours<br>
        <strong>3.</strong> Choose your closing date<br>
        <strong>4.</strong> Walk away with cash
      </p>
    </div>
    <div class="sidebar-card">
      <h3>Happy With Your Sale?</h3>
      <p style="font-size:12px;color:var(--muted);line-height:1.6;margin-bottom:12px">We'd love a Google review — helps other {city['name']} homeowners find us.</p>
      <a href="https://share.google/vGlYZ46PBCsE6BPhz" target="_blank" rel="noopener" style="display:block;background:#4ab840;color:#fff;padding:10px;font-weight:700;font-size:11px;text-decoration:none;border-radius:2px;letter-spacing:0.06em;text-transform:uppercase;text-align:center">Leave a Google Review ⭐</a>
    </div>
  </div>
</div>

<div class="cities-strip">
  <h2>We Buy Houses Across All of DFW</h2>
  <div class="cities-grid">
    <a href="/plano/" class="city-pill{'active' if city['name'] == 'Plano' else ''}">Plano</a>
    <a href="/frisco/" class="city-pill{'active' if city['name'] == 'Frisco' else ''}">Frisco</a>
    <a href="/allen/" class="city-pill{'active' if city['name'] == 'Allen' else ''}">Allen</a>
    <a href="/richardson/" class="city-pill{'active' if city['name'] == 'Richardson' else ''}">Richardson</a>
    <a href="/mckinney/" class="city-pill{'active' if city['name'] == 'McKinney' else ''}">McKinney</a>
    <a href="/the-colony/" class="city-pill{'active' if city['name'] == 'The Colony' else ''}">The Colony</a>
    <a href="/prosper/" class="city-pill{'active' if city['name'] == 'Prosper' else ''}">Prosper</a>
    <a href="/lewisville/" class="city-pill{'active' if city['name'] == 'Lewisville' else ''}">Lewisville</a>
    <a href="/carrollton/" class="city-pill{'active' if city['name'] == 'Carrollton' else ''}">Carrollton</a>
    <a href="/coppell/" class="city-pill{'active' if city['name'] == 'Coppell' else ''}">Coppell</a>
    <a href="/celina/" class="city-pill{'active' if city['name'] == 'Celina' else ''}">Celina</a>
    <a href="/hurst/" class="city-pill{'active' if city['name'] == 'Hurst' else ''}">Hurst</a>
    <a href="/euless/" class="city-pill{'active' if city['name'] == 'Euless' else ''}">Euless</a>
    <a href="/bedford/" class="city-pill{'active' if city['name'] == 'Bedford' else ''}">Bedford</a>
    <a href="/arlington/" class="city-pill{'active' if city['name'] == 'Arlington' else ''}">Arlington</a>
    <a href="/grand-prairie/" class="city-pill{'active' if city['name'] == 'Grand Prairie' else ''}">Grand Prairie</a>
    <a href="/garland/" class="city-pill{'active' if city['name'] == 'Garland' else ''}">Garland</a>
    <a href="/mesquite/" class="city-pill{'active' if city['name'] == 'Mesquite' else ''}">Mesquite</a>
    <a href="/keller/" class="city-pill{'active' if city['name'] == 'Keller' else ''}">Keller</a>
    <a href="/southlake/" class="city-pill{'active' if city['name'] == 'Southlake' else ''}">Southlake</a>
    <a href="/grapevine/" class="city-pill{'active' if city['name'] == 'Grapevine' else ''}">Grapevine</a>
  </div>
</div>

<footer>
  © {year} Top DFW House Buyers · <a href="/">topdfwhousebuyers.com</a> · 972-284-9713 · TX License #0657354<br>
  Serving {city['name']} and all of Dallas-Fort Worth
</footer>

<div class="sticky-cta">
  <span class="sticky-cta-text">Sell your {city['name']} home fast — cash offer in 24 hrs</span>
  <a href="tel:9722849713" class="sticky-cta-btn">Call Now →</a>
</div>

<script>
async function submitForm(e) {{
  e.preventDefault();
  const form = document.getElementById('city-form');
  const name = document.getElementById('fname').value;
  const phone = document.getElementById('phone').value;
  const btn = form.querySelector('.submit-btn');
  btn.textContent = 'Submitting...';
  btn.disabled = true;
  try {{
    const formData = new FormData(form);
    await fetch('/', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/x-www-form-urlencoded' }},
      body: new URLSearchParams(formData).toString()
    }});
  }} catch(err) {{ console.log(err); }}
  form.style.display = 'none';
  document.getElementById('form-success').style.display = 'block';
}}
</script>
</body>
</html>"""


def main():
    print(f"Generating city landing pages — {datetime.now().isoformat()}")
    print(f"Total cities: {len(CITIES)}")

    for i, city in enumerate(CITIES):
        slug = city['name'].lower().replace(' ', '-')
        output_dir = Path(slug)
        output_file = output_dir / "index.html"

        # Skip if already exists
        if output_file.exists():
            print(f"  [{i+1}/{len(CITIES)}] Skipping {city['name']} — already exists")
            continue

        print(f"  [{i+1}/{len(CITIES)}] Generating {city['name']}...")
        try:
            content = generate_city_content(city)
            html = build_city_page(content, city)
            output_dir.mkdir(parents=True, exist_ok=True)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"    ✓ Saved to {output_file}")
        except Exception as e:
            print(f"    ✗ Error: {e}")

    print(f"\nDone! City pages generated.")
    print("URLs will be live at:")
    for city in CITIES:
        slug = city['name'].lower().replace(' ', '-')
        print(f"  topdfwhousebuyers.com/{slug}/")


if __name__ == "__main__":
    main()
