import streamlit as st
import requests
import json
import base64
import pandas as pd
import google.generativeai as genai
from datetime import datetime
from collections import Counter

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="EXD Backlink Intelligence",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Design system ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background-color: #0a0a0a !important;
    color: #f0f0f0 !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stAppViewContainer"] > .main { background-color: #0a0a0a !important; }
.main .block-container {
    max-width: 960px !important;
    margin: 0 auto !important;
    padding: 2.5rem 1.5rem 5rem !important;
}
#MainMenu, footer, header, [data-testid="stToolbar"] { display: none !important; }
[data-testid="stSidebar"] { display: none !important; }
h1,h2,h3,h4 { font-family: 'Inter', sans-serif !important; }

/* Header */
.exd-header { text-align:center; margin-bottom:2.5rem; padding-bottom:2rem; border-bottom:1px solid #1a1a1a; }
.exd-wordmark { font-size:11px; font-weight:700; letter-spacing:0.25em; color:#ff6b2b; text-transform:uppercase; margin-bottom:0.75rem; }
.exd-title { font-size:2rem; font-weight:800; color:#fff; margin-bottom:0.4rem; }
.exd-subtitle { font-size:0.875rem; color:#555; }

/* Section label */
.section-label { display:flex; align-items:center; gap:0.75rem; margin-bottom:1rem; margin-top:2.25rem; }
.section-number { width:26px; height:26px; background:#ff6b2b; color:#fff; font-size:11px; font-weight:700; border-radius:50%; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.section-title { font-size:0.75rem; font-weight:700; letter-spacing:0.14em; text-transform:uppercase; color:#888; }

/* Inputs */
[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] > div > div,
[data-testid="stTextArea"] textarea {
    background:#141414 !important; border:1px solid #242424 !important;
    border-radius:6px !important; color:#f0f0f0 !important;
    font-family:'Inter',sans-serif !important; font-size:0.875rem !important;
}
[data-testid="stTextInput"] input:focus { border-color:#ff6b2b !important; }
label, [data-testid="stWidgetLabel"] p {
    color:#666 !important; font-size:0.72rem !important; font-weight:600 !important;
    letter-spacing:0.07em !important; text-transform:uppercase !important;
    font-family:'Inter',sans-serif !important;
}

/* Buttons */
.stButton > button {
    background:#ff6b2b !important; color:#fff !important; border:none !important;
    border-radius:6px !important; font-family:'Inter',sans-serif !important;
    font-weight:700 !important; font-size:0.75rem !important;
    letter-spacing:0.09em !important; text-transform:uppercase !important;
    padding:0.6rem 1.5rem !important; transition:all 0.15s !important;
}
.stButton > button:hover { background:#e55a1f !important; transform:translateY(-1px) !important; }

/* Stat cards */
.stat-card {
    background:#111; border:1px solid #1e1e1e; border-radius:8px; padding:1rem 1.25rem;
}
.stat-card.client { border-top:2px solid #ff6b2b; }
.stat-card.competitor { border-top:2px solid #2a2a2a; }
.stat-label { font-size:0.63rem; font-weight:700; letter-spacing:0.1em; text-transform:uppercase; color:#444; margin-bottom:0.25rem; }
.stat-domain { font-size:0.82rem; font-weight:700; color:#ccc; margin-bottom:0.65rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.stat-metric { display:flex; justify-content:space-between; margin-bottom:0.2rem; }
.stat-metric-label { font-size:0.68rem; color:#555; }
.stat-metric-value { font-size:0.68rem; font-weight:700; color:#fff; }
.stat-metric-value.hi { color:#ff6b2b; }
.dr-bar-bg { background:#1a1a1a; border-radius:3px; height:4px; margin:0.3rem 0 0.5rem; }
.dr-bar-fill { height:4px; border-radius:3px; background:#ff6b2b; }

/* Domain cards */
.domain-card {
    background:#111; border:1px solid #1e1e1e; border-radius:8px;
    padding:1.1rem 1.3rem; margin-bottom:0.55rem; transition:border-color 0.2s;
}
.domain-card:hover { border-color:#2a2a2a; }
.card-top { display:flex; align-items:flex-start; justify-content:space-between; gap:1rem; }
.card-domain { font-size:0.95rem; font-weight:700; color:#fff; }
.card-badges { display:flex; gap:0.35rem; flex-wrap:wrap; flex-shrink:0; }
.card-metrics { display:flex; gap:1.25rem; margin-top:0.5rem; flex-wrap:wrap; }
.card-metric { font-size:0.7rem; color:#555; }
.card-metric span { color:#ccc; font-weight:600; }
.card-rationale { font-size:0.77rem; color:#666; line-height:1.55; margin-top:0.55rem; font-style:italic; }

/* Badges */
.badge { display:inline-block; font-size:0.6rem; font-weight:700; letter-spacing:0.07em; text-transform:uppercase; padding:0.17rem 0.42rem; border-radius:3px; }
.badge-free      { background:rgba(34,197,94,0.1);  color:#22c55e; }
.badge-paid      { background:rgba(234,179,8,0.1);  color:#eab308; }
.badge-publisher { background:rgba(139,92,246,0.1); color:#8b5cf6; }
.badge-blog      { background:rgba(59,130,246,0.1); color:#3b82f6; }
.badge-top       { background:rgba(255,107,43,0.15);color:#ff6b2b; }
.badge-missed    { background:rgba(239,68,68,0.1);  color:#ef4444; }
.badge-unique    { background:rgba(20,184,166,0.1); color:#14b8a6; }

/* Relevance */
.rel-score { display:inline-flex; align-items:center; gap:0.3rem; }
.rel-dot { width:7px; height:7px; border-radius:50%; display:inline-block; }

/* Tabs */
[data-testid="stTabs"] [role="tablist"] {
    background:#111 !important; border-radius:8px !important;
    padding:0.25rem !important; border:1px solid #1e1e1e !important; flex-wrap:wrap !important;
}
[data-testid="stTabs"] button[role="tab"] {
    background:transparent !important; color:#555 !important;
    font-family:'Inter',sans-serif !important; font-size:0.7rem !important;
    font-weight:700 !important; letter-spacing:0.06em !important;
    text-transform:uppercase !important; border-radius:5px !important; border:none !important;
}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    background:#ff6b2b !important; color:#fff !important;
}

/* Alert */
.exd-alert {
    background:rgba(255,107,43,0.07); border:1px solid rgba(255,107,43,0.18);
    border-radius:6px; padding:0.7rem 1rem; font-size:0.78rem; color:#ff6b2b; margin-bottom:1rem;
}

/* Expander */
[data-testid="stExpander"] { background:#111 !important; border:1px solid #1e1e1e !important; border-radius:8px !important; }
[data-testid="stExpander"] summary { color:#666 !important; font-size:0.75rem !important; }

hr { border:none; border-top:1px solid #181818 !important; margin:2rem 0 !important; }
[data-testid="stNumberInput"] input { background:#141414 !important; border:1px solid #242424 !important; color:#f0f0f0 !important; }
</style>
""", unsafe_allow_html=True)

# ── Utilities ─────────────────────────────────────────────────────────────────

def get_dfs_headers():
    login    = st.secrets.get("DATAFORSEO_BACKLINK_LOGIN", st.secrets.get("DATAFORSEO_LOGIN", ""))
    password = st.secrets.get("DATAFORSEO_BACKLINK_PASSWORD", st.secrets.get("DATAFORSEO_PASSWORD", ""))
    token    = base64.b64encode(f"{login}:{password}".encode()).decode()
    return {"Authorization": f"Basic {token}", "Content-Type": "application/json"}

def get_gemini():
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    return genai.GenerativeModel("gemini-2.5-flash")

def dfs_post(endpoint, payload):
    r = requests.post(f"https://api.dataforseo.com/v3/{endpoint}",
                      headers=get_dfs_headers(), json=payload, timeout=60)
    r.raise_for_status()
    data = r.json()
    if data.get("status_code") != 20000:
        raise ValueError(f"DataForSEO: {data.get('status_message')}")
    return data

def clean_domain(url: str) -> str:
    url = url.strip().lower()
    for p in ["https://www.", "http://www.", "https://", "http://", "www."]:
        if url.startswith(p):
            url = url[len(p):]
    return url.rstrip("/")

def rel_color(score):
    if score >= 8: return "#22c55e"
    if score >= 5: return "#ff6b2b"
    return "#555"

def fmt_num(n):
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1_000:     return f"{n/1_000:.1f}K"
    return str(n)

def dr_bar_html(rank):
    pct = min(int((rank / 100) * 100), 100)
    return f'<div class="dr-bar-bg"><div class="dr-bar-fill" style="width:{pct}%"></div></div>'

def section_header(num, title):
    st.markdown(f"""
    <div class="section-label">
        <div class="section-number">{num}</div>
        <div class="section-title">{title}</div>
    </div>""", unsafe_allow_html=True)

# ── DataForSEO ────────────────────────────────────────────────────────────────

def fetch_summaries(domains):
    payload = [{"target": clean_domain(d), "include_subdomains": True} for d in domains]
    data    = dfs_post("backlinks/summary/live", payload)
    out     = {}
    for task in data.get("tasks", []):
        if task.get("result"):
            r = task["result"][0]
            out[r["target"]] = {
                "rank":              r.get("rank", 0),
                "backlinks":         r.get("backlinks", 0),
                "referring_domains": r.get("referring_domains", 0),
                "spam_score":        r.get("backlinks_spam_score", 0),
            }
    return out

def fetch_intersection(competitors, exclude):
    targets = {str(i+1): clean_domain(d) for i, d in enumerate(competitors)}
    payload = [{
        "targets":                    targets,
        "exclude_targets":            [clean_domain(exclude)],
        "limit":                      60,
        "order_by":                   ["1.rank,desc"],
        "exclude_internal_backlinks": True,
        "backlinks_filters":          ["dofollow", "=", True],
        "filters":                    ["backlinks_spam_score", "<", 40],
    }]
    data  = dfs_post("backlinks/domain_intersection/live", payload)
    items = []
    for task in data.get("tasks", []):
        if task.get("result"):
            for r in task["result"]:
                for item in r.get("items", []):
                    first = item.get("domain_intersection", {}).get("1", {})
                    if first.get("target"):
                        items.append({
                            "domain":     first.get("target", ""),
                            "rank":       first.get("rank", 0),
                            "backlinks":  first.get("backlinks", 0),
                            "spam_score": first.get("backlinks_spam_score", 0),
                            "source":     "intersection",
                        })
    return items

def fetch_referring(competitor, limit=30):
    payload = [{
        "target":                     clean_domain(competitor),
        "exclude_internal_backlinks": True,
        "backlinks_filters":          ["dofollow", "=", True],
        "filters":                    ["backlinks_spam_score", "<", 40],
        "order_by":                   ["rank,desc"],
        "limit":                      limit,
    }]
    data  = dfs_post("backlinks/referring_domains/live", payload)
    items = []
    for task in data.get("tasks", []):
        if task.get("result"):
            for r in task["result"]:
                for item in r.get("items", []):
                    items.append({
                        "domain":     item.get("domain", ""),
                        "rank":       item.get("rank", 0),
                        "backlinks":  item.get("backlinks", 0),
                        "spam_score": item.get("backlinks_spam_score", 0),
                        "source":     "referring",
                        "competitor": competitor,
                    })
    return items

# ── AI ────────────────────────────────────────────────────────────────────────

def ai_suggest_competitors(name, url, industry, market, language):
    model  = get_gemini()
    prompt = f"""You are an SEO expert.
Client: {name} ({url}) | Industry: {industry} | Market: {market} | Language: {language}
Return exactly 3 direct competitor root domains (no paths, no https://).
Return ONLY a JSON array: ["domain1.com","domain2.com","domain3.com"]
No explanation. No markdown. Pure JSON only."""
    r    = model.generate_content(prompt)
    text = r.text.strip().replace("```json","").replace("```","").strip()
    return json.loads(text)

def ai_enrich(domains, client_name, industry, market, language):
    model       = get_gemini()
    domain_list = "\n".join([
        f"- {d['domain']} (DR:{d.get('rank',0)}, backlinks:{d.get('backlinks',0)}, spam:{d.get('spam_score',0)})"
        for d in domains[:50]
    ])
    prompt = f"""You are a senior link-building strategist at a digital agency.
Client industry: {industry} | Market: {market} | Language: {language}

Analyze these domains and classify each one. Return ONLY a valid JSON array, no markdown fences, no explanation.

Domains:
{domain_list}

For each domain return exactly this structure:
{{
  "domain": "domain.com",
  "category": "free|paid|publisher|blog",
  "rationale": "One sentence, max 18 words, explaining why this domain is valuable for {industry} link building.",
  "contact_hint": "Practical outreach note e.g. Submit via /write-for-us page, Email editor via LinkedIn, Use contact form at /contact",
  "relevance_score": 7,
  "is_top_influential": false
}}

Category rules — pick the BEST fit:
- free: accepts guest posts, write-for-us, editorial submissions at no cost
- paid: sponsored content, paid placements, native ads, advertorial
- publisher: major media, news outlets, trade publications, industry press  
- blog: independent blogs, niche content sites, influencer blogs
- link_domain: pure link-building domains — private blog networks, link farms, paid backlink marketplaces, directories primarily used for DA/DR boosting (e.g. sites like fatjoe.com suppliers, linkbuilder.io domains)

IMPORTANT: Most domains will be free, publisher, or blog. Use link_domain only for sites whose PRIMARY purpose is selling/providing backlinks for SEO rather than publishing genuine content.

Set is_top_influential=true for the 10 most impactful domains for {industry} in {market}.
relevance_score is an integer 1-10."""

    r    = model.generate_content(prompt, generation_config={"max_output_tokens": 4096})
    text = r.text.strip().replace("```json","").replace("```","").strip()
    ai   = {d["domain"]: d for d in json.loads(text)}

    enriched = []
    for d in domains[:50]:
        a = ai.get(d["domain"], {})
        enriched.append({
            **d,
            "category":           a.get("category", "free"),
            "rationale":          a.get("rationale", ""),
            "contact_hint":       a.get("contact_hint", "Check website contact page"),
            "relevance_score":    a.get("relevance_score", 5),
            "is_top_influential": a.get("is_top_influential", False),
        })
    return sorted(enriched, key=lambda x: x.get("relevance_score", 0), reverse=True)

def ai_opportunities(industry, market, competitors, tab_type):
    """Pure AI-generated opportunities split into industry-specific and generic."""
    model = get_gemini()
    comp_context = f"Competitors in this space: {', '.join(competitors)}" if competitors else ""

    tab_instructions = {
        "top": f"""Return the TOP 20 most valuable domains for link building for a brand in {industry} in {market}.
These should be the highest-impact opportunities considering authority, relevance, and likelihood of acceptance.
Blend competitor context if provided. Mix industry-specific and well-known cross-industry sites.
{comp_context}""",

        "publishers": f"""Return the TOP 20 media outlets, news sites, trade publications, and high-authority editorial sites
relevant to {industry} in {market}. Include both industry-specific outlets AND major generic publishers
(Forbes, Entrepreneur, Gulf News, Arabian Business, etc.) that accept contributions.
{comp_context}""",

        "guest_posting": f"""Return the TOP 20 domains that actively accept guest posts and allow contributors to link back to their website.
Include both {industry}-specific sites AND generic high-authority guest posting platforms (Medium, HubSpot Blog,
Moz Blog, Search Engine Journal, etc.). Prioritize sites with active write-for-us programs.
{comp_context}""",

        "backlink_providers": f"""Return 20 well-known backlink service providers and directory/listing sites useful for {industry} in {market}.
Split into:
- Services: FatJoe, Adsy, Authority Builders, LinksThatRank, GetMeLinks, uSERP, etc.
- Directories/Forums: relevant industry directories, local listing sites, forum platforms, Yellow Pages equivalents for {market}.
These are NOT editorial sites — they are platforms specifically used to acquire backlinks."""
    }

    prompt = f"""You are a senior link-building strategist.
Industry: {industry} | Market: {market}

{tab_instructions.get(tab_type, tab_instructions["top"])}

For each domain classify whether it is "industry_specific" or "generic".
- industry_specific: directly relevant to {industry} or {market}
- generic: valuable for any industry/brand

Return ONLY a valid JSON array, no markdown, no explanation:
[
  {{
    "domain": "example.com",
    "specificity": "industry_specific",
    "dr_estimate": 75,
    "rationale": "One sentence max 18 words why this domain matters for link building here.",
    "contact_hint": "Practical outreach note e.g. Submit via /write-for-us, Use contact form, Email editor@domain.com",
    "relevance_score": 8
  }}
]

dr_estimate: your best estimate of the domain's authority (1-100).
relevance_score: integer 1-10 for how valuable this is for {industry} in {market}."""

    r    = model.generate_content(prompt, generation_config={"max_output_tokens": 4096})
    raw  = r.text.strip().replace("```json","").replace("```","").strip()
    data = json.loads(raw)
    return sorted(data, key=lambda x: x.get("relevance_score", 0), reverse=True)

def ai_generate_content(topic, length, tone, language, brand_terms, target_prompts, primary_kw, secondary_kws, client_name, industry, client_url):
    model  = get_gemini()
    prompt = f"""You are a senior content strategist writing for {client_name} in {industry}.

Write a guest post / outreach article with these specifications:
- Topic: {topic}
- Word count: {length} words
- Tone: {tone}
- Language: write the entire article in {language}
- Brand terms (use naturally): {brand_terms}
- AI prompts / questions to target: {target_prompts}
- Primary keyword: {primary_kw}
- Secondary keywords: {secondary_kws}
- Client website: {client_url}

Formatting requirements:
- Use markdown: ## for H2, ### for H3
- Make ALL H2 and H3 headings bold using **heading text**
- Bold every instance of the primary keyword and secondary keywords throughout the article using **keyword**
- Primary keyword must appear in the title, first paragraph, and at least 2 subheadings
- Secondary keywords woven naturally throughout
- Brand terms authentic, not forced
- Non-salesy conclusion
- Do NOT include byline, author bio, or meta description

Internal linking:
- At the end of the article, add a section titled "## **Internal Link Suggestions**"
- Suggest 3 internal links the editor should add when publishing on {client_url}
- Format each as: [Anchor text suggestion] → Page type: (e.g. project page, blog post, contact page, about page) — Reason: (one sentence why this link adds value here)
- These are editorial suggestions — the publisher will map real URLs

Write the full article now."""
    r = model.generate_content(prompt, generation_config={"max_output_tokens": 4096})
    return r.text

# ── Session state ─────────────────────────────────────────────────────────────

def init_state():
    defaults = {
        "page":              "input",
        "client":            {},
        "competitors":       [],
        "summaries":         {},
        "enriched":          [],
        "raw_domains":       [],
        "generated_content": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ── Header ────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="exd-header">
    <div class="exd-wordmark">Performics EXD · Publicis Groupe</div>
    <div class="exd-title">Backlink Intelligence</div>
    <div class="exd-subtitle">AI-powered off-page opportunity discovery & content generation</div>
</div>
""", unsafe_allow_html=True)

# ── Top navigation (shown on all pages except input) ─────────────────────────

if st.session_state.page != "input":
    _, _, col_new = st.columns([3, 3, 1])
    with col_new:
        if st.button("← New Analysis", key="nav_new"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()
    st.markdown("<hr>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE — INPUT
# ══════════════════════════════════════════════════════════════════════════════

if st.session_state.page == "input":

    section_header("1", "Client Details")

    c1, c2 = st.columns(2)
    with c1:
        client_name = st.text_input("Client Name", placeholder="e.g. Sobha Realty")
        industry    = st.selectbox("Industry", [
            "Telecommunications","Finance & Banking","Retail & E-commerce",
            "Travel & Tourism","Healthcare","Real Estate","Technology & SaaS",
            "Education","Food & Beverage","Automotive","Energy & Utilities",
            "Government & Public Sector","Media & Entertainment","Other"
        ])
    with c2:
        client_url = st.text_input("Client URL", placeholder="e.g. sobharealty.com")
        market     = st.selectbox("Market", [
            "UAE","Saudi Arabia","Oman","Qatar","Kuwait","Bahrain",
            "Egypt","Jordan","Lebanon","Global","UK","US","Other"
        ])

    language = st.selectbox("Language", ["English","Arabic","English & Arabic","French","Other"])

    # ── Two-path selection ────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    section_header("2", "What would you like to do?")

    st.markdown("""
    <style>
    .path-card {
        background:#111; border:1px solid #1e1e1e; border-radius:10px;
        padding:1.5rem 1.75rem; transition:border-color 0.2s;
    }
    .path-icon { font-size:1.5rem; margin-bottom:0.5rem; }
    .path-title { font-size:0.95rem; font-weight:800; color:#fff; margin-bottom:0.35rem; }
    .path-desc { font-size:0.76rem; color:#555; line-height:1.55; margin-bottom:0.85rem; }
    .path-features { list-style:none; padding:0; margin:0; }
    .path-features li { font-size:0.72rem; color:#555; padding:0.15rem 0; }
    .path-features li::before { content:"→ "; color:#ff6b2b; font-weight:700; }
    </style>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:1.25rem;">
        <div class="path-card">
            <div class="path-icon">🔗</div>
            <div class="path-title">Backlink Opportunity Analysis</div>
            <div class="path-desc">Discover the best domains to target for link building, powered by DataForSEO and AI.</div>
            <ul class="path-features">
                <li>Top 10 influential domains by industry and market</li>
                <li>Free, paid, publisher and blog opportunities</li>
                <li>Competitive intelligence and link gap analysis</li>
                <li>Contact pathway per domain</li>
                <li>CSV export per category</li>
            </ul>
        </div>
        <div class="path-card">
            <div class="path-icon">✍️</div>
            <div class="path-title">Content Creation</div>
            <div class="path-desc">Generate guest post and outreach content tailored to your brand, keywords and target publisher.</div>
            <ul class="path-features">
                <li>Topic, tone and keyword brief</li>
                <li>AI-generated full article</li>
                <li>Brand terms and AI prompt targeting</li>
                <li>Human review before outreach</li>
                <li>Download as .txt</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_a, col_c = st.columns(2)
    with col_a:
        go_analysis = st.button("▶  Backlink Analysis", use_container_width=True, key="go_analysis")
    with col_c:
        go_content = st.button("✍  Content Creation", use_container_width=True, key="go_content")

    # Content path — no analysis needed
    if go_content:
        if not client_name or not client_url:
            st.error("Client name and URL are required before continuing.")
        else:
            st.session_state.client = {
                "name": client_name, "url": client_url,
                "industry": industry, "market": market, "language": language,
            }
            st.session_state.page = "content"
            st.rerun()

    # Analysis path — reveal competitor inputs
    if go_analysis:
        if not client_name or not client_url:
            st.error("Client name and URL are required.")
        else:
            st.session_state.client = {
                "name": client_name, "url": client_url,
                "industry": industry, "market": market, "language": language,
            }
            st.session_state.show_competitors = True

    if st.session_state.get("show_competitors"):
        st.markdown("<br>", unsafe_allow_html=True)
        section_header("3", "Competitors")
        st.markdown('<div class="exd-alert">Enter up to 3 competitor URLs — or leave blank and AI will suggest them.</div>', unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1: comp1 = st.text_input("Competitor 1", placeholder="emaar.com")
        with c2: comp2 = st.text_input("Competitor 2", placeholder="damac.com")
        with c3: comp3 = st.text_input("Competitor 3", placeholder="nakheel.com")

        st.markdown("<br>", unsafe_allow_html=True)
        run = st.button("▶  Run Analysis Now", use_container_width=True, key="run_analysis")
    else:
        comp1 = comp2 = comp3 = ""
        run = False

    if run:
        if not client_name or not client_url:
            st.error("Client name and URL are required.")
        else:
            st.session_state.client = {
                "name": client_name, "url": client_url,
                "industry": industry, "market": market, "language": language,
            }
            competitors = [c for c in [comp1, comp2, comp3] if c.strip()]
            errors      = []

            if not competitors:
                with st.spinner("AI suggesting competitors…"):
                    try:
                        competitors = ai_suggest_competitors(client_name, client_url, industry, market, language)
                        st.success(f"✓ AI suggested: {', '.join(competitors)}")
                    except Exception as e:
                        errors.append(f"Competitor suggestion: {e}")
                        st.error(f"⚠ Gemini failed: {e}")
                        st.warning("Please enter competitors manually and try again.")

            if not competitors:
                st.stop()

            st.session_state.competitors = competitors

            with st.spinner("Fetching backlink profiles…"):
                try:
                    st.session_state.summaries = fetch_summaries([client_url] + competitors)
                    st.success(f"✓ Backlink profiles fetched ({len(st.session_state.summaries)} domains)")
                except Exception as e:
                    errors.append(f"Backlink summary: {e}")
                    st.warning(f"⚠ Backlink summary failed: {e}")
                    st.session_state.summaries = {}

            raw = []

            with st.spinner("Running link gap analysis…"):
                try:
                    inter = fetch_intersection(competitors, client_url)
                    raw.extend(inter)
                    st.success(f"✓ Link gap: {len(inter)} opportunities found")
                except Exception as e:
                    errors.append(f"Domain intersection: {e}")
                    st.warning(f"⚠ Domain intersection failed: {e}")

            with st.spinner("Fetching competitor referring domains…"):
                try:
                    for comp in competitors[:2]:
                        refs = fetch_referring(comp, limit=30)
                        raw.extend(refs)
                    st.success(f"✓ Referring domains fetched")
                except Exception as e:
                    errors.append(f"Referring domains: {e}")
                    st.warning(f"⚠ Referring domains failed: {e}")

            seen, unique = set(), []
            for d in sorted(raw, key=lambda x: x.get("rank", 0), reverse=True):
                if d["domain"] and d["domain"] not in seen:
                    seen.add(d["domain"])
                    unique.append(d)
            st.session_state.raw_domains = unique[:50]

            if unique:
                with st.spinner("AI analyzing and categorizing domains…"):
                    try:
                        enriched = ai_enrich(
                            unique[:50],
                            client_name, industry, market, language
                        )
                        st.session_state.enriched = enriched
                        st.success(f"✓ AI enriched {len(enriched)} domains")
                    except Exception as e:
                        errors.append(f"AI enrichment: {e}")
                        st.error(f"⚠ AI enrichment failed: {e}")
                        st.session_state.enriched = unique[:50]
            else:
                st.session_state.enriched = []
                if errors:
                    st.error("No domain data returned. DataForSEO Backlinks API may not be active yet.")

            if errors:
                with st.expander("⚠ Error details"):
                    for e in errors:
                        st.code(str(e))

            st.session_state.page = "dashboard"
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE — INTELLIGENCE DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

elif st.session_state.page == "dashboard":

    client      = st.session_state.client
    enriched    = st.session_state.enriched
    summaries   = st.session_state.summaries
    competitors = st.session_state.competitors
    raw_domains = st.session_state.raw_domains

    if st.button("✍  Go to Content Generation →", key="dash_to_content"):
        st.session_state.page = "content"
        st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Domain card renderer ──────────────────────────────────────────────────

    def domain_card(d, key_prefix):
        domain    = d.get("domain", "")
        rank      = d.get("rank", 0)
        backlinks = d.get("backlinks", 0)
        spam      = d.get("spam_score", 0)
        rel       = d.get("relevance_score", 5)
        rationale = d.get("rationale", "")
        contact   = d.get("contact_hint", "Check website contact page")
        cat       = d.get("category", "free")

        badges = f'<span class="badge badge-{cat}">{cat}</span>'
        if d.get("is_top_influential"): badges += ' <span class="badge badge-top">Top</span>'
        if d.get("is_missed"):          badges += ' <span class="badge badge-missed">Missed</span>'
        if d.get("is_unique"):          badges += ' <span class="badge badge-unique">Unique</span>'

        rc   = rel_color(rel)
        rdot = f'<span class="rel-dot" style="background:{rc}"></span>'

        st.markdown(f"""
        <div class="domain-card">
            <div class="card-top">
                <div class="card-domain">{domain}</div>
                <div class="card-badges">{badges}</div>
            </div>
            <div class="card-metrics">
                <div class="card-metric">DR <span>{rank}</span></div>
                <div class="card-metric">Backlinks <span>{fmt_num(backlinks)}</span></div>
                <div class="card-metric">Spam <span>{spam}</span></div>
                <div class="card-metric">Relevance <span class="rel-score">{rdot} <span style="color:{rc};font-weight:700">{rel}/10</span></span></div>
            </div>
            <div class="card-rationale">{rationale}</div>
        </div>""", unsafe_allow_html=True)

        with st.expander("📬 Contact pathway"):
            st.markdown(f"**Outreach approach:** {contact}")
            st.markdown(f"[Visit {domain} ↗](https://{domain})")

    def render_list(items, prefix, export_name):
        if not items:
            st.markdown('<p style="color:#444;font-size:0.82rem;padding:0.75rem 0;">No domains found in this category.</p>', unsafe_allow_html=True)
            return
        df = pd.DataFrame([{
            "Domain": d.get("domain",""), "DR": d.get("rank",0),
            "Backlinks": d.get("backlinks",0), "Spam": d.get("spam_score",0),
            "Category": d.get("category",""), "Relevance": d.get("relevance_score",""),
            "Rationale": d.get("rationale",""), "Contact": d.get("contact_hint",""),
        } for d in items])
        st.download_button(
            f"⬇ Export {len(items)} domains as CSV",
            df.to_csv(index=False).encode(), export_name, "text/csv"
        )
        st.markdown("<br>", unsafe_allow_html=True)
        for i, d in enumerate(items):
            domain_card(d, f"{prefix}_{i}")

    # ── 1. Client vs Competitors Snapshot ────────────────────────────────────

    section_header("1", "Backlink Profile — Client vs Competitors")

    def dr_rating(rank):
        if rank >= 80: return ("Excellent", "#22c55e")
        if rank >= 60: return ("Strong", "#86efac")
        if rank >= 40: return ("Good", "#ff6b2b")
        if rank >= 20: return ("Moderate", "#eab308")
        return ("Weak", "#ef4444")

    def spam_rating(score):
        if score <= 10: return ("Clean", "#22c55e")
        if score <= 30: return ("Low", "#86efac")
        if score <= 60: return ("Moderate", "#eab308")
        return ("High", "#ef4444")

    if summaries:
        client_domain = clean_domain(client["url"])
        for domain, m in summaries.items():
            is_client  = (domain == client_domain)
            label      = client["name"] if is_client else domain
            dr_val     = m["rank"]
            dr_pct     = min(dr_val, 100)
            dr_label, dr_color = dr_rating(dr_val)
            sp_label, sp_color = spam_rating(m["spam_score"])
            card_border  = "#ff6b2b" if is_client else "#1e1e1e"
            role_color   = "#ff6b2b" if is_client else "#444"
            role_text    = "✦ Client" if is_client else "Competitor"

            # Pre-compute SVG values
            r_svg = 38
            circ  = 2 * 3.14159 * r_svg
            fill  = round((dr_pct / 100) * circ, 1)
            gap   = round(circ - fill, 1)

            bl  = fmt_num(m["backlinks"])
            rd  = fmt_num(m["referring_domains"])
            sp  = str(m["spam_score"])

            html = (
                '<div style="background:#111;border:1px solid ' + card_border + ';'
                'border-radius:10px;padding:1.25rem 1.5rem;margin-bottom:1rem;">'
                '<div style="font-size:0.65rem;font-weight:700;letter-spacing:0.12em;'
                'text-transform:uppercase;color:' + role_color + ';margin-bottom:0.3rem;">' + role_text + '</div>'
                '<div style="font-size:1rem;font-weight:800;color:#fff;margin-bottom:1rem;">' + label + '</div>'
                '<div style="display:flex;align-items:center;gap:2rem;flex-wrap:wrap;">'

                # Donut
                '<div style="flex-shrink:0;text-align:center;">'
                '<svg width="110" height="110" viewBox="0 0 100 100">'
                '<circle cx="50" cy="50" r="38" fill="none" stroke="#1e1e1e" stroke-width="14"/>'
                '<circle cx="50" cy="50" r="38" fill="none" stroke="' + dr_color + '" stroke-width="14"'
                ' stroke-dasharray="' + str(fill) + ' ' + str(gap) + '"'
                ' stroke-linecap="round" transform="rotate(-90 50 50)"/>'
                '<text x="50" y="50" text-anchor="middle" dominant-baseline="central"'
                ' font-size="18" font-weight="800" fill="#fff" font-family="Inter,sans-serif">' + str(dr_val) + '</text>'
                '</svg>'
                '<div style="font-size:0.65rem;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:#555;margin-top:-0.25rem;">Domain Rating</div>'
                '<div style="font-size:0.7rem;font-weight:700;color:' + dr_color + ';margin-top:0.15rem;">' + dr_label + ' <span style="color:#444;font-weight:400">/ 100</span></div>'
                '</div>'

                # Stats grid
                '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1rem;flex:1;min-width:220px;">'
                '<div style="text-align:center;background:#0d0d0d;border-radius:8px;padding:0.75rem 0.5rem;border:1px solid #1a1a1a;">'
                '<div style="font-size:1.6rem;font-weight:800;color:#fff;line-height:1;">' + bl + '</div>'
                '<div style="font-size:0.62rem;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;color:#444;margin-top:0.3rem;">Backlinks</div>'
                '</div>'
                '<div style="text-align:center;background:#0d0d0d;border-radius:8px;padding:0.75rem 0.5rem;border:1px solid #1a1a1a;">'
                '<div style="font-size:1.6rem;font-weight:800;color:#fff;line-height:1;">' + rd + '</div>'
                '<div style="font-size:0.62rem;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;color:#444;margin-top:0.3rem;">Ref. Domains</div>'
                '</div>'
                '<div style="text-align:center;background:#0d0d0d;border-radius:8px;padding:0.75rem 0.5rem;border:1px solid #1a1a1a;">'
                '<div style="font-size:1.6rem;font-weight:800;color:' + sp_color + ';line-height:1;">' + sp + '</div>'
                '<div style="font-size:0.62rem;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;color:#444;margin-top:0.3rem;">Spam Score</div>'
                '<div style="font-size:0.6rem;color:' + sp_color + ';margin-top:0.15rem;">' + sp_label + '</div>'
                '</div>'
                '</div>'
                '</div>'
                '</div>'
            )
            st.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown('<p style="color:#444;font-size:0.83rem;padding:0.5rem 0;">Profile data unavailable — DataForSEO Backlinks API may still be activating.</p>', unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── 2. Opportunity tabs ───────────────────────────────────────────────────

    section_header("2", "Link Building Opportunities")

    cname = client["name"].lower().replace(" ","_")
    industry  = client.get("industry","")
    market    = client.get("market","")
    language  = client.get("language","")

    # Load-more state
    for key in ["show_top","show_pub","show_gp","show_bp"]:
        if key not in st.session_state:
            st.session_state[key] = 10

    # AI opportunities cache — run once per session per tab
    if "ai_opps_cache" not in st.session_state:
        st.session_state.ai_opps_cache = {}

    def get_ai_opps(tab_type):
        if tab_type not in st.session_state.ai_opps_cache:
            try:
                with st.spinner(f"AI researching {tab_type} opportunities…"):
                    data = ai_opportunities(industry, market, competitors, tab_type)
                    st.session_state.ai_opps_cache[tab_type] = data
            except Exception as e:
                st.warning(f"AI research failed: {e}")
                st.session_state.ai_opps_cache[tab_type] = []
        return st.session_state.ai_opps_cache[tab_type]

    def ai_domain_card(d, key_prefix):
        """Card for pure AI-generated opportunities (no DataForSEO metrics)."""
        domain    = d.get("domain","")
        dr_est    = d.get("dr_estimate", 0)
        rel       = d.get("relevance_score", 5)
        rationale = d.get("rationale","")
        contact   = d.get("contact_hint","Check website contact page")
        spec      = d.get("specificity","generic")
        rc        = rel_color(rel)
        rdot      = '<span class="rel-dot" style="background:' + rc + '"></span>'
        spec_badge = (
            '<span class="badge" style="background:rgba(255,107,43,0.15);color:#ff6b2b">Industry</span>'
            if spec == "industry_specific" else
            '<span class="badge" style="background:rgba(100,100,100,0.15);color:#666">Generic</span>'
        )
        html = (
            '<div class="domain-card">'
            '<div class="card-top">'
            '<div class="card-domain">' + domain + '</div>'
            '<div class="card-badges">' + spec_badge + '</div>'
            '</div>'
            '<div class="card-metrics">'
            '<div class="card-metric">DR (est.) <span>' + str(dr_est) + '</span></div>'
            '<div class="card-metric">Relevance <span class="rel-score">' + rdot + ' <span style="color:' + rc + ';font-weight:700">' + str(rel) + '/10</span></span></div>'
            '</div>'
            '<div class="card-rationale">' + rationale + '</div>'
            '</div>'
        )
        st.markdown(html, unsafe_allow_html=True)
        with st.expander("📬 Contact pathway"):
            st.markdown(f"**Outreach approach:** {contact}")
            st.markdown(f"[Visit {domain} ↗](https://{domain})")

    def render_split_cols(all_items, prefix, export_name, show_key):
        """Render items split into industry-specific (left) and generic (right) columns."""
        if not all_items:
            st.markdown('<p style="color:#444;font-size:0.82rem;padding:0.75rem 0;">No results — try running the analysis again.</p>', unsafe_allow_html=True)
            return

        industry_items = [d for d in all_items if d.get("specificity") == "industry_specific"]
        generic_items  = [d for d in all_items if d.get("specificity") != "industry_specific"]

        # Export
        df = pd.DataFrame([{
            "Domain": d.get("domain",""), "DR Estimate": d.get("dr_estimate",0),
            "Specificity": d.get("specificity",""), "Relevance": d.get("relevance_score",""),
            "Rationale": d.get("rationale",""), "Contact": d.get("contact_hint",""),
        } for d in all_items])
        st.download_button(
            f"⬇ Export all {len(all_items)} as CSV",
            df.to_csv(index=False).encode(), export_name, "text/csv", key=f"exp_{prefix}"
        )
        st.markdown("<br>", unsafe_allow_html=True)

        visible_n = st.session_state[show_key]
        col_l, col_r = st.columns(2)

        with col_l:
            st.markdown(
                '<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;'
                'color:#ff6b2b;margin-bottom:0.75rem;padding-bottom:0.4rem;border-bottom:1px solid #1e1e1e;">'
                + industry + ' — Industry Specific</div>',
                unsafe_allow_html=True
            )
            shown_l = industry_items[:visible_n]
            if shown_l:
                for i, d in enumerate(shown_l):
                    ai_domain_card(d, f"{prefix}_l_{i}")
            else:
                st.markdown('<p style="color:#444;font-size:0.78rem;">No industry-specific domains found — check generic list on the right.</p>', unsafe_allow_html=True)

        with col_r:
            st.markdown(
                '<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;'
                'color:#666;margin-bottom:0.75rem;padding-bottom:0.4rem;border-bottom:1px solid #1e1e1e;">'
                'Generic — Any Industry</div>',
                unsafe_allow_html=True
            )
            shown_r = generic_items[:visible_n]
            if shown_r:
                for i, d in enumerate(shown_r):
                    ai_domain_card(d, f"{prefix}_r_{i}")
            else:
                st.markdown('<p style="color:#444;font-size:0.78rem;">No generic domains found.</p>', unsafe_allow_html=True)

        # Load more based on whichever list is longer
        remaining = max(len(industry_items), len(generic_items)) - visible_n
        if remaining > 0:
            if st.button(f"Load {min(remaining, 10)} more ({remaining} remaining)", key=f"more_{prefix}"):
                st.session_state[show_key] += 10
                st.rerun()

    def render_bp(all_items, prefix, export_name, show_key):
        """Backlink providers — single list, no split needed (all generic)."""
        if not all_items:
            st.markdown('<p style="color:#444;font-size:0.82rem;padding:0.75rem 0;">No results.</p>', unsafe_allow_html=True)
            return

        services   = [d for d in all_items if d.get("specificity") == "industry_specific"]
        directories = [d for d in all_items if d.get("specificity") != "industry_specific"]

        df = pd.DataFrame([{
            "Domain": d.get("domain",""), "Relevance": d.get("relevance_score",""),
            "Rationale": d.get("rationale",""), "Contact": d.get("contact_hint",""),
        } for d in all_items])
        st.download_button(f"⬇ Export all {len(all_items)} as CSV", df.to_csv(index=False).encode(), export_name, "text/csv", key=f"exp_{prefix}")
        st.markdown("<br>", unsafe_allow_html=True)

        col_l, col_r = st.columns(2)
        visible_n = st.session_state[show_key]

        with col_l:
            st.markdown(
                '<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;'
                'color:#ff6b2b;margin-bottom:0.75rem;padding-bottom:0.4rem;border-bottom:1px solid #1e1e1e;">'
                'Backlink Services</div>',
                unsafe_allow_html=True
            )
            for i, d in enumerate(services[:visible_n]):
                ai_domain_card(d, f"{prefix}_s_{i}")
            if not services:
                st.markdown('<p style="color:#444;font-size:0.78rem;">No services found.</p>', unsafe_allow_html=True)

        with col_r:
            st.markdown(
                '<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;'
                'color:#666;margin-bottom:0.75rem;padding-bottom:0.4rem;border-bottom:1px solid #1e1e1e;">'
                'Directories & Forums</div>',
                unsafe_allow_html=True
            )
            for i, d in enumerate(directories[:visible_n]):
                ai_domain_card(d, f"{prefix}_d_{i}")
            if not directories:
                st.markdown('<p style="color:#444;font-size:0.78rem;">No directories found.</p>', unsafe_allow_html=True)

        remaining = max(len(services), len(directories)) - visible_n
        if remaining > 0:
            if st.button(f"Load {min(remaining,10)} more ({remaining} remaining)", key=f"more_{prefix}"):
                st.session_state[show_key] += 10
                st.rerun()

    tab_top, tab_pub, tab_gp, tab_bp = st.tabs([
        "⭐ Top Opportunities",
        "Publishers",
        "Guest Posting",
        "Backlink Providers",
    ])

    with tab_top:
        st.markdown('<p style="color:#555;font-size:0.78rem;margin-bottom:1rem;">The highest-impact domains for link building in your industry and market — influenced by your competitor profiles.</p>', unsafe_allow_html=True)
        data = get_ai_opps("top")
        render_split_cols(data, "top", f"top_opportunities_{cname}.csv", "show_top")

    with tab_pub:
        st.markdown('<p style="color:#555;font-size:0.78rem;margin-bottom:1rem;">Media outlets, news sites, trade publications and high-authority editorial platforms — industry-specific on the left, major generic publishers on the right.</p>', unsafe_allow_html=True)
        data = get_ai_opps("publishers")
        render_split_cols(data, "pub", f"publishers_{cname}.csv", "show_pub")

    with tab_gp:
        st.markdown('<p style="color:#555;font-size:0.78rem;margin-bottom:1rem;">Domains with active guest posting or contributor programs — where you can publish an article and link back to your website.</p>', unsafe_allow_html=True)
        data = get_ai_opps("guest_posting")
        render_split_cols(data, "gp", f"guest_posting_{cname}.csv", "show_gp")

    with tab_bp:
        st.markdown('<p style="color:#555;font-size:0.78rem;margin-bottom:1rem;">Platforms and services that provide backlinks — left column shows known backlink services (FatJoe, Adsy, etc.), right shows directories and forum placements relevant to your market.</p>', unsafe_allow_html=True)
        data = get_ai_opps("backlink_providers")
        render_bp(data, "bp", f"backlink_providers_{cname}.csv", "show_bp")

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── 3. Competitive Intelligence ───────────────────────────────────────────

    section_header("3", "Competitive Intelligence")

    # Load-more state for competitive tabs
    for key, default in [
        ("show_cs", 10), ("show_ci", 10), ("show_mo", 10),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    # Build signals from enriched or raw fallback
    source_pool = enriched if enriched else [
        {**d, "category": "free", "rationale": "", "contact_hint": "Check website contact page",
         "relevance_score": 5, "is_top_influential": False}
        for d in raw_domains
    ]

    # Missed opportunities: intersection domains first, fall back to top referring if empty
    missed_raw = [d for d in source_pool if d.get("source") == "intersection"]
    if not missed_raw:
        # Fallback: top referring domains from competitors = domains client is missing
        missed_raw = sorted(
            [d for d in source_pool if d.get("source") == "referring"],
            key=lambda x: x.get("rank", 0), reverse=True
        )[:30]
    missed_all = [{**d, "is_missed": True} for d in missed_raw]

    top_comp_sources_all = sorted(
        [d for d in source_pool if d.get("source") == "referring"],
        key=lambda x: x.get("rank", 0), reverse=True
    )

    intersection_all = sorted(
        [d for d in source_pool if d.get("source") == "intersection"],
        key=lambda x: x.get("rank", 0), reverse=True
    )

    # Unique per competitor — group raw_domains by competitor
    competitor_list = list(dict.fromkeys(
        d.get("competitor","") for d in raw_domains if d.get("source") == "referring" and d.get("competitor")
    ))

    def render_with_loadmore_ci(all_items, prefix, export_name, show_key):
        if not all_items:
            st.markdown('<p style="color:#444;font-size:0.82rem;padding:0.75rem 0;">No domains found.</p>', unsafe_allow_html=True)
            return
        visible = all_items[:st.session_state[show_key]]
        df = pd.DataFrame([{
            "Domain": d.get("domain",""), "DR": d.get("rank",0),
            "Backlinks": d.get("backlinks",0), "Spam": d.get("spam_score",0),
            "Rationale": d.get("rationale",""), "Contact": d.get("contact_hint",""),
        } for d in all_items])
        st.download_button(f"⬇ Export all {len(all_items)} as CSV", df.to_csv(index=False).encode(), export_name, "text/csv", key=f"exp_{prefix}")
        st.markdown("<br>", unsafe_allow_html=True)
        for i, d in enumerate(visible):
            domain_card(d, f"{prefix}_{i}")
        remaining = len(all_items) - len(visible)
        if remaining > 0:
            if st.button(f"Load {min(remaining, 10)} more ({remaining} remaining)", key=f"more_{prefix}"):
                st.session_state[show_key] += 10
                st.rerun()

    ci1, ci2, ci3, ci4 = st.tabs([
        f"Top Competitor Sources ({len(top_comp_sources_all)})",
        f"Domain Intersection ({len(intersection_all)})",
        "Unique Domains per Competitor",
        f"Missed Opportunities ({len(missed_all)})",
    ])

    with ci1:
        st.markdown('<p style="color:#555;font-size:0.78rem;margin-bottom:1rem;">Highest authority domains currently linking to your competitors — where you need to be.</p>', unsafe_allow_html=True)
        render_with_loadmore_ci(top_comp_sources_all, "cs", f"competitor_sources_{cname}.csv", "show_cs")

    with ci2:
        st.markdown('<p style="color:#555;font-size:0.78rem;margin-bottom:1rem;">Domains linking to multiple competitors simultaneously — proven industry linkers, highest priority targets.</p>', unsafe_allow_html=True)
        render_with_loadmore_ci(intersection_all, "ci", f"intersection_{cname}.csv", "show_ci")

    with ci3:
        st.markdown('<p style="color:#555;font-size:0.78rem;margin-bottom:1rem;">High-influence domains linking to each competitor but NOT to your client — split by competitor so you know exactly whose link sources to target first.</p>', unsafe_allow_html=True)
        if not competitor_list:
            st.markdown('<p style="color:#444;font-size:0.82rem;padding:0.75rem 0;">No competitor data available.</p>', unsafe_allow_html=True)
        else:
            for comp in competitor_list:
                comp_domains_raw = [d for d in raw_domains if d.get("competitor") == comp and d.get("source") == "referring"]
                # Enrich with AI data where available, else use raw
                enriched_map = {d.get("domain"): d for d in source_pool}
                comp_domains = []
                for d in sorted(comp_domains_raw, key=lambda x: x.get("rank",0), reverse=True):
                    enriched_d = enriched_map.get(d["domain"], d)
                    comp_domains.append({**enriched_d, "is_unique": True})

                show_key = f"show_unique_{comp.replace('.','_')}"
                if show_key not in st.session_state:
                    st.session_state[show_key] = 10

                st.markdown(f"""
                <div style="background:#111;border:1px solid #1e1e1e;border-left:3px solid #ff6b2b;
                border-radius:8px;padding:0.75rem 1rem;margin:1rem 0 0.75rem;">
                    <div style="font-size:0.7rem;font-weight:700;letter-spacing:0.1em;
                    text-transform:uppercase;color:#ff6b2b;margin-bottom:0.15rem;">Competitor</div>
                    <div style="font-size:0.95rem;font-weight:700;color:#fff;">{comp}</div>
                    <div style="font-size:0.72rem;color:#555;margin-top:0.2rem;">{len(comp_domains)} unique referring domains</div>
                </div>""", unsafe_allow_html=True)

                if not comp_domains:
                    st.markdown('<p style="color:#444;font-size:0.82rem;padding:0.5rem 0 1rem;">No unique domains found for this competitor.</p>', unsafe_allow_html=True)
                    continue

                visible = comp_domains[:st.session_state[show_key]]
                for i, d in enumerate(visible):
                    domain_card(d, f"unique_{comp.replace('.','_')}_{i}")

                remaining = len(comp_domains) - len(visible)
                if remaining > 0:
                    if st.button(f"Load {min(remaining,10)} more for {comp} ({remaining} remaining)", key=f"more_unique_{comp.replace('.','_')}"):
                        st.session_state[show_key] += 10
                        st.rerun()

                df_comp = pd.DataFrame([{
                    "Domain": d.get("domain",""), "DR": d.get("rank",0),
                    "Backlinks": d.get("backlinks",0), "Spam": d.get("spam_score",0),
                } for d in comp_domains])
                st.download_button(
                    f"⬇ Export {comp} domains",
                    df_comp.to_csv(index=False).encode(),
                    f"unique_{comp.replace('.','_')}_{cname}.csv",
                    "text/csv",
                    key=f"exp_unique_{comp.replace('.','_')}"
                )
                st.markdown("<br>", unsafe_allow_html=True)

    with ci4:
        st.markdown('<p style="color:#555;font-size:0.78rem;margin-bottom:1rem;">Domains your competitors have secured but your client is missing — close these gaps first.</p>', unsafe_allow_html=True)
        render_with_loadmore_ci(missed_all, "mo", f"missed_opportunities_{cname}.csv", "show_mo")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE — CONTENT GENERATION
# ══════════════════════════════════════════════════════════════════════════════

elif st.session_state.page == "content":

    client   = st.session_state.client
    enriched = st.session_state.enriched

    if st.session_state.get("summaries") or st.session_state.get("enriched"):
        if st.button("← Back to Intelligence Dashboard", key="content_to_dash"):
            st.session_state.page = "dashboard"
            st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)

    section_header("1", "Content Brief")

    # Target domain — use top influential from analysis if available, else fall back to client URL
    top_domains   = [d["domain"] for d in enriched if d.get("is_top_influential")][:10]
    all_domains   = [d["domain"] for d in enriched][:20]
    default_domain = top_domains[0] if top_domains else (all_domains[0] if all_domains else clean_domain(client.get("url","")))

    if top_domains or all_domains:
        target_options = top_domains if top_domains else all_domains
        target_domain  = st.selectbox("Target Domain", target_options,
                                       help="Domains from your backlink analysis — select the one you're writing for.")
    else:
        target_domain = clean_domain(client.get("url", ""))
        st.markdown(f'<div style="background:#141414;border:1px solid #242424;border-radius:6px;padding:0.6rem 0.9rem;font-size:0.82rem;color:#888;margin-bottom:0.75rem;">Target Domain &nbsp;<span style="color:#fff;font-weight:600">{target_domain}</span> &nbsp;<span style="color:#444;font-size:0.7rem">(run a backlink analysis to unlock domain-specific targeting)</span></div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        topic       = st.text_input("Article Topic", placeholder="e.g. The future of sustainable real estate in the UAE")
        tone        = st.selectbox("Tone of Voice", [
            "Authoritative & Expert","Conversational & Friendly",
            "Thought Leadership","Educational & Informative","Journalistic","Persuasive"
        ])
        content_lang = st.selectbox("Content Language", ["English", "Arabic", "French"])
        primary_kw  = st.text_input("Primary Keyword", placeholder="e.g. luxury real estate Dubai")
        brand_terms = st.text_input("Brand Terms", placeholder="e.g. Sobha Realty, Sobha Hartland")
    with c2:
        length         = st.number_input("Word Count", min_value=300, max_value=3000, value=800, step=100)
        target_prompts = st.text_area("AI Prompts / Questions to Target", height=104,
                                       placeholder="e.g. What is the best real estate developer in Dubai?\nWhy invest in Dubai property in 2025?")
        secondary_kws  = st.text_input("Secondary Keywords", placeholder="e.g. Dubai property investment, off-plan real estate UAE")

    st.markdown("<br>", unsafe_allow_html=True)
    gen = st.button("✦  Generate Content", use_container_width=True)

    if gen:
        if not topic or not primary_kw:
            st.error("Topic and primary keyword are required.")
        else:
            with st.spinner("Generating content…"):
                try:
                    content = ai_generate_content(
                        topic, length, tone, content_lang, brand_terms,
                        target_prompts, primary_kw, secondary_kws,
                        client.get("name",""), client.get("industry",""),
                        client.get("url","")
                    )
                    st.session_state.generated_content = content
                except Exception as e:
                    st.error(f"Content generation failed: {e}")

    if st.session_state.get("generated_content"):
        st.markdown("<hr>", unsafe_allow_html=True)
        section_header("2", "Generated Content — Review Before Use")
        st.markdown('<div class="exd-alert">⚠ AI-generated. Must be reviewed and edited by your team before outreach or publication.</div>', unsafe_allow_html=True)

        edited = st.text_area(
            "Edit content",
            value=st.session_state.generated_content,
            height=600,
            label_visibility="collapsed"
        )

        # ── Word document export ──────────────────────────────────────────────
        def build_docx(markdown_text, title, client_name):
            from docx import Document as DocxDocument
            from docx.shared import Pt, RGBColor, Inches
            from docx.enum.text import WD_ALIGN_PARAGRAPH
            import re, io

            doc = DocxDocument()

            # Page margins
            for section in doc.sections:
                section.top_margin    = Inches(1)
                section.bottom_margin = Inches(1)
                section.left_margin   = Inches(1.2)
                section.right_margin  = Inches(1.2)

            # Styles
            style = doc.styles["Normal"]
            style.font.name = "Arial"
            style.font.size = Pt(11)

            # Title
            title_para = doc.add_paragraph()
            title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = title_para.add_run(title or client_name)
            run.bold = True
            run.font.size = Pt(20)
            run.font.color.rgb = RGBColor(0xFF, 0x6B, 0x2B)
            doc.add_paragraph()

            def add_styled_run(para, text, bold=False, is_heading=False):
                run = para.add_run(text)
                run.bold = bold or is_heading
                if is_heading:
                    run.font.size = Pt(13) if para.style.name.startswith("Heading 2") else Pt(12)
                return run

            def parse_inline(para, text, force_bold=False):
                """Parse **bold** markers and add runs accordingly."""
                pattern = re.compile(r"\*\*(.+?)\*\*")
                last = 0
                for m in pattern.finditer(text):
                    before = text[last:m.start()]
                    if before:
                        r = para.add_run(before)
                        r.bold = force_bold
                    bold_run = para.add_run(m.group(1))
                    bold_run.bold = True
                    last = m.end()
                remainder = text[last:]
                if remainder:
                    r = para.add_run(remainder)
                    r.bold = force_bold

            lines = markdown_text.split("\n")
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    doc.add_paragraph()
                    continue

                if stripped.startswith("### "):
                    heading_text = stripped[4:].replace("**","")
                    p = doc.add_heading(level=3)
                    r = p.add_run(heading_text)
                    r.bold = True
                    r.font.size = Pt(12)
                elif stripped.startswith("## "):
                    heading_text = stripped[3:].replace("**","")
                    p = doc.add_heading(level=2)
                    r = p.add_run(heading_text)
                    r.bold = True
                    r.font.size = Pt(13)
                elif stripped.startswith("# "):
                    heading_text = stripped[2:].replace("**","")
                    p = doc.add_heading(level=1)
                    r = p.add_run(heading_text)
                    r.bold = True
                    r.font.size = Pt(16)
                elif stripped.startswith("- ") or stripped.startswith("* "):
                    p = doc.add_paragraph(style="List Bullet")
                    parse_inline(p, stripped[2:])
                elif re.match(r"^\d+\. ", stripped):
                    p = doc.add_paragraph(style="List Number")
                    parse_inline(p, re.sub(r"^\d+\. ", "", stripped))
                elif stripped.startswith("[") and "→" in stripped:
                    # Internal link suggestion line
                    p = doc.add_paragraph()
                    p.paragraph_format.left_indent = Inches(0.3)
                    parse_inline(p, stripped)
                else:
                    p = doc.add_paragraph()
                    parse_inline(p, stripped)

                # Body text spacing
                if hasattr(p, "paragraph_format"):
                    p.paragraph_format.space_after = Pt(6)

            buf = io.BytesIO()
            doc.save(buf)
            buf.seek(0)
            return buf.getvalue()

        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            try:
                article_title = edited.split("\n")[0].replace("#","").replace("*","").strip()
                docx_bytes = build_docx(edited, article_title, client.get("name","Article"))
                fname_docx = f"content_{client.get('name','article').lower().replace(' ','_')}_{datetime.now().strftime('%Y%m%d')}.docx"
                st.download_button(
                    "⬇ Download Word (.docx)",
                    data=docx_bytes,
                    file_name=fname_docx,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
            except Exception as e:
                fname_txt = f"content_{datetime.now().strftime('%Y%m%d')}.txt"
                st.download_button("⬇ Download .txt", edited.encode(), fname_txt, "text/plain", use_container_width=True)
                st.caption(f"Word export unavailable: {e}")
        with c2:
            fname_txt = f"content_{datetime.now().strftime('%Y%m%d')}.txt"
            st.download_button("⬇ Download .txt", edited.encode(), fname_txt, "text/plain", use_container_width=True)
        with c3:
            st.markdown(f'<div style="text-align:center;color:#444;font-size:0.77rem;padding:0.65rem;">{len(edited.split()):,} words</div>', unsafe_allow_html=True)
