# 🤖 AI Lead Generation Bot

> Scrape any webpage. Extract structured intelligence. Export to JSON — instantly.

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square&logo=python)
![Gemini](https://img.shields.io/badge/Google-Gemini_2.5_Flash-orange?style=flat-square&logo=google)
![CLI](https://img.shields.io/badge/Interface-CLI-lightgrey?style=flat-square)
![Status](https://img.shields.io/badge/Status-Available-brightgreen?style=flat-square)

---

## 📌 What It Does

**AI Lead Generation Bot** is a command-line tool that scrapes any public webpage, sends the extracted content to Google Gemini AI, and returns structured business intelligence — exported cleanly to a JSON file.

Point it at a competitor's site, a product page, or any business URL. Get back a summary, key points, or sentiment analysis in seconds.

---

## ✨ Features

- 🌐 **Web Scraper** — Extracts all headings and paragraph text from any public URL
- 🤖 **AI Analysis** — Powered by Gemini 2.5 Flash with strict, structured output
- 🎛️ **3 Analysis Modes** — Choose how the AI interprets the content
- 📁 **JSON Export** — Results saved automatically to `data.json`
- 🛡️ **Input Validation** — Handles invalid URLs, empty inputs, and unreachable sites gracefully

---

## 🎛️ Analysis Modes

| Mode | What You Get |
|------|--------------|
| **Summary** | A concise explanation of what the page is about |
| **Key Points** | Three bullet-point takeaways from the content |
| **Sentiment** | A single-word verdict: `positive`, `negative`, or `neutral` |

---

## 📊 Output Format

All results are saved to `data.json` in this structure:

**Summary Mode:**
```json
{
  "url": "https://example.com",
  "mode": "Summary",
  "ai-result": {
    "mode": "Summary",
    "summary": "A short explanation of the page content."
  }
}
```

**Key Points Mode:**
```json
{
  "url": "https://example.com",
  "mode": "Key Points",
  "ai-result": {
    "mode": "Key Points",
    "keypoints": ["Point 1", "Point 2", "Point 3"]
  }
}
```

**Sentiment Mode:**
```json
{
  "url": "https://example.com",
  "mode": "Sentiment",
  "ai-result": {
    "mode": "Sentiment",
    "sentiment": "positive"
  }
}
```

---

## 🚀 Get Access

This tool is available as a licensed script — ready to plug into your workflow.

> 📩 **Interested?** Reach out at: `abdull.devv@gmail.com`

---

## 🖥️ How to Use

1. Run the script from your terminal
2. Enter the target URL when prompted
3. Choose your analysis mode (1, 2, or 3)
4. The AI processes the page and saves results to `data.json`

---

## 🧰 Tech Stack

| Tool | Purpose |
|------|---------|
| `Google Gemini 2.5 Flash` | AI content analysis |
| `BeautifulSoup4` | Web scraping |
| `Requests` | HTTP fetching |
| `python-dotenv` | Secure API key management |

---

## ⚠️ Limitations

- Works on publicly accessible pages only (no login-protected sites)
- Output quality depends on how much readable text the page contains
- Currently processes one URL per run

---

## 🔮 Planned Features

- [ ] Multi-URL batch processing
- [ ] Streamlit UI for non-technical users
- [ ] CSV export option
- [ ] Scheduled scraping / automation mode

---

## 🙋 About

Built by a self-taught developer as part of an AI automation learning roadmap — shipping real tools, not just tutorials.

---

## 📄 License

All rights reserved. This tool is proprietary software. Unauthorized copying, distribution, or use without permission is prohibited.
