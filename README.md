# Top DFW House Buyers — Website & Blog Automation

## What This Does

This repository powers the automated blog system for [topdfwhousebuyers.com](https://www.topdfwhousebuyers.com).

**Every Monday and Thursday at 8am CT**, GitHub Actions automatically:
1. Picks the next topic from the queue (80+ topics covering cities, divorce, foreclosure, inheritance, education, and more)
2. Calls Claude AI to write a 1,200-word SEO-optimized blog post
3. Builds a complete HTML page with proper meta tags and schema markup
4. Commits it to this repo
5. Netlify automatically deploys it to the live site

## Blog Topics Covered

- **22+ DFW cities** — Plano, Frisco, Allen, McKinney, Richardson, The Colony, Lewisville, Flower Mound, Keller, Grapevine, Colleyville, Southlake, NRH, Hurst, Euless, Bedford, Watauga, Prosper, Celina, Anna, Melissa, Dallas + more
- **Foreclosure** — how to stop it, pre-foreclosure options, selling before foreclosure
- **Divorce** — Texas community property, selling during divorce, fast sale benefits
- **Inheritance** — probate process, inherited property, estate sales
- **Cash buyer education** — how it works, cash vs. agent, real costs, timelines
- **Specific situations** — tenants, foundation issues, fire damage, mold, code violations, liens, hoarder homes, vacant properties, financial hardship, relocation, downsizing, rental properties
- **DFW market** — market conditions, pricing, seller tips

## Setup

### 1. Add your Anthropic API key to GitHub Secrets

1. Go to your repo → **Settings → Secrets and variables → Actions**
2. Click **New repository secret**
3. Name: `ANTHROPIC_API_KEY`
4. Value: your Claude API key (starts with `sk-ant-`)
5. Click **Add secret**

### 2. Connect to Netlify

1. In Netlify → **Add new site → Import an existing project → GitHub**
2. Select this repository
3. Build command: (leave empty)
4. Publish directory: `.` (root)
5. Deploy

Netlify will auto-deploy every time GitHub gets a new blog post.

### 3. That's it

Posts generate automatically every Monday and Thursday. Check the **Actions** tab in GitHub to see each run.

## Manual Trigger

You can trigger a post manually anytime:
1. Go to **Actions** tab in GitHub
2. Click **Generate Blog Post**
3. Click **Run workflow**

## File Structure

```
/
├── index.html              ← Your main website
├── blog/
│   ├── index.html          ← Blog listing page
│   ├── tracking.json       ← Tracks which topics have been posted
│   └── [slug]/
│       └── index.html      ← Each generated blog post
├── scripts/
│   └── generate_post.py   ← The blog generation script
└── .github/
    └── workflows/
        └── generate-blog.yml  ← The automation schedule
```

## Monitoring

- **GitHub Actions tab** — see every run, success/failure, and output logs
- **Netlify deploys** — each new post triggers an automatic deploy
- Posts appear at: `topdfwhousebuyers.com/blog/[slug]/`
