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
    return genai.GenerativeModel("gemini-2.0-flash")

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

Category rules:
- free: guest posts, editorial submissions, community contributions at no cost
- paid: sponsored content, paid placements, native ads, advertorial
- publisher: major media, news outlets, trade publications, industry press
- blog: independent blogs, niche content sites, influencer blogs

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

def ai_generate_content(topic, length, tone, brand_terms, target_prompts, primary_kw, secondary_kws, client_name, industry):
    model  = get_gemini()
    prompt = f"""You are a senior content strategist writing for {client_name} in {industry}.

Write a guest post / outreach article with these specifications:
- Topic: {topic}
- Word count: {length} words
- Tone: {tone}
- Brand terms (use naturally): {brand_terms}
- AI prompts / questions to target: {target_prompts}
- Primary keyword: {primary_kw}
- Secondary keywords: {secondary_kws}

Requirements:
- Full structured article with H2/H3 headings (use markdown)
- Primary keyword in title, first paragraph, and at least 2 subheadings
- Secondary keywords woven naturally throughout
- Brand terms authentic, not forced
- Non-salesy conclusion
- Do NOT include byline, author bio, or meta description

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
    c1, c2, c3 = st.columns([1, 1, 3])
    with c1:
        if st.button("① Intelligence Dashboard", key="nav_dash"):
            st.session_state.page = "dashboard"
            st.rerun()
    with c2:
        if st.button("② Content Generation", key="nav_content"):
            st.session_state.page = "content"
            st.rerun()
    with c3:
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

    if summaries:
        client_domain = clean_domain(client["url"])
        cols          = st.columns(len(summaries))
        for i, (domain, m) in enumerate(summaries.items()):
            is_client = (domain == client_domain)
            with cols[i]:
                st.markdown(f"""
                <div class="stat-card {'client' if is_client else 'competitor'}">
                    <div class="stat-label">{'✦ Client' if is_client else 'Competitor'}</div>
                    <div class="stat-domain" title="{domain}">{''+client['name'] if is_client else domain}</div>
                    <div class="stat-metric">
                        <span class="stat-metric-label">Domain Rating</span>
                        <span class="stat-metric-value {'hi' if is_client else ''}">{m['rank']}</span>
                    </div>
                    {dr_bar_html(m['rank'])}
                    <div class="stat-metric">
                        <span class="stat-metric-label">Total Backlinks</span>
                        <span class="stat-metric-value">{fmt_num(m['backlinks'])}</span>
                    </div>
                    <div class="stat-metric">
                        <span class="stat-metric-label">Referring Domains</span>
                        <span class="stat-metric-value">{fmt_num(m['referring_domains'])}</span>
                    </div>
                    <div class="stat-metric">
                        <span class="stat-metric-label">Spam Score</span>
                        <span class="stat-metric-value">{m['spam_score']}</span>
                    </div>
                </div>""", unsafe_allow_html=True)
    else:
        st.markdown('<p style="color:#444;font-size:0.83rem;padding:0.5rem 0;">Profile data unavailable — DataForSEO Backlinks API may still be activating.</p>', unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── 2. Opportunity tabs ───────────────────────────────────────────────────

    section_header("2", "Link Building Opportunities")

    def get_cat(cat, n=10):
        return [d for d in enriched if d.get("category") == cat][:n]

    top10        = [d for d in enriched if d.get("is_top_influential")][:10]
    free_list    = get_cat("free")
    paid_list    = get_cat("paid")
    pub_list     = get_cat("publisher")
    blog_list    = get_cat("blog")

    tab_top, tab_free, tab_paid, tab_pub, tab_blog = st.tabs([
        "⭐ Top 10 Influential",
        "Free Opportunities",
        "Paid Placements",
        "Publishers",
        "Blogs",
    ])

    cname = client['name'].lower().replace(' ','_')

    with tab_top:
        st.markdown('<p style="color:#555;font-size:0.78rem;margin-bottom:1rem;">The 10 most impactful domains for your industry and market — ranked by AI relevance score, regardless of category.</p>', unsafe_allow_html=True)
        render_list(top10, "top", f"top_influential_{cname}.csv")

    with tab_free:
        st.markdown('<p style="color:#555;font-size:0.78rem;margin-bottom:1rem;">Domains accepting guest posts, editorial contributions or community submissions at no cost.</p>', unsafe_allow_html=True)
        render_list(free_list, "free", f"free_opportunities_{cname}.csv")

    with tab_paid:
        st.markdown('<p style="color:#555;font-size:0.78rem;margin-bottom:1rem;">Domains offering sponsored content, paid placements or native advertising opportunities.</p>', unsafe_allow_html=True)
        render_list(paid_list, "paid", f"paid_placements_{cname}.csv")

    with tab_pub:
        st.markdown('<p style="color:#555;font-size:0.78rem;margin-bottom:1rem;">Major media outlets, trade publications and industry press relevant to your space.</p>', unsafe_allow_html=True)
        render_list(pub_list, "pub", f"publishers_{cname}.csv")

    with tab_blog:
        st.markdown('<p style="color:#555;font-size:0.78rem;margin-bottom:1rem;">Independent blogs and niche content sites with engaged audiences in your industry.</p>', unsafe_allow_html=True)
        render_list(blog_list, "blog", f"blogs_{cname}.csv")

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── 3. Competitive Intelligence ───────────────────────────────────────────

    section_header("3", "Competitive Intelligence")

    # Build signals
    missed_domains = [
        {**d, "is_missed": True}
        for d in enriched if d.get("source") == "intersection"
    ][:10]

    top_comp_sources = sorted(
        [d for d in enriched if d.get("source") == "referring"],
        key=lambda x: x.get("rank", 0), reverse=True
    )[:10]

    intersection_domains = [d for d in enriched if d.get("source") == "intersection"][:10]

    # Unique: appears only once across competitor referring domains
    competitor_domain_freq = Counter(
        d.get("domain") for d in raw_domains if d.get("source") == "referring"
    )
    unique_domains = [
        {**d, "is_unique": True}
        for d in enriched
        if d.get("source") == "referring" and competitor_domain_freq.get(d.get("domain",""), 0) == 1
    ][:10]

    ci1, ci2, ci3, ci4 = st.tabs([
        "Top Competitor Sources",
        "Domain Intersection",
        "Unique Domains",
        "Missed Opportunities",
    ])

    with ci1:
        st.markdown('<p style="color:#555;font-size:0.78rem;margin-bottom:1rem;">Highest authority domains currently linking to your competitors — where you need to be.</p>', unsafe_allow_html=True)
        render_list(top_comp_sources, "cs", f"competitor_sources_{cname}.csv")

    with ci2:
        st.markdown('<p style="color:#555;font-size:0.78rem;margin-bottom:1rem;">Domains linking to multiple competitors simultaneously — proven industry linkers, highest priority targets.</p>', unsafe_allow_html=True)
        render_list(intersection_domains, "ci", f"intersection_{cname}.csv")

    with ci3:
        st.markdown('<p style="color:#555;font-size:0.78rem;margin-bottom:1rem;">Domains linking to only one competitor — less contested, easier to win with targeted outreach.</p>', unsafe_allow_html=True)
        render_list(unique_domains, "ud", f"unique_domains_{cname}.csv")

    with ci4:
        st.markdown('<p style="color:#555;font-size:0.78rem;margin-bottom:1rem;">Domains your competitors have secured but your client is missing entirely — close these gaps first.</p>', unsafe_allow_html=True)
        render_list(missed_domains, "mo", f"missed_opportunities_{cname}.csv")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE — CONTENT GENERATION
# ══════════════════════════════════════════════════════════════════════════════

elif st.session_state.page == "content":

    client   = st.session_state.client
    enriched = st.session_state.enriched

    section_header("1", "Content Brief")

    top_domains    = [d["domain"] for d in enriched if d.get("is_top_influential")][:10]
    all_domains    = [d["domain"] for d in enriched][:20]
    target_options = ["— No specific target —"] + (top_domains if top_domains else all_domains)
    target_domain  = st.selectbox("Target Domain", target_options,
                                   help="Select a domain from the intelligence dashboard to tailor the content for that publisher.")

    c1, c2 = st.columns(2)
    with c1:
        topic       = st.text_input("Article Topic", placeholder="e.g. The future of sustainable real estate in the UAE")
        tone        = st.selectbox("Tone of Voice", [
            "Authoritative & Expert","Conversational & Friendly",
            "Thought Leadership","Educational & Informative","Journalistic","Persuasive"
        ])
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
                        topic, length, tone, brand_terms,
                        target_prompts, primary_kw, secondary_kws,
                        client.get("name",""), client.get("industry","")
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

        c1, c2 = st.columns(2)
        with c1:
            fname = f"content_{primary_kw.lower().replace(' ','_') if 'primary_kw' in dir() else 'article'}_{datetime.now().strftime('%Y%m%d')}.txt"
            st.download_button("⬇ Download .txt", edited.encode(), fname, "text/plain", use_container_width=True)
        with c2:
            st.markdown(f'<div style="text-align:center;color:#444;font-size:0.77rem;padding:0.65rem;">{len(edited.split()):,} words</div>', unsafe_allow_html=True)
