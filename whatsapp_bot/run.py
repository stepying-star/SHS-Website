"""Entry point"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from app.main import app
from app.config import Config

if __name__ == "__main__":
    cfg = Config()
    print(f"Starting Soon Hoe WhatsApp Bot on port {cfg.PORT}")
    app.run(host="0.0.0.0", port=cfg.PORT, debug=False)
