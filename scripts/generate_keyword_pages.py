#!/usr/bin/env python3
"""
Top DFW House Buyers — Keyword Landing Page Generator v2
Creates /sell-my-house-fast-{city}-tx/ pages with completely unique content.
Each page has its own canonical, ZIP codes, neighborhoods, and unique angle.
Run: python scripts/generate_keyword_pages.py
"""

import os
import json
import re
import anthropic
from datetime import datetime
from pathlib import Path

CITIES = [
    {
        "name": "Celina", "slug": "celina", "kw_slug": "sell-my-house-fast-celina-tx",
        "county": "Collin", "zip": "75009", "zip2": "75078",
        "neighborhoods": ["Light Farms", "Sutton Fields", "Mustang Lakes", "Hidden Lakes", "Creeks of Legacy", "Bluewood"],
        "angle": "fastest growing city in America with thousands of new homes — but legacy homeowners and resale sellers still need fast cash options",
        "local_facts": "Celina ISD schools, proximity to Frisco and McKinney, Collin County location, explosive 2020s growth",
    },
    {
        "name": "Plano", "slug": "plano", "kw_slug": "sell-my-house-fast-plano-tx",
        "county": "Dallas", "zip": "75024", "zip2": "75075",
        "neighborhoods": ["Legacy West", "Willow Bend", "Prestonwood", "Kings Ridge", "East Plano", "Downtown Plano"],
        "angle": "corporate hub with Fortune 500 companies driving frequent relocations and fast sale needs",
        "local_facts": "Toyota, JCPenney, Liberty Mutual HQ, DART Red Line, Legacy West development, top-rated Plano ISD",
    },
    {
        "name": "Frisco", "slug": "frisco", "kw_slug": "sell-my-house-fast-frisco-tx",
        "county": "Collin", "zip": "75034", "zip2": "75033",
        "neighborhoods": ["Starwood", "Phillips Creek Ranch", "Stonebriar", "The Canals", "Edgewood", "Nichols Farm"],
        "angle": "one of the most competitive real estate markets in DFW — homeowners who need to sell fast skip the agent altogether",
        "local_facts": "PGA Frisco, Toyota Stadium, Hall Park, FC Dallas, top Frisco ISD schools, booming corporate campus development",
    },
    {
        "name": "McKinney", "slug": "mckinney", "kw_slug": "sell-my-house-fast-mckinney-tx",
        "county": "Collin", "zip": "75070", "zip2": "75071",
        "neighborhoods": ["Historic Downtown McKinney", "Stonebridge Ranch", "Craig Ranch", "Tucker Hill", "Trinity Falls", "Adriatica"],
        "angle": "consistently ranked best place to live — high demand means cash buyers can close fast without listing",
        "local_facts": "Historic Downtown McKinney, Collin County seat, Craig Ranch Golf Club, Adriatica Village, top-rated McKinney ISD",
    },
    {
        "name": "Allen", "slug": "allen", "kw_slug": "sell-my-house-fast-allen-tx",
        "county": "Collin", "zip": "75002", "zip2": "75013",
        "neighborhoods": ["Twin Creeks", "Watters Crossing", "Bethany Lakes", "Exchange Park", "Heritage Green", "Lost Creek"],
        "angle": "affluent suburb between Plano and McKinney where corporate relocations and life changes drive fast sale demand",
        "local_facts": "Allen Premium Outlets, Allen Event Center, Watters Creek, top-rated Allen ISD, Collin County location",
    },
    {
        "name": "The Colony", "slug": "the-colony", "kw_slug": "sell-my-house-fast-the-colony-tx",
        "county": "Denton", "zip": "75056", "zip2": "75056",
        "neighborhoods": ["Stewart Peninsula", "The Tribute", "Austin Ranch", "Garza Lake", "Legends", "Northpointe"],
        "angle": "lakeside community undergoing rapid transformation with Grandscape — longtime residents cashing out on appreciation",
        "local_facts": "Grandscape entertainment complex, Lewisville Lake, The Tribute Golf Club, Nebraska Furniture Mart, Denton County",
    },
    {
        "name": "Wylie", "slug": "wylie", "kw_slug": "sell-my-house-fast-wylie-tx",
        "county": "Collin", "zip": "75098", "zip2": "75098",
        "neighborhoods": ["Woodbridge", "Bozman Farms", "Dominion of Pleasant Valley", "Inspiration", "Lakeside Estates", "Rush Creek"],
        "angle": "fast-growing community where appreciation has created strong equity — homeowners can sell fast and walk away with cash",
        "local_facts": "Lavon Lake access, Woodbridge Golf Club, Historic Downtown Wylie, Muddy Creek Preserve, Collin County",
    },
    {
        "name": "Little Elm", "slug": "little-elm", "kw_slug": "sell-my-house-fast-little-elm-tx",
        "county": "Denton", "zip": "75068", "zip2": "75068",
        "neighborhoods": ["Paloma Creek", "Union Park", "Sunset Pointe", "Frisco Ranch", "Lakeview", "The Shores"],
        "angle": "booming lakeside community where new construction competition means resale sellers benefit from a fast cash sale",
        "local_facts": "Lewisville Lake waterfront, Little Elm Beach, Union Park amenity center, Denton County, proximity to Frisco",
    },
    {
        "name": "Prosper", "slug": "prosper", "kw_slug": "sell-my-house-fast-prosper-tx",
        "county": "Collin", "zip": "75078", "zip2": "75078",
        "neighborhoods": ["Lakes of La Paloma", "Star Trail", "Windsong Ranch", "Whitley Place", "Brookhollow", "Gentle Creek"],
        "angle": "upscale master-planned community where relocation and lifestyle changes drive demand for fast no-hassle sales",
        "local_facts": "Windsong Ranch amenity center, Prosper ISD top-rated schools, Collin County location, proximity to Frisco and Celina",
    },
    {
        "name": "Rockwall", "slug": "rockwall", "kw_slug": "sell-my-house-fast-rockwall-tx",
        "county": "Rockwall", "zip": "75087", "zip2": "75032",
        "neighborhoods": ["Harbor area", "Chandler Creek", "Dalton Ranch", "Shores", "Stonelake Estates", "Lakeview"],
        "angle": "lakeside city east of Dallas where waterfront property owners and growing families alike need fast cash options",
        "local_facts": "Lake Ray Hubbard Harbor, Rockwall Harbor marina, Founders Plaza, Rockwall ISD, easternmost DFW suburb",
    },
]


def generate_content(city: dict) -> dict:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    neighborhoods_str = ", ".join(city["neighborhoods"])

    prompt = f"""You are an expert real estate SEO content writer for Top DFW House Buyers.

COMPANY: Top DFW House Buyers | Phone: 972-284-9713 | Website: topdfwhousebuyers.com | TX License #0657354

Write a UNIQUE landing page targeting: "sell my house fast {city['name']} TX"

This page must be COMPLETELY DIFFERENT from a general city page. Focus on:
- URGENCY and SPEED — people searching this term need to sell NOW
- Specific {city['name']} ZIP codes: {city['zip']} and {city['zip2']}
- Specific neighborhoods: {neighborhoods_str}
- Local angle: {city['angle']}
- Local facts: {city['local_facts']}
- Common fast-sale situations: relocation, divorce, foreclosure, inherited, landlord fatigue

DO NOT use generic real estate content. Make it hyper-local to {city['name']}.

Requirements:
- 700-900 words
- Mention ZIP codes {city['zip']} and {city['zip2']}
- Mention at least 3 neighborhoods by name
- 3 H2 sections with urgency-focused headings
- 2 CTAs mentioning 972-284-9713
- Meta title: include "Sell My House Fast {city['name']} TX" — under 60 chars
- Meta description under 160 chars

Return ONLY valid JSON (no markdown):
{{
  "meta_title": "Sell My House Fast {city['name']} TX | Cash Offer Today",
  "meta_description": "...",
  "h1": "Sell My House Fast in {city['name']}, TX — Cash Offer in 24 Hours",
  "intro": "2-3 sentences specific to {city['name']} mentioning a neighborhood or ZIP code",
  "content_html": "HTML with h2, p, ul, li — mention neighborhoods and ZIP codes naturally",
  "why_points": ["...", "...", "...", "...", "..."]
}}"""

    prompt_safe = prompt.encode('ascii', errors='replace').decode('ascii')
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2500,
        messages=[{"role": "user", "content": prompt_safe}]
    )
    raw = message.content[0].text.strip()
    raw = re.sub(r'^```json\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)
    return json.loads(raw)


def build_page(content: dict, city: dict) -> str:
    year = datetime.now().year
    why_points = ''.join([
        f'<li style="padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.1);color:rgba(255,255,255,0.85);font-size:14px;display:flex;gap:10px"><span style="color:#4ab840;font-weight:700;flex-shrink:0">✓</span>{p}</li>'
        for p in content.get('why_points', [])
    ])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{content['meta_title']}</title>
<meta name="description" content="{content['meta_description']}">
<meta property="og:title" content="{content['meta_title']}">
<meta property="og:description" content="{content['meta_description']}">
<link rel="canonical" href="https://www.topdfwhousebuyers.com/{city['kw_slug']}/">
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "RealEstateAgent",
  "name": "Top DFW House Buyers",
  "telephone": "972-284-9713",
  "url": "https://www.topdfwhousebuyers.com",
  "areaServed": ["{city['name']}, Texas", "{city['zip']}", "{city['zip2']}"]
}}
</script>
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {{"@type":"Question","name":"How fast can you buy my house in {city['name']}, TX {city['zip']}?","acceptedAnswer":{{"@type":"Answer","text":"We close in as few as 7 days anywhere in {city['name']}. Call 972-284-9713 now."}}}},
    {{"@type":"Question","name":"Do I need repairs before selling my {city['name']} home?","acceptedAnswer":{{"@type":"Answer","text":"No. We buy houses in {city['name']} in any condition — no repairs, no cleaning, no staging."}}}},
    {{"@type":"Question","name":"What neighborhoods in {city['name']} do you buy houses in?","acceptedAnswer":{{"@type":"Answer","text":"We buy houses throughout {city['name']} in {city['zip']} and {city['zip2']} including {', '.join(city['neighborhoods'][:4])} and more."}}}},
    {{"@type":"Question","name":"Are there fees when selling to Top DFW House Buyers?","acceptedAnswer":{{"@type":"Answer","text":"Zero fees, zero commissions, zero closing costs. Our offer is what you receive at closing."}}}}
  ]
}}
</script>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-QSBN8EDR9Z"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-QSBN8EDR9Z');</script>
<script type="text/javascript">(function(c,l,a,r,i,t,y){{c[a]=c[a]||function(){{(c[a].q=c[a].q||[]).push(arguments)}};t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);}})(window,document,"clarity","script","wiurnc9zu7");</script>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Montserrat:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{--green:#4ab840;--dark:#0a0a0a;--navy:#1a1f1a;--cream:#f8faf8;--border:#d4e4d2;--muted:#52675f}}
body{{background:var(--cream);color:#1a1f1a;font-family:'Montserrat',sans-serif;font-weight:300;line-height:1.6}}
.site-nav{{background:var(--dark);padding:14px 32px;display:flex;align-items:center;justify-content:space-between;border-bottom:3px solid var(--green);position:sticky;top:0;z-index:100}}
.nav-logo{{color:var(--green);font-family:'Playfair Display',serif;font-weight:700;font-size:18px;text-decoration:none}}
.nav-logo span{{color:#fff}}
.nav-links{{display:flex;align-items:center;gap:20px}}
.nav-links a{{color:rgba(255,255,255,0.7);font-size:12px;font-weight:600;text-decoration:none;text-transform:uppercase;letter-spacing:0.05em}}
.nav-cta{{background:var(--green);color:#fff !important;padding:9px 18px;border-radius:2px}}
.hero{{background:var(--navy);padding:56px 40px;position:relative;overflow:hidden}}
.hero::before{{content:'';position:absolute;inset:0;background:url('https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=1400&q=70') center/cover;opacity:0.1}}
.hero-inner{{position:relative;z-index:1;max-width:1100px;margin:0 auto;display:grid;grid-template-columns:1fr 420px;gap:48px;align-items:center}}
@media(max-width:900px){{.hero-inner{{grid-template-columns:1fr}}}}
.eyebrow{{display:inline-flex;background:rgba(74,184,64,0.15);border:1px solid rgba(74,184,64,0.35);padding:5px 12px;border-radius:2px;font-size:10px;font-weight:700;letter-spacing:0.2em;text-transform:uppercase;color:#6dd962;margin-bottom:16px}}
.hero h1{{font-family:'Playfair Display',serif;font-size:clamp(28px,4vw,46px);font-weight:900;color:#fff;line-height:1.1;margin-bottom:16px}}
.hero h1 em{{font-style:italic;color:#6dd962;font-weight:400}}
.hero-sub{{font-size:15px;color:rgba(255,255,255,0.7);line-height:1.7;margin-bottom:24px}}
.zip-strip{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:20px}}
.zip-badge{{background:rgba(74,184,64,0.15);border:1px solid rgba(74,184,64,0.3);color:#6dd962;font-size:11px;font-weight:700;padding:4px 10px;border-radius:2px}}
.badges{{display:flex;gap:8px;flex-wrap:wrap}}
.badge{{display:flex;align-items:center;gap:5px;background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.15);padding:6px 12px;border-radius:2px;font-size:11px;color:rgba(255,255,255,0.8);font-weight:500}}
.hero-form{{background:#fff;border-top:4px solid var(--green);padding:28px 24px;box-shadow:0 20px 60px rgba(0,0,0,0.4)}}
.form-headline{{font-family:'Playfair Display',serif;font-size:20px;font-weight:700;color:#1a1f1a;margin-bottom:4px}}
.form-sub{{font-size:12px;color:var(--muted);margin-bottom:18px}}
.field{{margin-bottom:12px}}
.field label{{display:block;font-size:10px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:var(--muted);margin-bottom:4px}}
.field input,.field select{{width:100%;padding:11px 13px;border:1.5px solid var(--border);border-radius:2px;font-family:'Montserrat',sans-serif;font-size:13px;outline:none;transition:border-color .15s}}
.field input:focus,.field select:focus{{border-color:var(--green)}}
.field-grid{{display:grid;grid-template-columns:1fr 1fr;gap:10px}}
.submit-btn{{width:100%;padding:14px;background:#000;border:none;color:#fff;font-family:'Montserrat',sans-serif;font-weight:700;font-size:13px;letter-spacing:0.05em;text-transform:uppercase;cursor:pointer;border-radius:2px;transition:all .2s;margin-top:4px}}
.submit-btn:hover{{background:#222;transform:translateY(-1px)}}
.guarantee{{text-align:center;font-size:10px;color:var(--muted);margin-top:10px}}
.content-wrap{{max-width:1100px;margin:0 auto;padding:56px 24px;display:grid;grid-template-columns:1fr 300px;gap:48px}}
@media(max-width:768px){{.content-wrap{{grid-template-columns:1fr}}}}
.main h2{{font-family:'Playfair Display',serif;font-size:26px;font-weight:700;color:#1a1f1a;margin:32px 0 12px;line-height:1.2}}
.main p{{font-size:15px;line-height:1.9;color:#3a4a3a;margin-bottom:14px}}
.main ul{{padding-left:20px;margin-bottom:14px}}
.main li{{font-size:15px;line-height:1.8;color:#3a4a3a;margin:6px 0}}
.why-box{{background:var(--navy);padding:32px;margin:32px 0}}
.why-box h2{{font-family:'Playfair Display',serif;font-size:22px;color:#fff;margin-bottom:20px}}
.why-box ul{{list-style:none;padding:0}}
.cta-box{{background:#f8faf8;border:1px solid var(--border);border-left:4px solid var(--green);padding:24px 28px;margin:32px 0}}
.cta-box h3{{font-size:16px;font-weight:700;color:#1a1f1a;margin-bottom:8px}}
.cta-box p{{font-size:13px;color:var(--muted);margin-bottom:14px;line-height:1.6}}
.cta-box a{{display:inline-block;background:#1a1f1a;color:#fff;padding:12px 24px;font-weight:700;font-size:12px;text-decoration:none;border-radius:2px;letter-spacing:0.06em;text-transform:uppercase}}
.sidebar-card{{background:#fff;border:1px solid var(--border);border-top:3px solid var(--green);padding:20px;margin-bottom:16px}}
.sidebar-card h3{{font-size:14px;font-weight:700;color:#1a1f1a;margin-bottom:8px}}
.sidebar-phone{{font-size:22px;font-weight:700;color:var(--green);text-decoration:none;display:block;margin-bottom:10px}}
.s-btn{{display:block;padding:12px;font-weight:700;font-size:11px;text-decoration:none;border-radius:2px;text-align:center;margin-bottom:8px;text-transform:uppercase;letter-spacing:0.06em}}
.s-btn.green{{background:var(--green);color:#fff}}
.s-btn.dark{{background:#1a1f1a;color:#fff}}
.neighborhoods-box{{background:#f8faf8;border:1px solid var(--border);border-left:4px solid var(--green);padding:16px 20px;margin-bottom:16px}}
.neighborhoods-box h3{{font-size:12px;font-weight:700;color:#1a1f1a;margin-bottom:8px;text-transform:uppercase;letter-spacing:0.08em}}
footer{{background:var(--dark);color:rgba(255,255,255,0.4);text-align:center;padding:24px;font-size:11px;border-top:3px solid var(--green)}}
footer a{{color:var(--green);text-decoration:none}}
.sticky{{position:fixed;bottom:0;left:0;right:0;background:var(--navy);border-top:2px solid var(--green);padding:12px 20px;display:none;align-items:center;justify-content:space-between;z-index:200}}
@media(max-width:640px){{.sticky{{display:flex}}}}
.sticky span{{font-size:12px;color:rgba(255,255,255,0.7)}}
.sticky a{{padding:9px 18px;background:var(--green);color:#fff;font-weight:700;font-size:11px;text-decoration:none;border-radius:2px;white-space:nowrap}}
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
      <div class="eyebrow">{city['name']}, {city['county']} County TX · ZIP {city['zip']} · {city['zip2']}</div>
      <h1>{content['h1'].replace('Fast', '<em>Fast</em>')}</h1>
      <p class="hero-sub">Top DFW House Buyers purchases homes throughout {city['name']} — any condition, any situation. Cash offer in 24 hours, close in 7 days.</p>
      <div class="zip-strip">
        <span class="zip-badge">ZIP {city['zip']}</span>
        <span class="zip-badge">ZIP {city['zip2']}</span>
        <span class="zip-badge">{city['county']} County</span>
      </div>
      <div class="badges">
        <div class="badge">Cash Offer in 24 Hours</div>
        <div class="badge">Close in 7 Days</div>
        <div class="badge">No Repairs</div>
        <div class="badge">Zero Fees</div>
      </div>
    </div>
    <div class="hero-form">
      <div class="form-headline">Get Your Cash Offer Now</div>
      <div class="form-sub">{city['name']} homeowners — takes 60 seconds, no obligation</div>
      <form id="kw-form" name="contact" method="POST" data-netlify="true" netlify-honeypot="bot-field" onsubmit="submitForm(event)">
        <input type="hidden" name="form-name" value="contact">
        <input type="hidden" name="bot-field" style="display:none">
        <input type="hidden" name="city" value="{city['name']}">
        <div class="field"><label>Your Name *</label><input type="text" name="name" placeholder="John Smith" required></div>
        <div class="field"><label>Property Address *</label><input type="text" name="address" placeholder="{city['name']}, TX {city['zip']}" required></div>
        <div class="field-grid">
          <div class="field"><label>Phone *</label><input type="tel" name="phone" placeholder="(972) 555-0000" required></div>
          <div class="field"><label>Email</label><input type="email" name="email" placeholder="john@email.com"></div>
        </div>
        <div class="field">
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
      <div id="form-success" style="display:none;text-align:center;padding:24px">
        <div style="font-size:40px;margin-bottom:10px">✅</div>
        <h3 style="font-family:'Playfair Display',serif;font-size:20px;color:#1a1f1a;margin-bottom:8px">Got It!</h3>
        <p style="font-size:13px;color:var(--muted)">We will call you within 30 minutes.<br><strong>972-284-9713</strong></p>
      </div>
      <div class="guarantee">100% confidential · No obligation · No spam</div>
    </div>
  </div>
</section>
<div class="content-wrap">
  <div class="main">
    <p style="font-size:16px;line-height:1.9;color:#2a3a2a;font-weight:400;margin-bottom:24px">{content['intro']}</p>
    {content['content_html']}
    <div class="why-box">
      <h2>Why {city['name']} Homeowners Choose Top DFW House Buyers</h2>
      <ul>{why_points}</ul>
    </div>
    <div class="cta-box">
      <h3>Ready to Sell Your {city['name']} Home Fast?</h3>
      <p>Cash offer within 24 hours. No fees, no repairs, no commissions. We serve all of {city['name']} including ZIP codes {city['zip']} and {city['zip2']}.</p>
      <a href="tel:9722849713">Call 972-284-9713 Now</a>
    </div>
  </div>
  <div>
    <div class="sidebar-card">
      <h3>Get Your Free Cash Offer</h3>
      <p style="font-size:12px;color:var(--muted);margin-bottom:12px">Serving all of {city['name']} — ZIP {city['zip']} and {city['zip2']}.</p>
      <a href="tel:9722849713" class="sidebar-phone">972-284-9713</a>
      <a href="#" onclick="window.scrollTo({{top:0,behavior:'smooth'}});return false" class="s-btn green">Get Cash Offer →</a>
      <a href="tel:9722849713" class="s-btn dark">Call Now</a>
    </div>
    <div class="neighborhoods-box">
      <h3>Neighborhoods We Buy In</h3>
      <p style="font-size:12px;color:var(--muted);line-height:1.8">{' · '.join(city['neighborhoods'])}</p>
    </div>
    <div class="sidebar-card">
      <h3>How It Works</h3>
      <p style="font-size:12px;color:var(--muted);line-height:1.8;margin:0">
        <strong>1.</strong> Tell us about your property<br>
        <strong>2.</strong> Cash offer in 24 hours<br>
        <strong>3.</strong> Choose your closing date<br>
        <strong>4.</strong> Walk away with cash
      </p>
    </div>
  </div>
</div>
<footer>
  © {year} Top DFW House Buyers · <a href="/">topdfwhousebuyers.com</a> · 972-284-9713 · TX License #0657354<br>
  Serving {city['name']} {city['zip']} · {city['zip2']} · {city['county']} County, Texas
</footer>
<div class="sticky">
  <span>Sell your {city['name']} home fast — cash offer in 24 hrs</span>
  <a href="tel:9722849713">Call Now →</a>
</div>
<script>
async function submitForm(e){{
  e.preventDefault();
  const form=document.getElementById('kw-form');
  const btn=form.querySelector('.submit-btn');
  btn.textContent='Submitting...';btn.disabled=true;
  try{{const fd=new FormData(form);await fetch('/',{{method:'POST',headers:{{'Content-Type':'application/x-www-form-urlencoded'}},body:new URLSearchParams(fd).toString()}});}}catch(e){{}}
  form.style.display='none';document.getElementById('form-success').style.display='block';
}}
</script>
</body>
</html>"""


def main():
    print(f"Generating {len(CITIES)} DFW keyword landing pages v2 — {datetime.now().isoformat()}")
    print()
    for i, city in enumerate(CITIES):
        output_dir = Path(city['kw_slug'])
        output_file = output_dir / "index.html"
        print(f"  [{i+1}/{len(CITIES)}] {city['name']} → /{city['kw_slug']}/...")
        try:
            content = generate_content(city)
            html = build_page(content, city)
            output_dir.mkdir(parents=True, exist_ok=True)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"    ✓ {output_file}")
        except Exception as e:
            print(f"    ✗ Error on {city['name']}: {e}")
    print()
    print(f"Done! {len(CITIES)} keyword pages generated.")


if __name__ == "__main__":
    main()
