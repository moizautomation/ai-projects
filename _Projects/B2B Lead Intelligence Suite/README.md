# 🔍 AI Lead Intelligence Tool

> Paste a list of URLs. Get instant business intelligence on every company — ready for outreach.

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-red?style=flat-square&logo=streamlit)
![Gemini](https://img.shields.io/badge/Google-Gemini_2.5_Flash-orange?style=flat-square&logo=google)
![Status](https://img.shields.io/badge/Status-Available-brightgreen?style=flat-square)

---

## 📌 What It Does

The **AI Lead Intelligence Tool** is a Streamlit web app that automates lead research for sales and marketing teams. You paste a list of company URLs — the tool scrapes each website, sends the content to Google Gemini AI, and returns a structured business profile for every company.

No more manually browsing websites to understand what a company does before a cold email.

---

## ✨ Features

- 🌐 **Auto Web Scraper** — Fetches and extracts meaningful text from any company website
- 🤖 **AI-Powered Analysis** — Uses Gemini 2.5 Flash to analyze each company
- 📋 **Structured Reports** — Returns clean JSON with 5 key business fields per company
- ⚡ **Smart Caching** — Avoids re-analyzing the same URL in the same session
- 🔁 **Deduplication** — Skips duplicate URLs automatically
- 📥 **Download Results** — Export all reports as a single `.json` file
- 🛡️ **Error Handling** — Gracefully handles unreachable sites and empty pages

---

## 📊 AI Output Format

For every company URL, the tool returns:

```json
{
  "what_the_company_does": "...",
  "target_audience": "...",
  "main_product_or_service": "...",
  "customer_pain_points": "...",
  "sales_or_marketing_angle": "..."
}
```

---

## 🚀 Get Access

This tool is available as a hosted service — no setup, no code, just results.

> 📩 **Interested?** Reach out at: `abdull.devv@gmail.com`

---

## 🧰 Tech Stack

| Tool | Purpose |
|------|---------|
| `Streamlit` | Web UI |
| `Google Gemini 2.5 Flash` | AI analysis |
| `BeautifulSoup4` | Web scraping |
| `Requests` | HTTP fetching |
| `python-dotenv` | API key management |

---

## 🖥️ How to Use

1. Open the app and navigate to **AI Lead Intelligence Tool**
2. Paste one or more company URLs (one per line) into the text box
3. Click **Analyze Companies**
4. View the AI-generated report for each company
5. Click **Download Results** to export everything as `ai_result.json`

---

## 📸 App Navigation

| Page | Description |
|------|-------------|
| 🏠 HomePage | Overview of the tool |
| 🔍 AI Lead Intelligence Tool | Main analysis interface |
| 📖 Instructions | Step-by-step usage guide |

---

## ⚠️ Limitations

- Some websites block automated scraping (you'll get a status code error)
- Works best on content-rich marketing/landing pages
- Scraping is limited to the homepage URL provided

---

## 🙋 About

Built by a self-taught developer on **Day 34** of an AI automation learning roadmap — no tutorials, just curiosity and persistence.

---

## 📄 License

All rights reserved. This tool is proprietary software. Unauthorized copying, distribution, or use without permission is prohibited.
