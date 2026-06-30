# 🚀 Marketing Automation Agent System

<div align="center">

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI_API-412991?style=for-the-badge&logo=openai&logoColor=white)
![Instagram API](https://img.shields.io/badge/Instagram_Graph_API-E4405F?style=for-the-badge&logo=instagram&logoColor=white)

![Ideogram](https://img.shields.io/badge/Ideogram_AI-6C47FF?style=for-the-badge)
![Automation](https://img.shields.io/badge/Workflow_Automation-FF6B00?style=for-the-badge)
![SEO](https://img.shields.io/badge/SEO_Optimization-0AA545?style=for-the-badge)
![REST API](https://img.shields.io/badge/REST_API-0096D6?style=for-the-badge)

</div>

---

## 📌 Overview

A production-ready **AI-powered Marketing Automation System** built to automate end-to-end content generation and social media publishing.

The system autonomously generates:

- SEO-optimized blogs and website content  
- Keyword intelligence and trend analysis  
- Social media creatives with custom branding  
- AI-generated captions and trending hashtags  
- Automated Instagram publishing workflow  

### Key Impact

✔ Reduced manual content creation time by **90%**  
✔ Generated branded social media creatives in **under 2 minutes**  
✔ Automated hashtag generation based on topic relevance  
✔ Built an end-to-end Instagram publishing pipeline  

---

# ⚡ System Architecture

```text
User Input Topic
       ↓
Trend Analysis Engine
       ↓
AI Caption Generation
       ↓
Hashtag Recommendation Engine
       ↓
Brand-Aware Image Generation
       ↓
Content Approval Pipeline
       ↓
Instagram Auto Publishing
```

---

# 📸 Screenshots

## Assigned Trending Hashtags Based on Topic (Editable)

<img width="1549" height="885" alt="image" src="https://github.com/user-attachments/assets/ceb24fd5-3fe4-42fc-a4bf-f7364c223ae5" />

---

## AI Generated Creative with Custom Branding + Auto Published on Instagram

<img width="1580" height="893" alt="image" src="https://github.com/user-attachments/assets/a09667a3-2fdc-49b6-af3c-1309cef2e5ba" />

---

# 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r ../requirements.txt
```

### 2. Configure Environment Variables

```bash
cp ../.env.example ../.env
```

Fill API credentials inside `.env`

---

### 3. Run Application

```bash
cd ..
python app.py
```

---

### 4. Open Browser

```bash
http://localhost:5000
```

---

# 📁 Project Structure

```text
DMA_Web/
├── app.py                         # Flask server entry point
├── post_routes.py                # Instagram automation logic
├── requirements.txt             # Dependencies
├── .env.example                 # Environment template
│
├── templates/
│   └── index.html              # Dashboard UI
│
├── static/
│   ├── css/style.css          # Styling
│   └── js/app.js              # Frontend logic
│
├── Social_Agent/
│   ├── instagram_graph_api.py
│   └── src/modules/ai/
│        └── ideogram_gen.py
│
├── data/generated_images/      # Generated creatives
└── logs/                       # Application logs
```

---

# 🔑 Required Credentials

## Core AI APIs

| Variable | Description |
|-----------|------------|
| `OPENAI_API_KEY` | OpenAI API Access |
| `IDEOGRAM_API_KEY` | Ideogram API Access |

---

## Instagram Automation APIs

| Variable | Description |
|-----------|------------|
| `INSTAGRAM_TOKEN_1` | Instagram Graph API Token |
| `INSTAGRAM_ID_1` | Instagram Business Account ID |

---

# 🔄 Automation Workflow

### Step 1 → Topic Input

User provides content topic.

### Step 2 → AI Processing

System generates:

- Caption  
- SEO keywords  
- Trending hashtags  

### Step 3 → Creative Generation

AI generates custom branded image.

### Step 4 → Review Layer

User can edit/regenerate content.

### Step 5 → Publishing

Instant Instagram publishing or scheduling.

---

# 📊 Performance Metrics

| Metric | Result |
|----------|--------|
| Content Generation Speed | < 2 Minutes |
| Manual Effort Reduction | 90% |
| Social Content Automation | End-to-End |
| API Integrations | 4+ Services |

---

# 🔧 Troubleshooting

### Module Error

```bash
pip install -r ../requirements.txt
```

### Instagram Publishing Failure

Ensure:

- Instagram account is Business/Creator account  
- Connected with Facebook Developer App  

### Port Already In Use

Change port inside `.env`

```bash
PORT=5001
```

---

# 🎯 Future Improvements

- Multi-platform posting (LinkedIn, X, Facebook)  
- Content scheduling calendar  
- Analytics dashboard  
- AI competitor analysis  
- Marketing campaign automation  
