# Marketing Agent System

A professional module for Marketing System Automation, part of the DMA Web Platform.

# Screenshots

# Assigned Trending Hastags as per TOPIC and can be Editable 

<img width="1549" height="885" alt="image" src="https://github.com/user-attachments/assets/ceb24fd5-3fe4-42fc-a4bf-f7364c223ae5" />

# Image Generated and Published on Instagram

<img width="1580" height="893" alt="image" src="https://github.com/user-attachments/assets/a09667a3-2fdc-49b6-af3c-1309cef2e5ba" />

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

### 3. Run the server (from root)
```bash
cd ..
python app.py
```

### 4. Open browser
```
http://localhost:5000
```

---

## 📁 Project Structure (Social Agent Context)

```
DMA_Web/
├── app.py                  ← Flask web server (main entry point)
├── post_routes.py          ← Instagram Post Automation logic
├── requirements.txt        ← Python dependencies
├── .env.example            ← Credentials template (copy to .env)
│
├── templates/
│   └── index.html          ← Main UI (dark professional dashboard)
│
├── static/
│   ├── css/style.css       ← Dark theme styles
│   └── js/app.js           ← Frontend logic
│
├── Social_Agent/           ← Instagram posting modules (This directory)
│   ├── instagram_graph_api.py
│   └── src/modules/ai/ideogram_gen.py  ← Image generation
│
├── data/generated_images/  ← AI-generated images stored here
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

## 🧭 How Post Automation Works

1. **Step 1** — Enter a topic → AI generates hashtags (via Instagram Graph API + OpenAI fallback)
2. **Step 2** — Review hashtags + AI-generated caption (approve or regenerate)
3. **Step 3** — AI generates image via Ideogram API (approve or regenerate)
4. **Step 4** — Publish immediately or schedule for later

## 🔧 Troubleshooting

**`ModuleNotFoundError`** — Run `pip install -r ../requirements.txt`

**Instagram posts failing** — Ensure your Instagram account is a Business/Creator account connected to a Facebook Page

**Port in use** — Change `PORT=5000` in `.env` to another port like `5001`
