import sqlite3, json
from datetime import datetime, timedelta
from app.config import config

def get_db():
    db = sqlite3.connect(config.DB_PATH)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    import os; os.makedirs(os.path.dirname(config.DB_PATH), exist_ok=True)
    db = get_db()
    db.executescript("""
        CREATE TABLE IF NOT EXISTS conversations (
            wa_id       TEXT PRIMARY KEY,
            stage       TEXT DEFAULT 'new',
            lang        TEXT DEFAULT 'en',
            session_data TEXT DEFAULT '{}',
            created_at  TEXT,
            updated_at  TEXT
        );
        CREATE TABLE IF NOT EXISTS messages (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            wa_id       TEXT,
            direction   TEXT,
            content     TEXT,
            created_at  TEXT
        );
        CREATE TABLE IF NOT EXISTS leads (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            wa_id       TEXT,
            name        TEXT,
            phone       TEXT,
            lang        TEXT,
            interest    TEXT,
            notes       TEXT,
            status      TEXT DEFAULT 'new',
            created_at  TEXT,
            updated_at  TEXT
        );
    """)
    db.commit(); db.close()

def _now(): return datetime.utcnow().isoformat()

def get_conv(wa_id):
    db = get_db()
    row = db.execute("SELECT * FROM conversations WHERE wa_id=?", (wa_id,)).fetchone()
    db.close()
    return dict(row) if row else None

def upsert_conv(wa_id, **kwargs):
    db = get_db()
    now = _now()
    existing = db.execute("SELECT wa_id FROM conversations WHERE wa_id=?", (wa_id,)).fetchone()
    if existing:
        sets = ", ".join(f"{k}=?" for k in kwargs)
        vals = list(kwargs.values()) + [now, wa_id]
        db.execute(f"UPDATE conversations SET {sets}, updated_at=? WHERE wa_id=?", vals)
    else:
        kwargs.setdefault('stage', 'new')
        kwargs.setdefault('lang', 'en')
        kwargs.setdefault('session_data', '{}')
        cols = ', '.join(['wa_id'] + list(kwargs.keys()) + ['created_at', 'updated_at'])
        placeholders = ', '.join(['?'] * (len(kwargs) + 3))
        db.execute(f"INSERT INTO conversations ({cols}) VALUES ({placeholders})",
                   [wa_id] + list(kwargs.values()) + [now, now])
    db.commit(); db.close()

def get_session(wa_id):
    db = get_db()
    row = db.execute("SELECT session_data, updated_at FROM conversations WHERE wa_id=?", (wa_id,)).fetchone()
    db.close()
    if not row: return {}
    # Check timeout
    updated = datetime.fromisoformat(row['updated_at']) if row['updated_at'] else datetime.utcnow()
    if (datetime.utcnow() - updated) > timedelta(minutes=config.SESSION_TIMEOUT_MIN):
        upsert_conv(wa_id, stage='new', session_data='{}')
        return {}
    return json.loads(row['session_data'] or '{}')

def set_session(wa_id, data):
    upsert_conv(wa_id, session_data=json.dumps(data, ensure_ascii=False))

def get_stage(wa_id):
    db = get_db()
    row = db.execute("SELECT stage FROM conversations WHERE wa_id=?", (wa_id,)).fetchone()
    db.close()
    return row['stage'] if row else 'new'

def set_stage(wa_id, stage):
    upsert_conv(wa_id, stage=stage)

def get_lang(wa_id):
    db = get_db()
    row = db.execute("SELECT lang FROM conversations WHERE wa_id=?", (wa_id,)).fetchone()
    db.close()
    return row['lang'] if row else 'en'

def set_lang(wa_id, lang):
    upsert_conv(wa_id, lang=lang)

def add_message(wa_id, direction, content):
    db = get_db()
    db.execute("INSERT INTO messages (wa_id, direction, content, created_at) VALUES (?,?,?,?)",
               (wa_id, direction, content, _now()))
    db.commit(); db.close()

def get_history(wa_id, limit=10):
    db = get_db()
    rows = db.execute(
        "SELECT direction, content FROM messages WHERE wa_id=? ORDER BY id DESC LIMIT ?",
        (wa_id, limit)).fetchall()
    db.close()
    return [{'role': 'user' if r['direction']=='in' else 'assistant', 'content': r['content']}
            for r in reversed(rows)]

def upsert_lead(wa_id, **kwargs):
    db = get_db()
    now = _now()
    existing = db.execute("SELECT id FROM leads WHERE wa_id=? ORDER BY id DESC LIMIT 1", (wa_id,)).fetchone()
    if existing:
        sets = ", ".join(f"{k}=?" for k in kwargs)
        db.execute(f"UPDATE leads SET {sets}, updated_at=? WHERE id=?",
                   list(kwargs.values()) + [now, existing['id']])
    else:
        kwargs['wa_id'] = wa_id
        kwargs['created_at'] = now; kwargs['updated_at'] = now
        cols = ', '.join(kwargs.keys())
        placeholders = ', '.join(['?'] * len(kwargs))
        db.execute(f"INSERT INTO leads ({cols}) VALUES ({placeholders})", list(kwargs.values()))
    db.commit(); db.close()

def get_leads(status=None, limit=50):
    db = get_db()
    if status:
        rows = db.execute("SELECT * FROM leads WHERE status=? ORDER BY id DESC LIMIT ?",
                          (status, limit)).fetchall()
    else:
        rows = db.execute("SELECT * FROM leads ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    db.close()
    return [dict(r) for r in rows]

def get_stats():
    db = get_db()
    total_conv  = db.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]
    total_msg   = db.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
    total_leads = db.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
    new_leads   = db.execute("SELECT COUNT(*) FROM leads WHERE status='new'").fetchone()[0]
    by_lang     = db.execute("SELECT lang, COUNT(*) as c FROM conversations GROUP BY lang").fetchall()
    db.close()
    return {
        'conversations': total_conv, 'messages': total_msg,
        'leads': total_leads, 'new_leads': new_leads,
        'by_language': {r['lang']: r['c'] for r in by_lang}
    }
