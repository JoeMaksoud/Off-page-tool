# EXD Backlink Intelligence Tool

AI-powered off-page opportunity discovery and content generation for Performics EXD.

## Stack
- Streamlit (UI)
- DataForSEO Backlinks API (domain data)
- Gemini 2.0 Flash (AI categorization, competitor suggestion, content generation)

## DataForSEO Endpoints Used
- `POST /v3/backlinks/summary/live` — client + competitor profile snapshots
- `POST /v3/backlinks/domain_intersection/live` — link gap (competitors link, client doesn't)
- `POST /v3/backlinks/referring_domains/live` — high-authority referring domains per competitor

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Create `.streamlit/secrets.toml` from `secrets.template.toml`:
   ```
   mkdir -p .streamlit
   cp secrets.template.toml .streamlit/secrets.toml
   ```

3. Fill in your credentials in `.streamlit/secrets.toml`

4. Run locally:
   ```
   streamlit run app.py
   ```

## Deployment (Hugging Face Spaces)
Same pattern as EXD Keyword Research Tool:
- Push to GitHub
- Connect to Hugging Face Spaces
- Add secrets via Space Settings → Repository Secrets

## Workflow

### Stage 1 — Input
- Client name, URL, industry, market, language
- Up to 3 competitor URLs (or AI auto-suggests)

### Stage 2 — Discovery & Validation
- DataForSEO pulls link gap + referring domain data
- AI categorizes into: Free / Paid / Publisher / Blog
- AI writes rationale (why relevant) + contact pathway per domain
- Team reviews each domain: Approve / Reject / Add notes
- Approved domains exportable as CSV

### Stage 3 — Content Generation
- Select target domain from approved list
- Input topic, word count, tone, brand terms, AI prompts, keywords
- Gemini generates full article
- Editable in-app before download

## Note on DataForSEO Backlinks API
Backlinks API may require a separate account tier from SERP APIs.
Check https://app.dataforseo.com/api-access for your account's enabled APIs.
The tool falls back to DATAFORSEO_LOGIN/PASSWORD if backlink-specific credentials aren't set.
