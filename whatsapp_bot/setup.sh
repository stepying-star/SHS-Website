#!/bin/bash
# ═══════════════════════════════════════════════════════
# Soon Hoe WhatsApp Bot — VPS Setup Script
# Ubuntu 22.04 / Debian 11+
# ═══════════════════════════════════════════════════════
set -e

echo "══════════════════════════════════════"
echo "  Soon Hoe WhatsApp Bot Setup"
echo "══════════════════════════════════════"

# 1. System packages
sudo apt-get update -qq
sudo apt-get install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx git

# 2. Create app directory
sudo mkdir -p /opt/soonhoe-bot
sudo chown $USER:$USER /opt/soonhoe-bot
mkdir -p /var/data/soonhoe

# 3. Copy files
cp -r . /opt/soonhoe-bot/
cd /opt/soonhoe-bot

# 4. Python venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Environment file
if [ ! -f .env ]; then
  cp .env.example .env
  echo ""
  echo "⚠️  IMPORTANT: Edit /opt/soonhoe-bot/.env with your credentials!"
  echo "   nano /opt/soonhoe-bot/.env"
  echo ""
fi

# 6. Systemd service
sudo tee /etc/systemd/system/soonhoe-bot.service > /dev/null << EOF
[Unit]
Description=Soon Hoe WhatsApp Bot
After=network.target

[Service]
User=$USER
WorkingDirectory=/opt/soonhoe-bot
Environment=PATH=/opt/soonhoe-bot/venv/bin
ExecStart=/opt/soonhoe-bot/venv/bin/gunicorn wsgi:application \
  --workers 2 \
  --bind 127.0.0.1:5000 \
  --timeout 60 \
  --log-level info \
  --access-logfile /var/log/soonhoe-bot-access.log \
  --error-logfile /var/log/soonhoe-bot-error.log
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable soonhoe-bot

# 7. Nginx config
read -p "Enter your domain (e.g. bot.soonhoe.com.sg): " DOMAIN

sudo tee /etc/nginx/sites-available/soonhoe-bot > /dev/null << EOF
server {
    listen 80;
    server_name $DOMAIN;

    location /webhook {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_read_timeout 60s;
    }

    location /health {
        proxy_pass http://127.0.0.1:5000;
    }

    location /admin {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/soonhoe-bot /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# 8. SSL
sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos -m admin@soonhoe.com.sg

echo ""
echo "════════════════════════════════════════════"
echo "✅  Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit credentials:  nano /opt/soonhoe-bot/.env"
echo "2. Start the bot:     sudo systemctl start soonhoe-bot"
echo "3. Check status:      sudo systemctl status soonhoe-bot"
echo "4. View logs:         sudo journalctl -u soonhoe-bot -f"
echo ""
echo "5. In Meta Developer Console, set webhook URL to:"
echo "   https://$DOMAIN/webhook"
echo ""
echo "Admin dashboard:"
echo "   https://$DOMAIN/admin?token=YOUR_ADMIN_TOKEN"
echo "════════════════════════════════════════════"
