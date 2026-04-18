# SHS-Website

> Soon Hoe Management Website + WhatsApp Chatbot + OpenClaw Posters

## 🌐 Live Demo

Visit: **https://stepying-star.github.io/SHS-Website/**

## 📁 Structure

```
SHS-Website/
├── index.html                     ← Entry redirect (for GitHub Pages)
│
├── website/                       ← Soon Hoe Management main website
│   └── soonhoe_website.html       ← Full bilingual 7-language site (EN/ZH/MS/JA/TH/VI/FIL)
│                                    · Japanese design aesthetic
│                                    · GAIAGenX AI services overlay
│                                    · WhatsApp & email contacts
│
├── posters/                       ← OpenClaw + Hermes marketing posters
│   ├── openclaw-free-setup-poster_1_6.html    ← Main version (7-language selector)
│   ├── openclaw-free-setup-poster.html        ← English version
│   └── openclaw-free-setup-poster-zh.html     ← Chinese version
│
└── whatsapp_bot/                  ← WhatsApp Chatbot (Python/Flask)
    ├── app/                       ← Flask application
    │   ├── main.py                ← Webhook + admin dashboard
    │   ├── config.py              ← Configuration (env-based)
    │   ├── database.py            ← SQLite for leads & conversations
    │   ├── whatsapp.py            ← WhatsApp Cloud API client
    │   ├── ai_engine.py           ← Claude AI + knowledge base
    │   └── conversation.py        ← Stage machine + 7-language menus
    ├── run.py                     ← Development entrypoint
    ├── wsgi.py                    ← Production (gunicorn)
    ├── requirements.txt
    ├── .env.example               ← Copy to .env, fill in secrets
    ├── SETUP.md                   ← Full deployment guide
    ├── nginx.conf.example         ← Nginx reverse proxy config
    └── soonhoe-bot.service        ← Systemd service
```

## 🚀 Features

### Website
- **7 Languages**: English, 中文, Bahasa Melayu, 日本語, ภาษาไทย, Tiếng Việt, Filipino
- **150 i18n keys** × 7 languages = 1,050 translations
- Japanese design aesthetic (Shippori Mincho + Cormorant Garamond)
- Responsive mobile-friendly layout
- GAIAGenX AI services section with full-screen overlay

### WhatsApp Chatbot
- WhatsApp Business Cloud API (Meta official)
- Claude AI for intelligent responses
- Auto language detection (7 languages)
- Lead capture with admin dashboard
- Production-ready: Gunicorn + Nginx + Systemd

### OpenClaw Posters
- Built-in 7-language selector
- Red/gold OpenClaw brand styling
- Back navigation button

## 📝 Contact

- **Email**: admin@soonhoe.com.sg
- **WhatsApp**: +65 9035 9666
- **Website**: [www.soonhoe.com.sg](https://www.soonhoe.com.sg)

## 🏢 Offices

- Singapore (HQ) · Malaysia · China · Japan

---

© 2026 SOON HOE GROUP. All Rights Reserved.
