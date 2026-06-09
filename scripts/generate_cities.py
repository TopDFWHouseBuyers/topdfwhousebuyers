#!/usr/bin/env python3
"""
Top DFW House Buyers — Complete Enhanced City Page Generator
All 40 DFW cities with neighborhood-level detail.
Run: python scripts/generate_cities.py
"""

import os
import json
import re
import anthropic
from datetime import datetime
from pathlib import Path

CITIES = [
    # ── Collin County ──────────────────────────────────────────────────────
    {"slug":"plano","name":"Plano","county":"Dallas","zip":"75024","region":"Collin County",
     "neighborhoods":["Legacy West","Willow Bend","West Plano","East Plano","Downtown Plano","Preston Meadow","Ridgeview Ranch","Kings Ridge","Prestonwood","Shoal Creek"],
     "landmarks":"Legacy West, Shops at Willow Bend, Toyota North America HQ, JCPenney HQ, Arbor Hills Nature Preserve, DART Red Line",
     "market":"one of the wealthiest cities in Texas with median home prices from $400k in East Plano to $1M+ in Willow Bend, major corporate headquarters hub",
     "seller_situations":"corporate relocations, divorce, inherited properties, downsizing empty nesters, landlords exiting the rental market"},
    {"slug":"frisco","name":"Frisco","county":"Collin","zip":"75034","region":"Collin County",
     "neighborhoods":["Starwood","Phillips Creek Ranch","Stonebriar","The Canals at Grand Park","Edgewood","Nichols Farm","Lawler Park","Creekside"],
     "landmarks":"Toyota Stadium, PGA Frisco, Hall Park, Stonebriar Centre Mall, FC Dallas",
     "market":"one of fastest-growing cities in the US with major corporate campuses and master-planned communities, median home prices around $600k",
     "seller_situations":"corporate relocation, divorce, inherited properties, upgrading families, new construction competition"},
    {"slug":"mckinney","name":"McKinney","county":"Collin","zip":"75070","region":"Collin County",
     "neighborhoods":["Historic Downtown McKinney","Adriatica","Stonebridge Ranch","Craig Ranch","Tucker Hill","Trinity Falls","Painted Tree"],
     "landmarks":"Historic Downtown McKinney, Collin County Adventure Camp, Craig Ranch Golf Club, Adriatica Village",
     "market":"consistently ranked best place to live in America with charming historic downtown, median home prices around $500k",
     "seller_situations":"relocation, divorce, inherited historic properties, downsizing, new construction competition"},
    {"slug":"allen","name":"Allen","county":"Collin","zip":"75002","region":"Collin County",
     "neighborhoods":["Twin Creeks","Watters Crossing","Bethany Lakes","Exchange Park","Heritage Green","Ridgeview Ranch","Lost Creek"],
     "landmarks":"Allen Premium Outlets, Allen Event Center, Watters Creek, Joe Farmer Recreation Center",
     "market":"affluent suburb between Plano and McKinney with top-rated schools, median home prices around $500k",
     "seller_situations":"relocation, divorce, inherited properties, downsizing empty nesters, upgrading families"},
    {"slug":"richardson","name":"Richardson","county":"Dallas","zip":"75080","region":"Collin County",
     "neighborhoods":["Canyon Creek","Arapaho East","Breckinridge Park","UTD area","Cottonwood Park","Buckingham","Spring Creek"],
     "landmarks":"University of Texas at Dallas, Telecom Corridor, Eisemann Center, Breckinridge Park",
     "market":"Telecom Corridor hub with UT Dallas and mix of 1960s-1990s homes, median home prices around $400k",
     "seller_situations":"corporate relocation, inherited older homes, divorce, landlords, aging homeowners"},
    {"slug":"prosper","name":"Prosper","county":"Collin","zip":"75078","region":"Collin County",
     "neighborhoods":["Lakes of La Paloma","Star Trail","Windsong Ranch","Whitley Place","Brookhollow","Gentle Creek"],
     "landmarks":"Windsong Ranch amenity center, Prosper Town Hall, Frontier Park",
     "market":"fast-growing upscale suburb north of Frisco with master-planned communities, median home prices around $600k",
     "seller_situations":"relocation, divorce, inherited properties, upgrading families, new construction competition"},
    {"slug":"celina","name":"Celina","county":"Collin","zip":"75009","region":"Collin County",
     "neighborhoods":["Light Farms","Sutton Fields","Mustang Lakes","Hidden Lakes","Creeks of Legacy","Lariat","Bluewood"],
     "landmarks":"Light Farms amenity center, Celina High School, Downtown Celina, Wilson Creek",
     "market":"fastest-growing city in America with explosive new development and master-planned communities, median home prices around $500k",
     "seller_situations":"relocation, divorce, inherited properties, upgrading families, new construction resales"},
    {"slug":"wylie","name":"Wylie","county":"Collin","zip":"75098","region":"Collin County",
     "neighborhoods":["Woodbridge","Bozman Farms","Dominion of Pleasant Valley","Inspiration","Lakeside Estates","Rush Creek"],
     "landmarks":"Lavon Lake, Woodbridge Golf Club, Downtown Wylie, Muddy Creek Preserve",
     "market":"fast-growing community in Collin County with charming historic downtown and lake access, median home prices around $450k",
     "seller_situations":"relocation, divorce, inherited properties, upgrading families, landlords"},
    {"slug":"the-colony","name":"The Colony","county":"Denton","zip":"75056","region":"Denton County",
     "neighborhoods":["Stewart Peninsula","The Tribute","Austin Ranch","Garza Lake","Legends","Northpointe","Ridgepointe"],
     "landmarks":"Grandscape entertainment complex, Lewisville Lake, The Tribute Golf Club, Old American Golf Club, Nebraska Furniture Mart",
     "market":"lakeside community on Lewisville Lake with rapidly growing Grandscape development, median home prices around $458k",
     "seller_situations":"job relocation, divorce, inherited properties, downsizing, homeowners cashing out on appreciated lakeside properties"},
    {"slug":"sachse","name":"Sachse","county":"Dallas","zip":"75048","region":"Collin County",
     "neighborhoods":["Ranch at Rowlett Creek","Woodbridge","Heritage","Sachse Estates","Miles Crossing"],
     "landmarks":"Sachse Athletic Complex, Miles Branch Creek, Rowlett Creek Preserve",
     "market":"small fast-growing community between Garland and Wylie with affordable family homes, median home prices around $380k",
     "seller_situations":"relocation, inherited properties, divorce, upgrading families"},

    # ── Denton County ──────────────────────────────────────────────────────
    {"slug":"lewisville","name":"Lewisville","county":"Denton","zip":"75067","region":"Denton County",
     "neighborhoods":["Castle Hills","Lakeland Hills","Old Town Lewisville","Vista Ridge","Bellaire Ranch","Vail Ranch"],
     "landmarks":"Lewisville Lake, Vista Ridge Mall, Music City Mall, Old Town Lewisville",
     "market":"growing Denton County suburb with Lewisville Lake access, median home prices around $380k",
     "seller_situations":"relocation, divorce, inherited properties, landlords, aging homeowners"},
    {"slug":"flower-mound","name":"Flower Mound","county":"Denton","zip":"75028","region":"Denton County",
     "neighborhoods":["The Trails","Wellington","Bridlewood","Lakeside DFW","River Walk","Timber Creek","Morriss Road corridor"],
     "landmarks":"Grapevine Lake, Bridlewood Golf Club, Lakeside DFW, Marcus High School",
     "market":"affluent master-planned community known for large lots and top schools, median home prices around $550k",
     "seller_situations":"relocation, divorce, inherited properties, downsizing empty nesters, trust sales"},
    {"slug":"denton","name":"Denton","county":"Denton","zip":"76201","region":"Denton County",
     "neighborhoods":["Fry Street area","TWU area","UNT area","Downtown Denton","Rayzor Ranch","Pecan Creek","Robson Ranch"],
     "landmarks":"University of North Texas, Texas Woman's University, Denton Square, Rayzor Ranch Town Center",
     "market":"vibrant college town home to UNT and TWU with diverse housing stock, median home prices around $350k",
     "seller_situations":"relocation, inherited rental properties, divorce, landlords near universities, aging homeowners"},
    {"slug":"little-elm","name":"Little Elm","county":"Denton","zip":"75068","region":"Denton County",
     "neighborhoods":["Paloma Creek","Union Park","Sunset Pointe","Frisco Ranch","Lakeview","The Shores"],
     "landmarks":"Lewisville Lake waterfront, Little Elm Beach, Union Park amenity center",
     "market":"lakeside community on Lewisville Lake with booming residential growth, median home prices around $400k",
     "seller_situations":"relocation, divorce, inherited lake properties, upgrading families, new construction competition"},
    {"slug":"coppell","name":"Coppell","county":"Dallas","zip":"75019","region":"Denton County",
     "neighborhoods":["Old Coppell","Riverchase","Northlake Woodlands","Austin Ranch adjacent","Meadowglen","Plantation Resort"],
     "landmarks":"DFW Airport adjacent, Coppell Arts Center, Andrew Brown Park, Wagon Wheel Park",
     "market":"upscale suburb adjacent to DFW Airport with top-rated schools, median home prices around $550k",
     "seller_situations":"corporate relocation, divorce, inherited properties, downsizing empty nesters"},

    # ── Tarrant County ─────────────────────────────────────────────────────
    {"slug":"fort-worth","name":"Fort Worth","county":"Tarrant","zip":"76102","region":"Tarrant County",
     "neighborhoods":["Sundance Square","Fairmount","Ryan Place","Monticello","Rivercrest","TCU area","Near Southside","Cultural District"],
     "landmarks":"Stockyards National Historic District, Kimbell Art Museum, Bass Performance Hall, TCU",
     "market":"10th largest US city known as Cowtown with world-class museums and diverse neighborhoods, median home prices around $300k",
     "seller_situations":"inherited properties, divorce, relocation, landlords, homes needing repairs, probate"},
    {"slug":"arlington","name":"Arlington","county":"Tarrant","zip":"76010","region":"Tarrant County",
     "neighborhoods":["North Arlington","South Arlington","Pantego adjacent","Entertainment District","UTA area","Dalworthington Gardens"],
     "landmarks":"AT&T Stadium, Globe Life Field, Six Flags Over Texas, UT Arlington",
     "market":"home of AT&T Stadium and Globe Life Field with diverse city between Dallas and Fort Worth, median home prices around $280k",
     "seller_situations":"relocation, inherited properties, divorce, landlords, homes needing repairs"},
    {"slug":"keller","name":"Keller","county":"Tarrant","zip":"76248","region":"Tarrant County",
     "neighborhoods":["Keller Crossing","Bear Creek","Woodland Springs","Hidden Lakes","Park Glen","Stone Oak","Keller Town Center"],
     "landmarks":"Keller Town Center, Bear Creek Community Church, Old Town Keller, Alliance corridor nearby",
     "market":"affluent north Tarrant County suburb with large lots and top-rated Keller ISD schools, median home prices around $500k",
     "seller_situations":"relocation, divorce, inherited properties, downsizing empty nesters, trust sales"},
    {"slug":"grapevine","name":"Grapevine","county":"Tarrant","zip":"76051","region":"Tarrant County",
     "neighborhoods":["Historic Downtown Grapevine","Lakeside","Silver Lake","Grapevine Lake area","Coppell adjacent","Nash Farm"],
     "landmarks":"Historic Main Street, Grapevine Lake, Gaylord Texan Resort, DFW Airport adjacent",
     "market":"charming historic wine city adjacent to DFW Airport with lakeside properties, median home prices around $450k",
     "seller_situations":"relocation, divorce, inherited historic homes, trust sales, estate sales"},
    {"slug":"colleyville","name":"Colleyville","county":"Tarrant","zip":"76034","region":"Tarrant County",
     "neighborhoods":["Colleyville Downs","Timarron","Church Street area","Mira Vista adjacent","Montclair Parc","Creekwood"],
     "landmarks":"Colleyville Nature Center, Heritage Park, Colleyville Town Center",
     "market":"upscale suburban community known for large lots and top-rated GCISD schools, median home prices around $700k",
     "seller_situations":"relocation, divorce, estate sales, inherited large lot properties, trust sales"},
    {"slug":"southlake","name":"Southlake","county":"Tarrant","zip":"76092","region":"Tarrant County",
     "neighborhoods":["Southlake Town Square area","Timarron","Estes Park","Carillon","Majestic Hills","Kirkwood Hollow","The Woods"],
     "landmarks":"Southlake Town Square, Bob Jones Nature Center, Carroll Dragon Stadium",
     "market":"among wealthiest suburbs in Texas with top Carroll ISD schools and premium estates, median home prices above $900k",
     "seller_situations":"estate sales, trust sales, divorce settlements, corporate relocation, inherited premium properties"},
    {"slug":"north-richland-hills","name":"North Richland Hills","county":"Tarrant","zip":"76180","region":"Tarrant County",
     "neighborhoods":["Smithfield","Iron Horse","Fossil Creek","Meadow Lakes","Thornbridge","Walker Branch"],
     "landmarks":"NRHS Recreation Center, NRH2O Family Water Park, Iron Horse Golf Course, North Hills Mall area",
     "market":"Mid-Cities hub with convenient DFW Airport access and affordable family homes, median home prices around $320k",
     "seller_situations":"relocation, inherited properties, divorce, aging homeowners, landlords"},
    {"slug":"hurst","name":"Hurst","county":"Tarrant","zip":"76053","region":"Tarrant County",
     "neighborhoods":["Hurst Hills","Downtown Hurst","Precinct Line corridor","Bellaire","Hurstview"],
     "landmarks":"North East Mall, Hurst Conference Center, Hurst Community Park",
     "market":"Mid-Cities community with affordable housing and good access to DFW Airport, median home prices around $280k",
     "seller_situations":"aging homeowners, inherited properties, divorce, relocation, homes needing updates"},
    {"slug":"euless","name":"Euless","county":"Tarrant","zip":"76039","region":"Tarrant County",
     "neighborhoods":["Bear Creek","DFW Lakes","Euless Hills","Heritage","Lakewood","Westwood"],
     "landmarks":"DFW Airport adjacent, Bear Creek Park, Texas Star Golf Course nearby",
     "market":"Mid-Cities community adjacent to DFW Airport with affordable diverse housing, median home prices around $280k",
     "seller_situations":"relocation, inherited properties, divorce, landlords, aging homeowners"},
    {"slug":"bedford","name":"Bedford","county":"Tarrant","zip":"76021","region":"Tarrant County",
     "neighborhoods":["Bedford Boys Ranch area","Shady Brook","Forest Hills","Stonegate","Liberty Park","Meadowbrook"],
     "landmarks":"Boys Ranch Park, Bedford Public Library, Central Park Bedford",
     "market":"centrally located Mid-Cities community with established neighborhoods, median home prices around $280k",
     "seller_situations":"aging homeowners, inherited properties, divorce, relocation, homes needing updates"},
    {"slug":"mansfield","name":"Mansfield","county":"Tarrant","zip":"76063","region":"Tarrant County",
     "neighborhoods":["South Pointe","Walnut Creek","Cypress Meadows","Heritage Park","Woodland Creek","Britton"],
     "landmarks":"Hawaiian Falls Waterpark, Mansfield National Golf Club, Elbow Creek Park",
     "market":"growing southern Tarrant County suburb with excellent schools, median home prices around $380k",
     "seller_situations":"relocation, divorce, inherited properties, upgrading families, new construction competition"},
    {"slug":"burleson","name":"Burleson","county":"Johnson","zip":"76028","region":"Johnson County",
     "neighborhoods":["Briar Meadow","Hidden Creek","Joshua Creek","Spyglass","Willow Creek","Old Town Burleson"],
     "landmarks":"Old Town Burleson, Burleson Centennial High School, Joshua Creek Golf Club",
     "market":"growing south Fort Worth suburb with small-town feel and strong community, median home prices around $350k",
     "seller_situations":"relocation, divorce, inherited properties, upgrading families, landlords"},

    # ── Dallas County ──────────────────────────────────────────────────────
    {"slug":"dallas","name":"Dallas","county":"Dallas","zip":"75201","region":"Dallas County",
     "neighborhoods":["Uptown","Deep Ellum","Oak Cliff","Bishop Arts District","Preston Hollow","Highland Park adjacent","Oak Lawn","Lakewood"],
     "landmarks":"Reunion Tower, AT&T Discovery District, Dallas Museum of Art, Klyde Warren Park, Deep Ellum",
     "market":"9th largest US city and economic hub of North Texas with diverse neighborhoods, median home prices around $350k citywide",
     "seller_situations":"inherited properties, divorce, relocation, landlords with tenant issues, probate, homes needing major repairs"},
    {"slug":"garland","name":"Garland","county":"Dallas","zip":"75040","region":"Dallas County",
     "neighborhoods":["North Garland","South Garland","Historic Downtown Garland","Firewheel","Lakeside Village","Duck Creek"],
     "landmarks":"Firewheel Town Center, Lake Ray Hubbard access, Granville Arts Center, Spring Creek Nature Area",
     "market":"diverse east Dallas suburb with affordable housing and lake access, median home prices around $300k",
     "seller_situations":"inherited properties, divorce, relocation, aging homeowners, homes needing repairs"},
    {"slug":"irving","name":"Irving","county":"Dallas","zip":"75038","region":"Dallas County",
     "neighborhoods":["Las Colinas","Valley Ranch","Heritage Crossing","MacArthur Hills","North Hills","Hackberry Creek"],
     "landmarks":"Las Colinas Urban Center, Toyota Music Factory, Irving Arts Center, DFW Airport adjacent",
     "market":"home to Fortune 500 headquarters and Las Colinas urban center, median home prices around $350k",
     "seller_situations":"corporate relocation, divorce, inherited properties, landlords, condo sales near Las Colinas"},
    {"slug":"grand-prairie","name":"Grand Prairie","county":"Dallas","zip":"75050","region":"Dallas County",
     "neighborhoods":["South Grand Prairie","Epic Waters area","Lynn Creek","Dalworth Park","West Grand Prairie","Corn Valley"],
     "landmarks":"Epic Waters Indoor Waterpark, EpicCentral, Lynn Creek Marina, Traders Village",
     "market":"diverse city between Dallas and Fort Worth with affordable housing and lake access, median home prices around $280k",
     "seller_situations":"relocation, inherited properties, divorce, landlords, homes needing repairs"},
    {"slug":"mesquite","name":"Mesquite","county":"Dallas","zip":"75149","region":"Dallas County",
     "neighborhoods":["North Mesquite","South Mesquite","Sunmeadow","Lake June","Motley","East Mesquite"],
     "landmarks":"Mesquite Championship Rodeo, Town East Mall, Eastfield College",
     "market":"east Dallas suburb with affordable working-class neighborhoods and rodeo heritage, median home prices around $280k",
     "seller_situations":"inherited properties, aging homeowners, divorce, relocation, homes needing significant repairs"},
    {"slug":"carrollton","name":"Carrollton","county":"Dallas","zip":"75006","region":"Dallas County",
     "neighborhoods":["Old Town Carrollton","Bent Tree North","Country Club","Rosemeade","Josey Ranch","Mill Valley"],
     "landmarks":"Old Town Carrollton Square, Arbor Hills Nature Preserve, Korean Business District on Belt Line",
     "market":"diverse north Dallas suburb with large Korean-American community and mix of housing, median home prices around $380k",
     "seller_situations":"relocation, divorce, inherited properties, landlords, aging homeowners"},
    {"slug":"farmers-branch","name":"Farmers Branch","county":"Dallas","zip":"75234","region":"Dallas County",
     "neighborhoods":["Caruth Hills","Rawhide","Valwood","East Farmers Branch","Mercer Crossing"],
     "landmarks":"Farmers Branch Historical Park, Mercer Crossing development, LBJ Freeway access",
     "market":"centrally located inner suburb of Dallas with easy LBJ Freeway access, median home prices around $380k",
     "seller_situations":"inherited older homes, divorce, relocation, landlords, homes needing updates"},
    {"slug":"rowlett","name":"Rowlett","county":"Dallas","zip":"75088","region":"Dallas County",
     "neighborhoods":["Bayside","Waterview","Lakeshore","Springfield Estates","Liberty Grove","Toler Oaks"],
     "landmarks":"Lake Ray Hubbard waterfront, Bayside development, Waterview Golf Club",
     "market":"lakeside community on Lake Ray Hubbard with strong residential base, median home prices around $350k",
     "seller_situations":"relocation, inherited lake properties, divorce, landlords, upgrading families"},
    {"slug":"desoto","name":"DeSoto","county":"Dallas","zip":"75115","region":"Dallas County",
     "neighborhoods":["Pleasant Run","Thorntree","Westridge","Cockrell Hill adjacent","Eldorado","Kiest Park area"],
     "landmarks":"DeSoto Town Center, Thorntree Country Club, UNT Dallas nearby",
     "market":"growing south Dallas suburb with strong sense of community, median home prices around $300k",
     "seller_situations":"relocation, inherited properties, divorce, landlords, homes needing updates"},
    {"slug":"duncanville","name":"Duncanville","county":"Dallas","zip":"75116","region":"Dallas County",
     "neighborhoods":["North Duncanville","South Duncanville","Wheatland","Bear Creek","Lake Ridge","Camp Wisdom area"],
     "landmarks":"Duncanville Fieldhouse, Camp Wisdom Road corridor, Mountain Creek Lake nearby",
     "market":"established southwest Dallas suburb with affordable housing, median home prices around $280k",
     "seller_situations":"aging homeowners, inherited properties, divorce, relocation, homes needing repairs"},
    {"slug":"cedar-hill","name":"Cedar Hill","county":"Dallas","zip":"75104","region":"Dallas County",
     "neighborhoods":["High Pointe","Straus Ranch","Uptown Village","Cedar Hill Estates","Waterford Oaks","Cheyenne Crossing"],
     "landmarks":"Cedar Hill State Park, Joe Pool Lake, Uptown Village at Cedar Hill",
     "market":"scenic city on the Escarpment with beautiful views and Joe Pool Lake access, median home prices around $300k",
     "seller_situations":"relocation, inherited properties, divorce, landlords, homes needing updates"},
    {"slug":"lancaster","name":"Lancaster","county":"Dallas","zip":"75146","region":"Dallas County",
     "neighborhoods":["Historic Downtown Lancaster","Hensley Field area","Bear Creek","Rolling Hills","Brookwood"],
     "landmarks":"Historic Downtown Lancaster, Lancaster Country Club, Hensley Field",
     "market":"rapidly growing south Dallas suburb with easy highway access, median home prices around $280k",
     "seller_situations":"inherited properties, aging homeowners, divorce, relocation, homes needing significant repairs"},

    # ── Rockwall / Ellis / Johnson ─────────────────────────────────────────
    {"slug":"rockwall","name":"Rockwall","county":"Rockwall","zip":"75087","region":"Rockwall County",
     "neighborhoods":["Harbor area","Chandler Creek","Dalton Ranch","Shores","Stonelake Estates","Lakeview"],
     "landmarks":"Lake Ray Hubbard Harbor, Rockwall Harbor marina, Founders Plaza",
     "market":"lakeside city on Lake Ray Hubbard east of Dallas with scenic waterfront, median home prices around $430k",
     "seller_situations":"relocation, divorce, inherited lake properties, downsizing, upgrading families"},
    {"slug":"waxahachie","name":"Waxahachie","county":"Ellis","zip":"75165","region":"Ellis County",
     "neighborhoods":["Historic District","Creekside","Gingerbread Trail area","Mockingbird Hills","Pecan Creek","Wintergreen"],
     "landmarks":"Ellis County Courthouse, Scarborough Renaissance Festival, Gingerbread Trail historic homes",
     "market":"historic Crape Myrtle Capital of Texas with growing suburban development, median home prices around $300k",
     "seller_situations":"inherited historic homes, relocation, divorce, aging homeowners, homes needing restoration"},
    {"slug":"midlothian","name":"Midlothian","county":"Ellis","zip":"76065","region":"Ellis County",
     "neighborhoods":["Bryson","Crossroads","Arbor Hill","Mitchells Run","Milas Ranch","Creek View"],
     "landmarks":"Midlothian Conference Center, Fun Station Midlothian, Midlothian ISD stadiums",
     "market":"one of fastest-growing cities in Ellis County with new master-planned communities, median home prices around $350k",
     "seller_situations":"relocation, upgrading families, divorce, inherited properties, new construction competition"},
]

# ── Full city strip for DFW ────────────────────────────────────────────────
CITIES_BY_REGION = {
    "Collin County": ["Plano","Frisco","McKinney","Allen","Richardson","Prosper","Celina","Wylie","The Colony","Sachse"],
    "Denton County": ["Denton","Lewisville","Flower Mound","Little Elm","Coppell"],
    "Dallas County": ["Dallas","Garland","Irving","Grand Prairie","Mesquite","Carrollton","Farmers Branch","Rowlett","DeSoto","Duncanville","Cedar Hill","Lancaster"],
    "Tarrant County": ["Fort Worth","Arlington","Keller","Grapevine","Colleyville","Southlake","North Richland Hills","Hurst","Euless","Bedford","Mansfield","Burleson"],
    "Rockwall · Ellis · Johnson": ["Rockwall","Waxahachie","Midlothian"],
}

REGION_COLORS = {
    "Collin County": "#4ab840",
    "Denton County": "#6dd962",
    "Dallas County": "#4ab840",
    "Tarrant County": "#6dd962",
    "Rockwall · Ellis · Johnson": "#4ab840",
}


def generate_city_content(city: dict) -> dict:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    neighborhoods_str = ", ".join(city["neighborhoods"])

    prompt = f"""You are an expert real estate SEO content writer for Top DFW House Buyers, a cash home buying company serving Dallas-Fort Worth.

COMPANY: Top DFW House Buyers | Phone: 972-284-9713 | Website: topdfwhousebuyers.com | TX License #0657354

Write enhanced neighborhood-level landing page content for {city['name']}, {city['county']} County, TX.

NEIGHBORHOODS TO MENTION: {neighborhoods_str}
LOCAL LANDMARKS: {city['landmarks']}
MARKET CONTEXT: {city['market']}
COMMON SELLER SITUATIONS: {city['seller_situations']}

REQUIREMENTS:
1. 800-1000 words of unique helpful content
2. Mention at least 4 specific neighborhoods by name naturally in the content
3. Include what makes each mentioned neighborhood distinctive for sellers
4. 3 H2 sections with natural subheadings
5. 2 CTA sections mentioning 972-284-9713
6. Include Texas-specific considerations (community property, foundation issues, HOA)
7. Warm helpful tone
8. Meta title under 60 chars
9. Meta description under 160 chars

Return ONLY valid JSON (no markdown no backticks):
{{
  "meta_title": "...",
  "meta_description": "...",
  "h1": "We Buy Houses in {city['name']}, TX - Fast Cash Offers",
  "intro": "2-3 sentences mentioning the city and a specific neighborhood",
  "content_html": "HTML with h2 p ul li tags mentioning neighborhoods naturally",
  "why_sellers_title": "Why {city['name']} Homeowners Choose Us",
  "why_sellers_points": ["...", "...", "...", "..."]
}}"""

    prompt_safe = prompt.encode('ascii', errors='replace').decode('ascii')
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt_safe}]
    )
    raw = message.content[0].text.strip()
    raw = re.sub(r'^```json\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)
    return json.loads(raw)


def build_cities_strip(current_city_name: str) -> str:
    html = ''
    for region, cities in CITIES_BY_REGION.items():
        color = REGION_COLORS.get(region, "#4ab840")
        html += f'\n  <div style="margin-top:24px">\n    <div style="font-size:10px;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;color:{color};border:1px solid {color};padding:4px 12px;border-radius:2px;display:inline-block;margin-bottom:12px">{region}</div>\n    <div style="display:flex;flex-wrap:wrap;gap:7px">'
        for city_name in cities:
            slug = city_name.lower().replace(' ', '-')
            if city_name == current_city_name:
                style = f'background:{color};color:#fff;border-color:{color};padding:7px 14px;font-size:11px;font-weight:600;text-decoration:none;border-radius:2px;white-space:nowrap'
            else:
                style = 'background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.15);color:rgba(255,255,255,0.75);padding:7px 14px;font-size:11px;font-weight:600;text-decoration:none;border-radius:2px;white-space:nowrap'
            html += f'\n      <a href="/{slug}/" style="{style}">{city_name}</a>'
        html += '\n    </div>\n  </div>'
    return html


def build_city_page(content: dict, city: dict) -> str:
    slug = city['slug']
    year = datetime.now().year
    why_points = ''.join([f'<li style="font-size:15px;line-height:1.8;color:#3a4a3a;margin:8px 0">{p}</li>' for p in content.get('why_sellers_points', [])])
    cities_strip_html = build_cities_strip(city['name'])
    neighborhoods_pills = ' '.join([f'<span style="display:inline-block;background:rgba(74,184,64,0.1);border:1px solid rgba(74,184,64,0.3);color:#1a7a2a;font-size:11px;font-weight:600;padding:3px 10px;border-radius:2px;margin:3px">{n}</span>' for n in city['neighborhoods']])

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
<script async src="https://www.googletagmanager.com/gtag/js?id=G-QSBN8EDR9Z"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-QSBN8EDR9Z');</script>
<script type="text/javascript">(function(c,l,a,r,i,t,y){{c[a]=c[a]||function(){{(c[a].q=c[a].q||[]).push(arguments)}};t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);}})(window,document,"clarity","script","wiurnc9zu7");</script>
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"RealEstateAgent","name":"Top DFW House Buyers","telephone":"972-284-9713","url":"https://www.topdfwhousebuyers.com","areaServed":"{city['name']}, Texas"}}
</script>
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
{{"@type":"Question","name":"How fast can you buy my house in {city['name']}, TX?","acceptedAnswer":{{"@type":"Answer","text":"We can close in as few as 7 days in {city['name']}. Call 972-284-9713."}}}},
{{"@type":"Question","name":"Do I need to make repairs before selling my {city['name']} home?","acceptedAnswer":{{"@type":"Answer","text":"Never. We buy houses in {city['name']} in any condition."}}}},
{{"@type":"Question","name":"Are there fees when selling to Top DFW House Buyers?","acceptedAnswer":{{"@type":"Answer","text":"Zero fees, zero commissions, zero closing costs."}}}},
{{"@type":"Question","name":"What neighborhoods in {city['name']} do you buy houses in?","acceptedAnswer":{{"@type":"Answer","text":"We buy houses throughout all of {city['name']} including {', '.join(city['neighborhoods'][:4])} and more."}}}}
]}}
</script>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Montserrat:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{--navy:#1a1f1a;--gold:#4ab840;--gold-light:#6dd962;--cream:#f8faf8;--border:#d4e4d2;--muted:#52675f}}
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
.neighborhoods-strip{{background:#f8faf8;border:1px solid var(--border);border-left:4px solid #4ab840;padding:20px 24px;margin:28px 0}}
.neighborhoods-strip h3{{font-size:14px;font-weight:700;color:#1a1f1a;margin-bottom:12px}}
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
.why-box li:last-child{{border:none}}
.cta-box{{background:#f8faf8;border:1px solid var(--border);border-left:4px solid #4ab840;padding:24px 28px;margin:32px 0}}
.cta-box h3{{font-size:16px;font-weight:700;color:#1a1f1a;margin-bottom:8px}}
.cta-box p{{font-size:13px;color:var(--muted);margin-bottom:16px;line-height:1.7}}
.cta-box a{{display:inline-block;background:#1a1f1a;color:#fff;padding:12px 24px;font-weight:700;font-size:12px;text-decoration:none;border-radius:2px;letter-spacing:0.06em;text-transform:uppercase}}
.sidebar{{position:sticky;top:80px}}
.sidebar-card{{background:#fff;border:1px solid var(--border);border-top:3px solid #4ab840;padding:24px;margin-bottom:20px}}
.sidebar-card h3{{font-size:14px;font-weight:700;color:#1a1f1a;margin-bottom:8px}}
.sidebar-phone{{font-size:22px;font-weight:700;color:#4ab840;text-decoration:none;display:block;margin-bottom:12px}}
.sidebar-btn{{display:block;background:#1a1f1a;color:#fff;padding:12px;font-weight:700;font-size:11px;text-decoration:none;border-radius:2px;letter-spacing:0.06em;text-transform:uppercase;text-align:center;margin-bottom:8px}}
.sidebar-btn.green{{background:#4ab840}}
.cities-section{{background:#1a1f1a;padding:48px 40px}}
.cities-section h2{{font-family:'Playfair Display',serif;font-size:24px;color:#fff;margin-bottom:24px;text-align:center}}
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
    <a href="/">Home</a><a href="/blog/">Blog</a>
    <a href="tel:9722849713">972-284-9713</a>
    <a href="/#offer" class="nav-cta">Get Cash Offer</a>
  </div>
</nav>
<section class="hero">
  <div class="hero-inner">
    <div>
      <div class="hero-eyebrow">{city['name']}, {city['county']} County, TX</div>
      <h1>{content['h1'].replace('Fast Cash Offers','<em>Fast Cash Offers</em>')}</h1>
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
        <div class="field-group"><label>Your Name *</label><input type="text" name="name" placeholder="John Smith" required></div>
        <div class="field-group"><label>Property Address *</label><input type="text" name="address" placeholder="{city['name']}, TX {city['zip']}" required></div>
        <div class="field-grid">
          <div class="field-group"><label>Phone *</label><input type="tel" name="phone" placeholder="(972) 555-0000" required></div>
          <div class="field-group"><label>Email</label><input type="email" name="email" placeholder="john@email.com"></div>
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
      <div class="form-success" id="form-success" style="display:none;text-align:center;padding:24px">
        <div style="font-size:40px;margin-bottom:10px">✅</div>
        <h3 style="font-family:'Playfair Display',serif;font-size:20px;color:#1a1f1a;margin-bottom:8px">Got It!</h3>
        <p style="font-size:13px;color:var(--muted)">We will call you within 30 minutes.<br><strong>972-284-9713</strong></p>
      </div>
      <div class="form-guarantee">100% confidential · No obligation · No spam</div>
    </div>
  </div>
</section>
<div class="content-wrap">
  <div class="main-content">
    <p style="font-size:16px;line-height:1.9;color:#2a3a2a;font-weight:400;margin-bottom:24px">{content['intro']}</p>
    <div class="neighborhoods-strip">
      <h3>Neighborhoods We Buy Houses In — {city['name']}</h3>
      <div style="margin-top:8px">{neighborhoods_pills}</div>
    </div>
    {content['content_html']}
    <div class="why-box">
      <h2>{content['why_sellers_title']}</h2>
      <ul>{why_points}</ul>
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
      <p style="font-size:12px;color:var(--muted);margin-bottom:14px">No fees, no repairs. Close in 7 days or on your schedule.</p>
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
      <p style="font-size:12px;color:var(--muted);line-height:1.6;margin-bottom:12px">Leave us a Google review — it helps other DFW homeowners find us.</p>
      <a href="https://share.google/vGlYZ46PBCsE6BPhz" target="_blank" rel="noopener" style="display:block;background:#4ab840;color:#fff;padding:10px;font-weight:700;font-size:11px;text-decoration:none;border-radius:2px;letter-spacing:0.06em;text-transform:uppercase;text-align:center">Leave a Google Review ⭐</a>
    </div>
  </div>
</div>
<div class="cities-section">
  <h2>We Buy Houses Across All of DFW</h2>
  {cities_strip_html}
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
async function submitForm(e){{
  e.preventDefault();
  const form=document.getElementById('city-form');
  const btn=form.querySelector('.submit-btn');
  btn.textContent='Submitting...';btn.disabled=true;
  try{{const fd=new FormData(form);await fetch('/',{{method:'POST',headers:{{'Content-Type':'application/x-www-form-urlencoded'}},body:new URLSearchParams(fd).toString()}});}}catch(e){{}}
  form.style.display='none';document.getElementById('form-success').style.display='block';
}}
</script>
</body>
</html>"""


def main():
    print(f"Generating {len(CITIES)} enhanced DFW city pages — {datetime.now().isoformat()}")
    print()
    for i, city in enumerate(CITIES):
        slug = city['slug']
        output_dir = Path(slug)
        output_file = output_dir / "index.html"
        print(f"  [{i+1}/{len(CITIES)}] {city['name']} ({city['region']})...")
        try:
            content = generate_city_content(city)
            html = build_city_page(content, city)
            output_dir.mkdir(parents=True, exist_ok=True)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"    ✓ {output_file}")
        except Exception as e:
            print(f"    ✗ Error on {city['name']}: {e}")
    print()
    print(f"Done! {len(CITIES)} cities processed.")
    print("Commit all folders to GitHub — Netlify will auto-deploy.")


if __name__ == "__main__":
    main()
