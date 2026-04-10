"""Configuration — loads from environment variables"""
import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    # WhatsApp Cloud API
    WA_PHONE_NUMBER_ID: str = os.getenv("WA_PHONE_NUMBER_ID", "")
    WA_TOKEN: str           = os.getenv("WA_TOKEN", "")
    WA_VERIFY_TOKEN: str    = os.getenv("WA_VERIFY_TOKEN", "soonhoe_bot_2026")
    WA_APP_SECRET: str      = os.getenv("WA_APP_SECRET", "")

    # Claude AI
    ANTHROPIC_API_KEY: str  = os.getenv("ANTHROPIC_API_KEY", "")
    CLAUDE_MODEL: str       = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")

    # App
    PORT: int               = int(os.getenv("PORT", 5000))
    DB_PATH: str            = os.getenv("DB_PATH", "soonhoe_bot.db")
    ADMIN_TOKEN: str        = os.getenv("ADMIN_TOKEN", "change_this_secret")
    SESSION_TIMEOUT: int    = int(os.getenv("SESSION_TIMEOUT", 3600))

    # Contact
    HUMAN_AGENT_PHONE: str  = os.getenv("HUMAN_AGENT_PHONE", "")
    CONTACT_EMAIL: str      = os.getenv("CONTACT_EMAIL", "admin@soonhoe.com.sg")
