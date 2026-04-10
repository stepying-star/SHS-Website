# Soon Hoe WhatsApp Bot — Setup Guide

## Prerequisites
- Ubuntu 20.04+ VPS with public IP
- Domain name (required for HTTPS webhook)
- Python 3.10+
- Meta Business Account + WhatsApp Business API access

---

## Step 1: Meta / WhatsApp Business API Setup

1. Go to https://developers.facebook.com
2. Create App → **Business** type
3. Add **WhatsApp** product
4. In WhatsApp → Getting Started:
   - Note your **Phone Number ID**
   - Generate a **Permanent System User Token** (not temporary)
   - Note your **App Secret**
5. In WhatsApp → Configuration → Webhooks:
   - Webhook URL: `https://YOUR_DOMAIN/webhook`
   - Verify Token: `soonhoe_verify_2026` (match your .env)
   - Subscribe to: `messages`
6. Add a real phone number or use the test number (sandbox)

---

## Step 2: Server Setup

```bash
# Update server
sudo apt update && sudo apt upgrade -y

# Install Python & nginx
sudo apt install python3 python3-pip python3-venv nginx certbot python3-certbot-nginx -y

# Clone / upload your bot files
mkdir -p /home/ubuntu/whatsapp_bot
cd /home/ubuntu/whatsapp_bot
# Upload files here...

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
nano .env
# → Fill in all values

# Create data/logs directories
mkdir -p data logs
```

---

## Step 3: SSL Certificate (HTTPS required by Meta)

```bash
sudo certbot --nginx -d YOUR_DOMAIN
```

---

## Step 4: Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/soonhoe-bot
# Paste the nginx.conf content, replace YOUR_DOMAIN

sudo ln -s /etc/nginx/sites-available/soonhoe-bot /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

---

## Step 5: Systemd Service (auto-start)

```bash
sudo nano /etc/systemd/system/soonhoe-bot.service
# Paste the soonhoe-bot.service content

sudo systemctl daemon-reload
sudo systemctl enable soonhoe-bot
sudo systemctl start soonhoe-bot
sudo systemctl status soonhoe-bot
```

---

## Step 6: Test

```bash
# Check health
curl https://YOUR_DOMAIN/health

# View logs
tail -f /home/ubuntu/whatsapp_bot/logs/bot.log

# Admin dashboard
https://YOUR_DOMAIN/admin?token=YOUR_ADMIN_TOKEN
```

---

## Step 7: WhatsApp Webhook Verification

After your server is running with HTTPS:
1. Go to Meta Developers → WhatsApp → Configuration
2. Click **Verify and Save** for your webhook URL
3. You should see "✓ Verified" 

---

## Maintenance

```bash
# Restart bot
sudo systemctl restart soonhoe-bot

# View live logs
tail -f logs/bot.log

# View leads (JSON)
curl "https://YOUR_DOMAIN/admin/leads.json?token=YOUR_TOKEN"
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Webhook not verified | Check VERIFY_TOKEN matches .env |
| Bot not responding | Check WA_TOKEN and PHONE_NUMBER_ID |
| AI not working | Check ANTHROPIC_API_KEY |
| HTTPS error | Run certbot again |

---

## Admin Dashboard

Access at: `https://YOUR_DOMAIN/admin?token=YOUR_ADMIN_TOKEN`

Shows:
- Total conversations, messages, leads
- Users by language breakdown  
- Recent leads with contact details
- Lead export: `/admin/leads.json?token=...`
