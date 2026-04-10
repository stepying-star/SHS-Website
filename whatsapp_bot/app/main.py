import json, logging, hmac, hashlib
from flask import Flask, request, jsonify, abort
from app.config import config
from app import database as db
from app import whatsapp as wa
from app import conversation as conv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s — %(message)s",
    handlers=[
        logging.FileHandler("logs/bot.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger("main")

app = Flask(__name__)
db.init_db()

@app.route("/webhook", methods=["GET"])
def verify():
    mode      = request.args.get("hub.mode")
    token     = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == config.WA_VERIFY_TOKEN:
        log.info("Webhook verified ✓")
        return challenge, 200
    abort(403)

@app.route("/webhook", methods=["POST"])
def webhook():
    # Verify signature
    if config.WA_APP_SECRET:
        sig = request.headers.get("X-Hub-Signature-256", "")
        expected = "sha256=" + hmac.new(
            config.WA_APP_SECRET.encode(), request.data, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected):
            log.warning("Invalid webhook signature")
            abort(403)

    payload = request.get_json(silent=True) or {}
    incoming = wa.parse_incoming(payload)

    if incoming and incoming["text"]:
        log.info(f"← {incoming['wa_id']}: {incoming['text'][:80]}")
        try:
            conv.handle_message(incoming)
        except Exception as e:
            log.exception(f"Error handling message: {e}")
    return jsonify({"status": "ok"})

@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "SoonHoe WhatsApp Bot"})

@app.route("/admin")
def admin():
    token = request.args.get("token", "")
    if token != config.ADMIN_TOKEN:
        abort(403)
    stats = db.get_stats()
    leads = db.get_leads(limit=20)
    html  = f"""<!DOCTYPE html><html><head><title>Soon Hoe Bot Admin</title>
    <meta charset="UTF-8">
    <style>
      body{{font-family:sans-serif;max-width:900px;margin:2rem auto;padding:0 1rem;color:#1a1a2e;}}
      h1{{color:#0c1f3f;border-bottom:2px solid #c4a047;padding-bottom:.5rem;}}
      h2{{color:#3d4a5c;margin-top:2rem;}}
      .stats{{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin:1rem 0;}}
      .stat{{background:#f5f5f0;border:1px solid #e0d5c0;border-radius:8px;padding:1rem;text-align:center;}}
      .stat .n{{font-size:2rem;font-weight:bold;color:#0c1f3f;}}
      .stat .l{{font-size:.8rem;color:#7a8a9e;}}
      table{{width:100%;border-collapse:collapse;margin-top:1rem;font-size:.85rem;}}
      th{{background:#0c1f3f;color:#fff;padding:.6rem .8rem;text-align:left;}}
      td{{padding:.5rem .8rem;border-bottom:1px solid #eee;}}
      tr:hover{{background:#fafaf5;}}
      .badge{{display:inline-block;padding:.2rem .6rem;border-radius:50px;font-size:.75rem;}}
      .new{{background:#fef3c7;color:#92400e;}}
      .captured{{background:#d1fae5;color:#065f46;}}
    </style></head><body>
    <h1>🤖 Soon Hoe WhatsApp Bot — Admin</h1>
    <div class="stats">
      <div class="stat"><div class="n">{stats['conversations']}</div><div class="l">Conversations</div></div>
      <div class="stat"><div class="n">{stats['messages']}</div><div class="l">Messages</div></div>
      <div class="stat"><div class="n">{stats['leads']}</div><div class="l">Total Leads</div></div>
      <div class="stat"><div class="n" style="color:#c4a047">{stats['new_leads']}</div><div class="l">New Leads</div></div>
    </div>
    <h2>📊 Users by Language</h2>
    <p>{" &nbsp;|&nbsp; ".join(f"<b>{k.upper()}</b>: {v}" for k,v in stats["by_language"].items())}</p>
    <h2>📋 Recent Leads</h2>
    <table>
      <tr><th>ID</th><th>Name</th><th>Phone</th><th>WA ID</th><th>Language</th><th>Interest</th><th>Status</th><th>Date</th></tr>
    """
    for l in leads:
        badge = "captured" if l["status"] == "captured" else "new"
        html += f"""<tr>
          <td>{l['id']}</td><td>{l.get('name','—')}</td><td>{l.get('phone','—')}</td>
          <td>{l['wa_id']}</td><td>{l.get('lang','en').upper()}</td>
          <td>{l.get('interest','—')}</td>
          <td><span class="badge {badge}">{l['status']}</span></td>
          <td>{(l.get('created_at','')[:10])}</td></tr>"""
    html += "</table></body></html>"
    return html

@app.route("/admin/leads.json")
def leads_json():
    token = request.args.get("token", "")
    if token != config.ADMIN_TOKEN:
        abort(403)
    return jsonify(db.get_leads())

if __name__ == "__main__":
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
