# Soon Hoe WhatsApp Chatbot 🤖

AI-powered WhatsApp chatbot for **Soon Hoe Business Management Group** and **GAIAGenX**.  
Supports 7 languages: English, 中文, Melayu, 日本語, ภาษาไทย, Tiếng Việt, Filipino.

---

## Architecture

```
WhatsApp User
     │
     ▼
Meta WhatsApp Cloud API
     │  (webhook POST)
     ▼
Flask App (webhook receiver)
     │
     ├── ConversationManager (state machine)
     │        │
     │        ├── AIEngine (Claude claude-sonnet)
     │        │        └── Knowledge Base (Soon Hoe + GAIAGenX)
     │        │
     │        ├── WhatsAppClient (send messages/buttons)
     │        │
     │        └── Database (SQLite — conversations, leads)
     │
     └── Admin Dashboard (/admin)
```

## Conversation Stages

```
greeting → enquiry ──────────────────────────────→ handoff
               │                                      │
               ├── appointment_interest               │
               ├── appointment_name                   │
               ├── appointment_time                   │
               └── appointment_contact ──→ confirmed  │
```

---

## Quick Setup

### Prerequisites
- VPS with Ubuntu 22.04+ 
- Domain with DNS pointing to your VPS
- Meta Business Account + WhatsApp Business API
- Anthropic API key

### Step 1 — Meta Developer Setup

1. Go to **https://developers.facebook.com**
2. Create App → Business → Add WhatsApp product
3. Note your **Phone Number ID** and **App Secret**
4. Generate a **Permanent Token** (System User in Business Manager)
5. Set Webhook URL: `https://yourdomain.com/webhook`
6. Webhook Verify Token: `soonhoe_bot_2026` (or your custom value)
7. Subscribe to: `messages`

### Step 2 — VPS Deployment

```bash
git clone your-repo
cd soonhoe-whatsapp-bot
bash setup.sh
```

### Step 3 — Configure

```bash
nano /opt/soonhoe-bot/.env
```

Fill in:
```
WA_PHONE_NUMBER_ID=xxx
WA_TOKEN=xxx
WA_APP_SECRET=xxx
ANTHROPIC_API_KEY=sk-ant-xxx
ADMIN_TOKEN=your_strong_password
```

### Step 4 — Start

```bash
sudo systemctl start soonhoe-bot
sudo systemctl status soonhoe-bot
```

---

## Admin Dashboard

```
https://yourdomain.com/admin?token=YOUR_ADMIN_TOKEN
```

Shows:
- Total conversations
- Leads captured
- Messages today
- Language breakdown
- Recent leads table

---

## Files

```
soonhoe-whatsapp-bot/
├── app/
│   ├── __init__.py
│   ├── main.py          # Flask webhook server
│   ├── config.py        # Environment config
│   ├── database.py      # SQLite (conversations, leads)
│   ├── whatsapp.py      # WhatsApp Cloud API client
│   ├── ai_engine.py     # Claude AI + knowledge base
│   └── conversation.py  # State machine
├── run.py               # Dev server
├── wsgi.py              # Gunicorn entry
├── requirements.txt
├── .env.example
├── setup.sh             # VPS auto-setup
└── README.md
```

---

## Logs

```bash
# Bot logs
sudo journalctl -u soonhoe-bot -f

# Nginx access log  
tail -f /var/log/nginx/access.log

# Bot access log
tail -f /var/log/soonhoe-bot-access.log
```
