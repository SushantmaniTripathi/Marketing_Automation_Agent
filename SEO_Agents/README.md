# SEO Automation Agent

A professional module for SEO Automation, part of the DMA Web Platform.

---

## 🚀 Quick Start

### 1. Install Python dependencies
```bash
pip install -r ../requirements.txt
```

### 2. Configure credentials
```bash
cp ../.env.example ../.env
# Open ../.env and fill in your API keys
```

### 3. Place your Google Service Account JSON
```bash
# Download from Google Cloud Console → Service Accounts
# Save as: service_account.json (in the project root directory)
```

### 4. Run the server (from root)
```bash
cd ..
python app.py
```

### 5. Open browser
```
http://localhost:5000
```

---

## 📁 Project Structure (SEO Agent Context)

```
DMA_Web/
├── app.py                  ← Flask web server (main entry point)
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
├── SEO_Agents/             ← SEO engine modules (This directory)
│   └── modules/
│       ├── seo_engine.py   ← Core SEO pipeline
│       ├── backlinks.py    ← Dev.to & Hashnode posting
│       ├── contents.py     ← Content generation
│       └── reporting.py    ← Report generation
│
├── reports/                ← SEO reports (CSV, PDF, JSON)
└── logs/                   ← App logs
```

---

## 🔑 Required Credentials (.env)

### Core AI
| Variable | Where to get |
|----------|-------------|
| `OPENAI_API_KEY` | https://platform.openai.com/api-keys |

### SEO Automation
| Variable | Where to get |
|----------|-------------|
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Google Cloud Console → Service Accounts → JSON key |
| `GSC_SITE_URL` | e.g. `sc-domain:yourdomain.com` |
| `GA4_PROPERTY_ID` | e.g. `properties/123456789` |
| `DEVTO_API_KEY` | https://dev.to/settings/account |
| `HASHNODE_API_KEY` | https://hashnode.com/settings/developer |

## 🧭 How SEO Automation Works

Each card is independent — run any step in any order, or click **⚡ Run Full Pipeline**:
- **Keywords + Research** — pulls from Google Search Console + AI keyword expansion
- **Technical Audit** — checks site health, HTTPS, robots.txt, sitemap, response time
- **Backlink Strategy** — AI-generated anchor texts, outreach templates, link plan
- **Performance Report** — GA4 + GSC metrics with AI insights
- **Auto-Post Blogs** — generates full blog post, publishes to Dev.to & Hashnode
- **PDF Report** — downloads a complete formatted SEO PDF

## 🔧 Troubleshooting

**`ModuleNotFoundError`** — Run `pip install -r ../requirements.txt`

**GSC/GA4 not loading** — Make sure `service_account.json` is in the project root and has the correct permissions in Google Cloud Console

**Port in use** — Change `PORT=5000` in `.env` to another port like `5001`
