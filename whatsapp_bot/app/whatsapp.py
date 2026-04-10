import json, logging, urllib.request, urllib.error
from app.config import config

log = logging.getLogger("whatsapp")
BASE_URL = f"https://graph.facebook.com/v19.0/{config.WA_PHONE_NUMBER_ID}"

def _post(endpoint, data):
    url = f"{BASE_URL}/{endpoint}"
    body = json.dumps(data).encode()
    headers = {
        "Authorization": f"Bearer {config.WA_TOKEN}",
        "Content-Type": "application/json"
    }
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        r = urllib.request.urlopen(req, timeout=10)
        return json.loads(r.read())
    except urllib.error.HTTPError as e:
        log.error(f"WA API error {e.code}: {e.read().decode()}")
        return None
    except Exception as e:
        log.error(f"WA API exception: {e}")
        return None

def mark_read(message_id):
    _post("messages", {"messaging_product": "whatsapp", "status": "read", "message_id": message_id})

def send_text(to, text):
    log.info(f"→ {to}: {text[:80]}")
    return _post("messages", {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"preview_url": False, "body": text}
    })

def send_buttons(to, body, buttons):
    """buttons: list of {"id": "btn_id", "title": "Button Label"} (max 3)"""
    return _post("messages", {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body},
            "action": {
                "buttons": [{"type": "reply", "reply": b} for b in buttons[:3]]
            }
        }
    })

def send_list(to, body, button_label, sections):
    """sections: [{"title": "...", "rows": [{"id":..., "title":..., "description":...}]}]"""
    return _post("messages", {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {"text": body},
            "action": {"button": button_label, "sections": sections}
        }
    })

def parse_incoming(payload):
    """Extract message info from Meta webhook payload"""
    try:
        entry   = payload["entry"][0]
        changes = entry["changes"][0]
        value   = changes["value"]
        msgs    = value.get("messages", [])
        if not msgs:
            return None
        msg     = msgs[0]
        wa_id   = msg["from"]
        msg_id  = msg["id"]
        msg_type = msg.get("type", "")
        text    = ""
        if msg_type == "text":
            text = msg["text"]["body"].strip()
        elif msg_type == "interactive":
            inter = msg["interactive"]
            if inter["type"] == "button_reply":
                text = inter["button_reply"]["id"]
            elif inter["type"] == "list_reply":
                text = inter["list_reply"]["id"]
        profile = value.get("contacts", [{}])[0].get("profile", {})
        name    = profile.get("name", "")
        return {"wa_id": wa_id, "msg_id": msg_id, "type": msg_type, "text": text, "name": name}
    except (KeyError, IndexError):
        return None
