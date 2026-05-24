# Digital Marketing Automation — Web Platform

A professional web-based dashboard replacing the Telegram bot interface.
Post Automation and SEO Automation run from a single browser UI.

---

## 🚀 Quick Start

### 1. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure credentials
```bash
cp .env.example .env
# Open .env and fill in your API keys
```

### 3. (SEO only) Place your Google Service Account JSON
```bash
# Download from Google Cloud Console → Service Accounts
# Save as: service_account.json  (in the project root)
```

### 4. Run the server
```bash
python app.py
```

### 5. Open browser
```
http://localhost:5000
```

---

## 📁 Project Structure

```
DMA_Web/
├── app.py                  ← Flask web server (main entry point)
├── post_routes.py          ← Instagram Post Automation logic
├── seo_routes.py           ← SEO Automation logic
├── requirements.txt        ← Python dependencies
├── .env.example            ← Credentials template (copy to .env)
├── service_account.json    ← Google Service Account (you add this)
│
├── templates/
│   └── index.html          ← Main UI (dark professional dashboard)
│
├── static/
│   ├── css/style.css       ← Dark theme styles
│   └── js/app.js           ← Frontend logic
│
├── Social_Agent/           ← Instagram posting modules
│   ├── instagram_graph_api.py
│   └── src/modules/ai/ideogram_gen.py  ← Image generation
│
├── SEO_Agents/             ← SEO engine modules
│   └── modules/
│       ├── seo_engine.py   ← Core SEO pipeline
│       ├── backlinks.py    ← Dev.to & Hashnode posting
│       ├── contents.py     ← Content generation
│       └── reporting.py    ← Report generation
│
├── data/generated_images/  ← AI-generated images stored here
├── reports/                ← SEO reports (CSV, PDF, JSON)
└── logs/                   ← App logs
```

---

## 🔑 Required Credentials (.env)

### Core AI
| Variable | Where to get |
|----------|-------------|
| `OPENAI_API_KEY` | https://platform.openai.com/api-keys |
| `IDEOGRAM_API_KEY` | https://ideogram.ai/manage-api |

### Post Automation (Instagram)
| Variable | Where to get |
|----------|-------------|
| `INSTAGRAM_TOKEN_1` | Meta Developer Portal → your App → Instagram Graph API |
| `INSTAGRAM_ID_1` | Your Instagram Business Account ID |

### SEO Automation
| Variable | Where to get |
|----------|-------------|
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Google Cloud Console → Service Accounts → JSON key |
| `GSC_SITE_URL` | e.g. `sc-domain:yourdomain.com` |
| `GA4_PROPERTY_ID` | e.g. `properties/123456789` |
| `DEVTO_API_KEY` | https://dev.to/settings/account |
| `HASHNODE_API_KEY` | https://hashnode.com/settings/developer |

## 🧭 How Each Module Works

### Post Automation (Instagram)
1. **Step 1** — Enter a topic → AI generates hashtags (via Instagram Graph API + OpenAI fallback)
2. **Step 2** — Review hashtags + AI-generated caption (approve or regenerate)
3. **Step 3** — AI generates image via Ideogram API (approve or regenerate)
4. **Step 4** — Publish immediately or schedule for later

### SEO Automation
Each card is independent — run any step in any order, or click **⚡ Run Full Pipeline**:
- **Keywords + Research** — pulls from Google Search Console + AI keyword expansion
- **Technical Audit** — checks site health, HTTPS, robots.txt, sitemap, response time
- **Backlink Strategy** — AI-generated anchor texts, outreach templates, link plan
- **Performance Report** — GA4 + GSC metrics with AI insights
- **Auto-Post Blogs** — generates full blog post, publishes to Dev.to & Hashnode
- **PDF Report** — downloads a complete formatted SEO PDF

## 🔧 Troubleshooting

**`ModuleNotFoundError`** — Run `pip install -r requirements.txt`

**Instagram posts failing** — Ensure your Instagram account is a Business/Creator account connected to a Facebook Page

**GSC/GA4 not loading** — Make sure `service_account.json` is in the project root and has the correct permissions in Google Cloud Console

**Port in use** — Change `PORT=5000` in `.env` to another port like `5001`
