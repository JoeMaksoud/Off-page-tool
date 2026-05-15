import streamlit as st
import requests
import json
import base64
import pandas as pd
import google.generativeai as genai
from datetime import datetime
import time

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="EXD Backlink Intelligence",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Design system (EXD standard) ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* Reset & base */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background-color: #0e0e0e !important;
    color: #f0f0f0 !important;
    font-family: 'Inter', sans-serif !important;
}

[data-testid="stAppViewContainer"] > .main {
    background-color: #0e0e0e !important;
}

.main .block-container {
    max-width: 860px !important;
    margin: 0 auto !important;
    padding: 2.5rem 1.5rem 4rem !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header, [data-testid="stToolbar"] { display: none !important; }
[data-testid="stSidebar"] { display: none !important; }

/* Typography */
h1, h2, h3, h4 { font-family: 'Inter', sans-serif !important; }

/* ── Header ── */
.exd-header {
    text-align: center;
    margin-bottom: 3rem;
    padding-bottom: 2rem;
    border-bottom: 1px solid #1e1e1e;
}
.exd-wordmark {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.25em;
    color: #ff6b2b;
    text-transform: uppercase;
    margin-bottom: 0.75rem;
}
.exd-title {
    font-size: 2rem;
    font-weight: 800;
    color: #ffffff;
    line-height: 1.2;
    margin-bottom: 0.5rem;
}
.exd-subtitle {
    font-size: 0.875rem;
    color: #666;
    font-weight: 400;
}

/* ── Section label ── */
.section-label {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1.25rem;
    margin-top: 2rem;
}
.section-number {
    width: 28px;
    height: 28px;
    background: #ff6b2b;
    color: #fff;
    font-size: 12px;
    font-weight: 700;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}
.section-title {
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #aaa;
}

/* ── Input styling ── */
[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] select,
[data-testid="stTextArea"] textarea {
    background: #161616 !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 6px !important;
    color: #f0f0f0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: #ff6b2b !important;
    box-shadow: 0 0 0 2px rgba(255,107,43,0.15) !important;
}
label, [data-testid="stWidgetLabel"] p {
    color: #999 !important;
    font-size: 0.775rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    font-family: 'Inter', sans-serif !important;
}

/* ── Primary button ── */
.stButton > button {
    background: #ff6b2b !important;
    color: #fff !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    padding: 0.6rem 1.5rem !important;
    cursor: pointer !important;
    transition: all 0.15s ease !important;
}
.stButton > button:hover {
    background: #e55a1f !important;
    transform: translateY(-1px) !important;
}

/* ── Cards ── */
.domain-card {
    background: #141414;
    border: 1px solid #222;
    border-radius: 8px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 0.75rem;
    transition: border-color 0.2s ease;
}
.domain-card:hover { border-color: #333; }
.domain-card.approved { border-left: 3px solid #22c55e; }
.domain-card.rejected { border-left: 3px solid #ef4444; opacity: 0.5; }
.domain-card.pending  { border-left: 3px solid #ff6b2b; }

.card-domain {
    font-size: 1rem;
    font-weight: 700;
    color: #fff;
    margin-bottom: 0.35rem;
}
.card-meta {
    display: flex;
    gap: 1.25rem;
    margin-bottom: 0.6rem;
    flex-wrap: wrap;
}
.card-metric {
    font-size: 0.75rem;
    color: #666;
}
.card-metric span {
    color: #ff6b2b;
    font-weight: 600;
}
.card-rationale {
    font-size: 0.8rem;
    color: #888;
    line-height: 1.5;
    margin-bottom: 0.75rem;
    font-style: italic;
}
.card-contact {
    font-size: 0.775rem;
    color: #555;
    background: #0e0e0e;
    border-radius: 4px;
    padding: 0.4rem 0.6rem;
    border: 1px solid #1e1e1e;
    margin-bottom: 0.75rem;
}
.card-contact a { color: #ff6b2b; text-decoration: none; }

.badge {
    display: inline-block;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 0.2rem 0.5rem;
    border-radius: 3px;
    margin-right: 0.4rem;
}
.badge-free      { background: rgba(34,197,94,0.12);  color: #22c55e; }
.badge-paid      { background: rgba(234,179,8,0.12);  color: #eab308; }
.badge-publisher { background: rgba(139,92,246,0.12); color: #8b5cf6; }
.badge-blog      { background: rgba(59,130,246,0.12); color: #3b82f6; }

/* ── Tabs ── */
[data-testid="stTabs"] [role="tablist"] {
    background: #141414 !important;
    border-radius: 8px !important;
    padding: 0.25rem !important;
    border: 1px solid #1e1e1e !important;
    gap: 0.25rem !important;
}
[data-testid="stTabs"] button[role="tab"] {
    background: transparent !important;
    color: #666 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.775rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    border-radius: 6px !important;
    border: none !important;
}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    background: #ff6b2b !important;
    color: #fff !important;
}

/* ── Status bar ── */
.status-bar {
    background: #141414;
    border: 1px solid #1e1e1e;
    border-radius: 8px;
    padding: 1rem 1.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
    gap: 0.75rem;
}
.status-item { text-align: center; }
.status-value {
    font-size: 1.4rem;
    font-weight: 800;
    color: #ff6b2b;
}
.status-label {
    font-size: 0.65rem;
    color: #555;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

/* ── Divider ── */
.exd-divider {
    border: none;
    border-top: 1px solid #1a1a1a;
    margin: 2rem 0;
}

/* ── Alert ── */
.exd-alert {
    background: rgba(255,107,43,0.08);
    border: 1px solid rgba(255,107,43,0.2);
    border-radius: 6px;
    padding: 0.75rem 1rem;
    font-size: 0.8rem;
    color: #ff6b2b;
    margin-bottom: 1rem;
}

/* ── Summary box ── */
.summary-box {
    background: #141414;
    border: 1px solid #1e1e1e;
    border-radius: 8px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
}
.summary-box-title {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #555;
    margin-bottom: 0.5rem;
}
.summary-domain {
    font-size: 0.9rem;
    font-weight: 700;
    color: #fff;
}
.summary-metrics {
    display: flex;
    gap: 1.5rem;
    margin-top: 0.5rem;
    flex-wrap: wrap;
}
.summary-metric {
    font-size: 0.75rem;
    color: #666;
}
.summary-metric span { color: #ccc; font-weight: 600; }

/* Selectbox dropdown */
[data-testid="stSelectbox"] > div > div {
    background: #161616 !important;
    border: 1px solid #2a2a2a !important;
    color: #f0f0f0 !important;
}

/* Number input */
[data-testid="stNumberInput"] input {
    background: #161616 !important;
    border: 1px solid #2a2a2a !important;
    color: #f0f0f0 !important;
}

/* Spinner */
[data-testid="stSpinner"] { color: #ff6b2b !important; }

/* Success/error messages */
[data-testid="stSuccess"] { background: rgba(34,197,94,0.08) !important; border-color: #22c55e !important; }
[data-testid="stError"]   { background: rgba(239,68,68,0.08) !important; border-color: #ef4444 !important; }

hr { border-color: #1a1a1a !important; }
</style>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────

def get_dfs_creds():
    login    = st.secrets.get("DATAFORSEO_BACKLINK_LOGIN", st.secrets.get("DATAFORSEO_LOGIN", ""))
    password = st.secrets.get("DATAFORSEO_BACKLINK_PASSWORD", st.secrets.get("DATAFORSEO_PASSWORD", ""))
    token    = base64.b64encode(f"{login}:{password}".encode()).decode()
    return {"Authorization": f"Basic {token}", "Content-Type": "application/json"}

def get_gemini():
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    return genai.GenerativeModel("gemini-2.0-flash")

def dfs_post(endpoint, payload):
    url  = f"https://api.dataforseo.com/v3/{endpoint}"
    resp = requests.post(url, headers=get_dfs_creds(), json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    if data.get("status_code") != 20000:
        raise ValueError(f"DataForSEO error: {data.get('status_message')}")
    return data

def clean_domain(url):
    """Strip protocol and www from a URL for DataForSEO."""
    url = url.strip().lower()
    for prefix in ["https://www.", "http://www.", "https://", "http://", "www."]:
        if url.startswith(prefix):
            url = url[len(prefix):]
    return url.rstrip("/")

def spam_color(score):
    if score < 20:  return "#22c55e"
    if score < 50:  return "#eab308"
    return "#ef4444"

# ── DataForSEO calls ──────────────────────────────────────────────────────────

def fetch_backlink_summary(domains: list[str]) -> dict:
    """Backlink summary for client + competitors."""
    payload = [{"target": clean_domain(d), "include_subdomains": True} for d in domains]
    data    = dfs_post("backlinks/summary/live", payload)
    results = {}
    for task in data.get("tasks", []):
        if task.get("result"):
            r = task["result"][0]
            results[r["target"]] = {
                "rank":              r.get("rank", 0),
                "backlinks":         r.get("backlinks", 0),
                "referring_domains": r.get("referring_domains", 0),
                "spam_score":        r.get("backlinks_spam_score", 0),
            }
    return results

def fetch_domain_intersection(competitor_domains: list[str], exclude_domain: str) -> list[dict]:
    """Domains linking to competitors but NOT to client."""
    targets = {str(i+1): clean_domain(d) for i, d in enumerate(competitor_domains)}
    payload = [{
        "targets":                  targets,
        "exclude_targets":          [clean_domain(exclude_domain)],
        "limit":                    50,
        "order_by":                 ["1.rank,desc"],
        "exclude_internal_backlinks": True,
        "backlinks_filters":        ["dofollow", "=", True],
        "filters":                  ["backlinks_spam_score", "<", 40],
    }]
    data  = dfs_post("backlinks/domain_intersection/live", payload)
    items = []
    for task in data.get("tasks", []):
        if task.get("result"):
            for r in task["result"]:
                for item in r.get("items", []):
                    # grab data from first target's perspective
                    target_data = item.get("domain_intersection", {})
                    first       = target_data.get("1", {})
                    items.append({
                        "domain":       first.get("target", ""),
                        "rank":         first.get("rank", 0),
                        "backlinks":    first.get("backlinks", 0),
                        "spam_score":   first.get("backlinks_spam_score", 0),
                        "first_seen":   first.get("first_seen", ""),
                        "is_new":       first.get("is_new", False),
                        "source":       "domain_intersection",
                    })
    return items

def fetch_referring_domains(competitor_domain: str, limit: int = 30) -> list[dict]:
    """High-authority referring domains for a competitor."""
    payload = [{
        "target":                     clean_domain(competitor_domain),
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
                        "source":     "referring_domains",
                    })
    return items

# ── AI layer ─────────────────────────────────────────────────────────────────

def ai_suggest_competitors(client_name, client_url, industry, market, language) -> list[str]:
    model  = get_gemini()
    prompt = f"""You are an SEO expert.

Client: {client_name} ({client_url})
Industry: {industry}
Market: {market}
Language: {language}

Return exactly 3 direct competitor URLs (just the root domain, no paths) that compete with this client in their market and industry.
Return ONLY a JSON array of 3 strings like: ["competitor1.com", "competitor2.com", "competitor3.com"]
No explanation. No markdown. Pure JSON only."""

    resp = model.generate_content(prompt)
    text = resp.text.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(text)

def ai_categorize_and_enrich(domains: list[dict], client_name: str, industry: str, market: str) -> list[dict]:
    """AI categorizes domains and writes rationale + contact pathway."""
    model   = get_gemini()
    domain_list = "\n".join([
        f"- {d['domain']} (rank:{d['rank']}, backlinks:{d['backlinks']}, spam:{d['spam_score']})"
        for d in domains[:40]
    ])

    prompt = f"""You are a senior link-building strategist at a digital agency.

Client industry: {industry}
Market: {market}

Analyze these domains and for each one return structured data.

Domains:
{domain_list}

For EACH domain return:
- domain: the domain name
- category: one of "free", "paid", "publisher", "blog"
  * free = accepts guest posts, community contributions, editorial submissions at no cost
  * paid = sponsored content, paid placements, advertorial
  * publisher = major media, news, trade publications
  * blog = independent blogs, niche content sites
- rationale: one sentence (max 20 words) explaining WHY this domain is relevant for link building in {industry}
- contact_hint: a short practical note on how to reach them (e.g. "Check /write-for-us", "Editorial team via LinkedIn", "Use contact form at /contact")
- relevance_score: integer 1-10 for how relevant this domain is to {industry} in {market}

Return ONLY a JSON array. No markdown. No explanation. Example format:
[{{"domain":"example.com","category":"free","rationale":"Active tech blog accepting guest posts in B2B SaaS space.","contact_hint":"Submit via /write-for-us page","relevance_score":8}}]"""

    resp   = model.generate_content(prompt)
    text   = resp.text.strip().replace("```json", "").replace("```", "").strip()
    ai_data = json.loads(text)

    # Merge AI data back with DataForSEO metrics
    ai_map = {d["domain"]: d for d in ai_data}
    enriched = []
    for d in domains[:40]:
        ai = ai_map.get(d["domain"], {})
        enriched.append({
            **d,
            "category":        ai.get("category", "free"),
            "rationale":       ai.get("rationale", ""),
            "contact_hint":    ai.get("contact_hint", "Check website contact page"),
            "relevance_score": ai.get("relevance_score", 5),
        })
    return enriched

def ai_generate_content(topic, length, tone, brand_terms, target_prompts, primary_kw, secondary_kws, client_name, industry) -> str:
    model  = get_gemini()
    prompt = f"""You are a senior content strategist writing for {client_name} in the {industry} industry.

Write a guest post / outreach article with the following specifications:

Topic: {topic}
Target word count: {length} words
Tone of voice: {tone}
Brand terms to include naturally: {brand_terms}
AI prompts / questions to target: {target_prompts}
Primary keyword: {primary_kw}
Secondary keywords: {secondary_kws}

Requirements:
- Write the full article, properly structured with H2/H3 headings (use markdown)
- Include the primary keyword in the title, first paragraph, and at least 2 subheadings
- Weave secondary keywords naturally throughout
- Match the tone specified precisely
- Include brand terms authentically — not as forced mentions
- End with a clear, non-salesy conclusion
- Do NOT include a byline, author bio, or meta description — just the article content

Write the full article now."""

    resp = model.generate_content(prompt, generation_config={"max_output_tokens": 4096})
    return resp.text

# ── Session state init ────────────────────────────────────────────────────────

def init_state():
    defaults = {
        "stage":           "input",      # input | results | content
        "client_info":     {},
        "competitors":     [],
        "summaries":       {},
        "raw_domains":     [],
        "enriched":        [],
        "validation":      {},           # domain -> {status, notes}
        "generated_content": "",
        "content_domain":  "",
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

# ══════════════════════════════════════════════════════════════════════════════
# STAGE 1 — INPUT
# ══════════════════════════════════════════════════════════════════════════════

if st.session_state.stage == "input":

    # Section 1 — Client details
    st.markdown("""
    <div class="section-label">
        <div class="section-number">1</div>
        <div class="section-title">Client Details</div>
    </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        client_name = st.text_input("Client Name", placeholder="e.g. Omantel")
        industry    = st.selectbox("Industry", [
            "Telecommunications", "Finance & Banking", "Retail & E-commerce",
            "Travel & Tourism", "Healthcare", "Real Estate", "Technology & SaaS",
            "Education", "Food & Beverage", "Automotive", "Energy & Utilities",
            "Government & Public Sector", "Media & Entertainment", "Other"
        ])
    with col2:
        client_url = st.text_input("Client URL", placeholder="e.g. omantel.om")
        market     = st.selectbox("Market", [
            "UAE", "Saudi Arabia", "Oman", "Qatar", "Kuwait", "Bahrain",
            "Egypt", "Jordan", "Lebanon", "Global", "UK", "US", "Other"
        ])

    language = st.selectbox("Language", ["English", "Arabic", "English & Arabic", "French", "Other"])

    # Section 2 — Competitors
    st.markdown("""
    <div class="section-label">
        <div class="section-number">2</div>
        <div class="section-title">Competitors</div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="exd-alert">Enter up to 3 competitor URLs — or leave blank to let AI suggest them based on your industry and market.</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1: comp1 = st.text_input("Competitor 1", placeholder="competitor.com")
    with col2: comp2 = st.text_input("Competitor 2", placeholder="competitor.com")
    with col3: comp3 = st.text_input("Competitor 3", placeholder="competitor.com")

    st.markdown("<br>", unsafe_allow_html=True)

    run = st.button("▶  Run Backlink Intelligence", use_container_width=True)

    if run:
        if not client_name or not client_url:
            st.error("Client name and URL are required.")
        else:
            st.session_state.client_info = {
                "name":     client_name,
                "url":      client_url,
                "industry": industry,
                "market":   market,
                "language": language,
            }

            competitors = [c for c in [comp1, comp2, comp3] if c.strip()]

            with st.spinner("Running analysis…"):

                # Auto-suggest competitors if not provided
                if not competitors:
                    with st.spinner("AI suggesting competitors…"):
                        try:
                            competitors = ai_suggest_competitors(
                                client_name, client_url, industry, market, language
                            )
                            st.info(f"AI suggested competitors: {', '.join(competitors)}")
                        except Exception as e:
                            st.error(f"Competitor suggestion failed: {e}")
                            competitors = []

                st.session_state.competitors = competitors

                if not competitors:
                    st.error("No competitors available. Please enter at least one manually.")
                    st.stop()

                # DataForSEO calls
                all_domains_for_summary = [client_url] + competitors
                try:
                    with st.spinner("Fetching backlink summaries…"):
                        summaries = fetch_backlink_summary(all_domains_for_summary)
                        st.session_state.summaries = summaries
                except Exception as e:
                    st.warning(f"Summary fetch issue: {e} — continuing without summaries.")

                raw = []
                try:
                    with st.spinner("Running domain intersection (link gap analysis)…"):
                        intersection = fetch_domain_intersection(competitors, client_url)
                        raw.extend(intersection)
                except Exception as e:
                    st.warning(f"Domain intersection issue: {e}")

                try:
                    with st.spinner("Fetching referring domains from competitors…"):
                        for comp in competitors[:2]:  # limit to first 2 for cost
                            refs = fetch_referring_domains(comp, limit=25)
                            raw.extend(refs)
                except Exception as e:
                    st.warning(f"Referring domains issue: {e}")

                # Deduplicate by domain
                seen   = set()
                unique = []
                for d in sorted(raw, key=lambda x: x["rank"], reverse=True):
                    if d["domain"] and d["domain"] not in seen:
                        seen.add(d["domain"])
                        unique.append(d)

                st.session_state.raw_domains = unique[:40]

                # AI enrichment
                if unique:
                    with st.spinner("AI categorizing and enriching results…"):
                        try:
                            enriched = ai_categorize_and_enrich(
                                unique[:40],
                                client_name, industry, market
                            )
                            st.session_state.enriched = sorted(
                                enriched, key=lambda x: x.get("relevance_score", 0), reverse=True
                            )
                        except Exception as e:
                            st.error(f"AI enrichment failed: {e}")
                            st.session_state.enriched = unique[:40]

                # Init validation state
                for d in st.session_state.enriched:
                    domain = d["domain"]
                    if domain not in st.session_state.validation:
                        st.session_state.validation[domain] = {"status": "pending", "notes": ""}

                st.session_state.stage = "results"
                st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# STAGE 2 — RESULTS & VALIDATION
# ══════════════════════════════════════════════════════════════════════════════

elif st.session_state.stage == "results":

    info = st.session_state.client_info

    # Back button
    if st.button("← New Analysis"):
        st.session_state.stage = "input"
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Client summary boxes
    st.markdown("""
    <div class="section-label">
        <div class="section-number">1</div>
        <div class="section-title">Backlink Profile Snapshot</div>
    </div>""", unsafe_allow_html=True)

    summaries = st.session_state.summaries
    if summaries:
        cols = st.columns(len(summaries))
        for i, (domain, metrics) in enumerate(summaries.items()):
            is_client = domain == clean_domain(info["url"])
            with cols[i]:
                label = f"✦ {info['name']}" if is_client else domain
                st.markdown(f"""
                <div class="summary-box">
                    <div class="summary-box-title">{'Client' if is_client else 'Competitor'}</div>
                    <div class="summary-domain">{label}</div>
                    <div class="summary-metrics">
                        <div class="summary-metric">DR <span>{metrics.get('rank', 0)}</span></div>
                        <div class="summary-metric">Backlinks <span>{metrics.get('backlinks', 0):,}</span></div>
                        <div class="summary-metric">Ref. Domains <span>{metrics.get('referring_domains', 0):,}</span></div>
                    </div>
                </div>""", unsafe_allow_html=True)

    # Validation status bar
    val    = st.session_state.validation
    total  = len(val)
    approved = sum(1 for v in val.values() if v["status"] == "approved")
    rejected = sum(1 for v in val.values() if v["status"] == "rejected")
    pending  = sum(1 for v in val.values() if v["status"] == "pending")

    st.markdown(f"""
    <div class="status-bar">
        <div class="status-item">
            <div class="status-value">{total}</div>
            <div class="status-label">Total Opportunities</div>
        </div>
        <div class="status-item">
            <div class="status-value" style="color:#ff6b2b">{pending}</div>
            <div class="status-label">Pending Review</div>
        </div>
        <div class="status-item">
            <div class="status-value" style="color:#22c55e">{approved}</div>
            <div class="status-label">Approved</div>
        </div>
        <div class="status-item">
            <div class="status-value" style="color:#ef4444">{rejected}</div>
            <div class="status-label">Rejected</div>
        </div>
    </div>""", unsafe_allow_html=True)

    # Tabs by category
    st.markdown("""
    <div class="section-label">
        <div class="section-number">2</div>
        <div class="section-title">Opportunities — Review & Validate</div>
    </div>""", unsafe_allow_html=True)

    enriched = st.session_state.enriched

    def get_top(category, n=10):
        return [d for d in enriched if d.get("category") == category][:n]

    tab_free, tab_paid, tab_pub, tab_blog, tab_approved = st.tabs([
        "Free Opportunities", "Paid Placements", "Publishers", "Blogs", "✓ Approved"
    ])

    def render_domain_cards(domains, tab_key):
        if not domains:
            st.markdown('<p style="color:#555;font-size:0.85rem;padding:1rem 0;">No domains found in this category.</p>', unsafe_allow_html=True)
            return

        for d in domains:
            domain  = d["domain"]
            vstatus = st.session_state.validation.get(domain, {}).get("status", "pending")
            cat     = d.get("category", "free")
            badge_class = f"badge-{cat}"

            status_indicator = {"approved": "✓", "rejected": "✗", "pending": "·"}[vstatus]

            st.markdown(f"""
            <div class="domain-card {vstatus}">
                <div class="card-domain">{status_indicator} {domain}</div>
                <div class="card-meta">
                    <div class="card-metric">DR <span>{d.get('rank', 0)}</span></div>
                    <div class="card-metric">Backlinks <span>{d.get('backlinks', 0):,}</span></div>
                    <div class="card-metric">Spam <span style="color:{spam_color(d.get('spam_score',0))}">{d.get('spam_score', 0)}</span></div>
                    <div class="card-metric">Relevance <span>{d.get('relevance_score', '–')}/10</span></div>
                    <span class="badge {badge_class}">{cat}</span>
                </div>
                <div class="card-rationale">{d.get('rationale', '')}</div>
                <div class="card-contact">📬 {d.get('contact_hint', '')}</div>
            </div>""", unsafe_allow_html=True)

            col_a, col_r, col_n = st.columns([1, 1, 3])
            with col_a:
                if st.button("✓ Approve", key=f"approve_{tab_key}_{domain}"):
                    st.session_state.validation[domain]["status"] = "approved"
                    st.rerun()
            with col_r:
                if st.button("✗ Reject", key=f"reject_{tab_key}_{domain}"):
                    st.session_state.validation[domain]["status"] = "rejected"
                    st.rerun()
            with col_n:
                note = st.text_input(
                    "Notes", value=st.session_state.validation[domain].get("notes", ""),
                    key=f"note_{tab_key}_{domain}", label_visibility="collapsed",
                    placeholder="Add reviewer notes…"
                )
                st.session_state.validation[domain]["notes"] = note

    with tab_free:
        render_domain_cards(get_top("free"), "free")
    with tab_paid:
        render_domain_cards(get_top("paid"), "paid")
    with tab_pub:
        render_domain_cards(get_top("publisher"), "pub")
    with tab_blog:
        render_domain_cards(get_top("blog"), "blog")

    with tab_approved:
        approved_list = [
            d for d in enriched
            if st.session_state.validation.get(d["domain"], {}).get("status") == "approved"
        ]
        if not approved_list:
            st.markdown('<p style="color:#555;font-size:0.85rem;padding:1rem 0;">No domains approved yet. Review and approve opportunities in the other tabs.</p>', unsafe_allow_html=True)
        else:
            # Export
            export_data = []
            for d in approved_list:
                export_data.append({
                    "Domain":        d["domain"],
                    "Category":      d.get("category", ""),
                    "DR":            d.get("rank", 0),
                    "Backlinks":     d.get("backlinks", 0),
                    "Spam Score":    d.get("spam_score", 0),
                    "Relevance":     d.get("relevance_score", ""),
                    "Rationale":     d.get("rationale", ""),
                    "Contact Hint":  d.get("contact_hint", ""),
                    "Notes":         st.session_state.validation.get(d["domain"], {}).get("notes", ""),
                })
            df = pd.DataFrame(export_data)
            csv = df.to_csv(index=False).encode("utf-8")
            col_exp, col_cont = st.columns([1, 2])
            with col_exp:
                st.download_button(
                    "⬇ Export Approved CSV",
                    data=csv,
                    file_name=f"backlink_opportunities_{info['name'].lower().replace(' ','_')}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            with col_cont:
                if st.button("✦ Generate Content →", use_container_width=True):
                    st.session_state.stage = "content"
                    st.rerun()

            render_domain_cards(approved_list, "approved")

# ══════════════════════════════════════════════════════════════════════════════
# STAGE 3 — CONTENT GENERATION
# ══════════════════════════════════════════════════════════════════════════════

elif st.session_state.stage == "content":

    info = st.session_state.client_info

    col_back, _ = st.columns([1, 4])
    with col_back:
        if st.button("← Back to Results"):
            st.session_state.stage = "results"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div class="section-label">
        <div class="section-number">3</div>
        <div class="section-title">Content Generation</div>
    </div>""", unsafe_allow_html=True)

    approved_list = [
        d for d in st.session_state.enriched
        if st.session_state.validation.get(d["domain"], {}).get("status") == "approved"
    ]

    if approved_list:
        target_options = ["— No specific target —"] + [d["domain"] for d in approved_list]
        content_domain = st.selectbox("Target Domain (Approved)", target_options)
        st.session_state.content_domain = content_domain
    else:
        st.markdown('<div class="exd-alert">No approved domains yet. You can still generate content without a target.</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        topic       = st.text_input("Article Topic", placeholder="e.g. The future of 5G connectivity in the GCC")
        tone        = st.selectbox("Tone of Voice", [
            "Authoritative & Expert", "Conversational & Friendly",
            "Thought Leadership", "Educational & Informative",
            "Journalistic", "Persuasive"
        ])
        primary_kw  = st.text_input("Primary Keyword", placeholder="e.g. 5G connectivity Oman")
        brand_terms = st.text_input("Brand Terms", placeholder="e.g. Omantel, SuperNet, OmPay")

    with col2:
        length          = st.number_input("Word Count", min_value=300, max_value=3000, value=800, step=100)
        target_prompts  = st.text_area("AI Prompts / Questions to Target", height=100,
                                       placeholder="e.g. What is the best 5G provider in Oman?\nHow does 5G improve business productivity?")
        secondary_kws   = st.text_input("Secondary Keywords", placeholder="e.g. 5G business, high-speed internet Oman")

    st.markdown("<br>", unsafe_allow_html=True)
    gen = st.button("✦ Generate Content", use_container_width=True)

    if gen:
        if not topic or not primary_kw:
            st.error("Topic and primary keyword are required.")
        else:
            with st.spinner("Generating content…"):
                try:
                    content = ai_generate_content(
                        topic, length, tone, brand_terms,
                        target_prompts, primary_kw, secondary_kws,
                        info.get("name", ""), info.get("industry", "")
                    )
                    st.session_state.generated_content = content
                except Exception as e:
                    st.error(f"Content generation failed: {e}")

    if st.session_state.generated_content:
        st.markdown("<hr class='exd-divider'>", unsafe_allow_html=True)

        st.markdown("""
        <div class="section-label">
            <div class="section-number">4</div>
            <div class="section-title">Generated Content — Human Review Required</div>
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="exd-alert">⚠ This content is AI-generated and must be reviewed and edited by your team before outreach or publication.</div>', unsafe_allow_html=True)

        # Editable content
        edited = st.text_area(
            "Review & Edit Content",
            value=st.session_state.generated_content,
            height=600,
            label_visibility="collapsed"
        )

        col_dl, col_copy = st.columns(2)
        with col_dl:
            st.download_button(
                "⬇ Download as .txt",
                data=edited.encode("utf-8"),
                file_name=f"content_{primary_kw.lower().replace(' ','_') if 'primary_kw' in dir() else 'article'}_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        with col_copy:
            word_count = len(edited.split())
            st.markdown(f'<div style="text-align:center;color:#555;font-size:0.8rem;padding:0.6rem;">{word_count:,} words</div>', unsafe_allow_html=True)
