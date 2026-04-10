"""
Claude AI engine with Soon Hoe + GAIAGenX knowledge base
Supports 7 languages, detects intent, generates natural replies
"""
import json, logging, urllib.request, urllib.error
from .config import Config

logger = logging.getLogger(__name__)

# ════════════════════════════════════════════════════════════════════════════
# KNOWLEDGE BASE
# ════════════════════════════════════════════════════════════════════════════
KNOWLEDGE_BASE = """
# SOON HOE BUSINESS MANAGEMENT GROUP (顺和商务管理集团)

## Company Overview
- Full name (EN): Soon Hoe Business Management Co., Ltd. / Soon Hoe Management Pte Ltd (Singapore entity)
- Full name (ZH): 顺和商务管理有限公司 / 顺和集团
- Email: admin@soonhoe.com.sg | Website: www.soonhoe.com.sg
- Offices: Singapore (main), Malaysia (Johor Bahru), China (Beijing, hotline: 400 668 0819), Japan (Osaka)
- Singapore address: 3 Benoi Road #02-209, Singapore 629877 (in COSL Yard)

## Mission
Professional guidance on identity planning and shaping a new start in life. 
Pursuing financial freedom, time freedom, and peace of mind — for clients and their families across Asia.

---

## MODULE 1: Investment Immigration & Residency (投资移民与居留身份)
Target clients: HNW individuals seeking overseas identity, PR status, or residency

Services:
- Singapore PR application (including GIP — Global Investor Programme)
- MM2H — Malaysia My Second Home programme
- Identity & residency planning advisory
- Family office structuring & setup in Singapore
- Singapore bank account opening (personal & corporate)
- High-net-worth asset allocation advice

Pricing: Custom quotation based on client profile. Contact for consultation.

---

## MODULE 2: Business Setup & Overseas Expansion (企业出海与海外布局)
Target clients: Businesses expanding from China/Asia to Singapore/SEA

Services:
- Company incorporation & corporate structuring in Singapore
- Work pass applications: EP (Employment Pass), DP (Dependant Pass), S Pass
- Shareholder agreements & legal advisory
- Business inspection tours & enterprise visits to Singapore
- Cross-border HR & payroll management
- Enterprise overseas training programmes

---

## MODULE 3: Lifestyle, Education & Real Estate (生活、教育与地产)
Services:
- International study placements & campus visits (Singapore, UK, Australia, etc.)
- Academic profile enhancement & GPA management
- Career planning & professional development
- Premium overseas property investment
- End-to-end property management & rental
- Premium concierge & lifestyle services

---

## MODULE 4: Enterprise Data Intelligence (企业数据情报服务)
Partnership: Soon Hoe × GAIAGenX × Cross-Border Data (跨境数科)

Services:
- Enterprise background investigation reports (企业背景调查)
- Enterprise profiling & risk labelling
- Southeast Asia partner screening & matching
- Compliance checks & due diligence (DD)
- Supplier & channel partner vetting

Pricing plans:
- Single project: One-off fee per report
- Retainer: Monthly package for ongoing screening
- Annual membership: Best value for law firms, insurers, cross-border platforms

---

## PROFESSIONAL SERVICES (专业技术服务)

### Accounting & Compilation
- Monthly bookkeeping & accounting
- GST submission (quarterly)
- Financial statement compilation
- Management accounts & reporting

### Audit Services
- Statutory audit (ACRA-compliant)
- Special purpose audit
- Internal audit advisory

### Corporate & Individual Tax
- Corporate income tax (ECI & Form C/CS)
- Individual income tax filing
- Tax planning & advisory
- IR8A & IR21 submissions

### Corporate Secretarial
- Annual AGM, resolutions & XBRL filing
- Nominee director & company secretary
- Registered office address service
- Company strike-off & winding-up

### HR & Administration
- Payroll processing & CPF contributions
- CorpPass, SinPass & MOM account setup
- GST registration / de-registration
- Corporate & individual bank account opening
- Recruitment & talent sourcing

### Strategic Consulting & Operations
- Market entry & business strategy
- Process optimisation & cost management
- Project planning, execution & monitoring
- Cross-border operations advisory

---

# GAIAGenX — AI Enterprise Solutions

## Overview
GAIAGenX is an AI enterprise deployment brand under the Soon Hoe Group, focused on bringing intelligent AI solutions to businesses in Singapore and Southeast Asia.

## Services
1. **AI Agent Deployment** — Remote configuration & deployment of custom AI agents
2. **Workflow Automation** — Intelligent automation to eliminate operational bottlenecks
3. **AI Analytics & Insights** — Predictive analytics, anomaly detection, KPI reporting
4. **System Integration** — Connect AI to existing ERP, CRM, HR platforms
5. **AI Training & Enablement** — Executive briefings to hands-on team workshops
6. **Governance & Compliance** — PDPA-aligned responsible AI deployment

## Pricing (GAIAGenX)
- Varies by scope. Start with a free discovery call.
- Contact: admin@soonhoe.com.sg

---

## APPOINTMENT BOOKING FLOW
When a user wants to book a consultation:
1. Ask for preferred service area (Immigration / Business Setup / Education / Data Intelligence / GAIAGenX / General)
2. Ask for preferred date and time (suggest business hours: Mon-Fri 9am-6pm SGT)
3. Ask for preferred contact method (WhatsApp callback / Video call / In-person Singapore)
4. Ask for full name and email
5. Confirm and summarise the booking request
6. Inform that the team will confirm within 1 business day

---

## LANGUAGE POLICY
Always respond in the same language the user writes in:
- English → Reply in English
- Chinese (Simplified or Traditional) → Reply in Chinese (Simplified)
- Malay → Reply in Malay
- Japanese → Reply in Japanese
- Thai → Reply in Thai
- Vietnamese → Reply in Vietnamese
- Filipino/Tagalog → Reply in Filipino
"""

# ════════════════════════════════════════════════════════════════════════════
# SYSTEM PROMPTS PER LANGUAGE
# ════════════════════════════════════════════════════════════════════════════
SYSTEM_PROMPTS = {
    "en": """You are Soo, the friendly AI assistant for Soon Hoe Business Management Group and GAIAGenX.
You help clients on WhatsApp with enquiries about immigration, company setup, education, real estate, professional accounting/audit/tax/secretarial services, and GAIAGenX AI enterprise solutions.

Personality: warm, professional, concise. Never overly formal. Keep messages short (3-5 sentences max per reply) — this is WhatsApp, not email.

Rules:
1. Always respond in the user's language.
2. For pricing, always say "contact us for a custom quote" — never invent numbers.
3. If unsure, offer to connect them with a human consultant.
4. For appointment requests, follow the booking flow in the knowledge base.
5. End each message with a clear next-step question when relevant.
6. Never fabricate information not in the knowledge base.
7. Keep WhatsApp formatting: use *bold* sparingly, avoid markdown tables.

Knowledge base:
""" + KNOWLEDGE_BASE,

    "zh": """你是Soo，顺和商务管理集团和GAIAGenX的AI客服助手。
你在WhatsApp上帮助客户解答关于移民、公司注册、教育、地产、专业服务（会计/审计/税务/企业秘书）以及GAIAGenX AI企业解决方案的咨询。

性格：亲切、专业、简洁。每次回复保持简短（3-5句话），这是WhatsApp，不是邮件。

规则：
1. 始终用客户的语言回复。
2. 价格问题，始终说"请联系我们获取定制报价"——不要臆造数字。
3. 如不确定，提出转接人工顾问。
4. 预约咨询时，按知识库中的预约流程进行。
5. 每次回复以清晰的下一步问题结尾（适当时）。
6. 不捏造知识库以外的信息。
7. WhatsApp格式：谨慎使用*粗体*，避免markdown表格。

知识库：
""" + KNOWLEDGE_BASE,
}

# For other languages, default to English system prompt but instruct to reply in target language
for lang in ["ms", "ja", "th", "vi", "fil"]:
    SYSTEM_PROMPTS[lang] = SYSTEM_PROMPTS["en"]


class AIEngine:
    API_URL = "https://api.anthropic.com/v1/messages"

    def __init__(self, cfg: Config):
        self.api_key = cfg.ANTHROPIC_API_KEY
        self.model   = cfg.CLAUDE_MODEL

    def detect_language(self, text: str) -> str:
        """Detect language from message text"""
        text_lower = text.lower().strip()
        # Simple heuristics
        if any(0x4E00 <= ord(c) <= 0x9FFF for c in text):
            return "zh"
        if any(0x3040 <= ord(c) <= 0x30FF for c in text):
            return "ja"
        if any(0x0E00 <= ord(c) <= 0x0E7F for c in text):
            return "th"
        if any(c in text for c in ["ă", "ơ", "ư", "đ", "ắ", "ế", "ứ"]):
            return "vi"
        malay_words = ["saya", "anda", "terima", "boleh", "kami", "awak", "bagaimana", "berapa"]
        if any(w in text_lower for w in malay_words):
            return "ms"
        filipino_words = ["po", "opo", "ako", "ikaw", "sige", "salamat", "magkano", "paano"]
        if any(w in text_lower for w in filipino_words):
            return "fil"
        return "en"

    def detect_intent(self, text: str) -> str:
        """Detect intent from message"""
        text_lower = text.lower()
        appointment_words = ["book", "appointment", "consult", "schedule", "meet", "预约", "咨询", "约", "时间"]
        if any(w in text_lower for w in appointment_words):
            return "appointment"
        service_words = ["price", "cost", "fee", "how much", "pricing", "价格", "费用", "收费", "多少钱"]
        if any(w in text_lower for w in service_words):
            return "pricing"
        human_words = ["human", "person", "agent", "staff", "人工", "真人", "客服"]
        if any(w in text_lower for w in human_words):
            return "handoff"
        return "enquiry"

    def generate_reply(self, user_message: str, history: list, language: str,
                       session_data: dict = None) -> str:
        """Call Claude API and return reply text"""
        system = SYSTEM_PROMPTS.get(language, SYSTEM_PROMPTS["en"])

        # Add session context if available
        if session_data:
            ctx = json.dumps(session_data, ensure_ascii=False)
            system += f"\n\nCurrent session context: {ctx}"

        # Build messages (keep last 10 for token efficiency)
        messages = []
        for h in history[-10:]:
            messages.append({"role": h["role"], "content": h["content"]})
        messages.append({"role": "user", "content": user_message})

        payload = json.dumps({
            "model":      self.model,
            "max_tokens": 600,
            "system":     system,
            "messages":   messages
        }).encode("utf-8")

        req = urllib.request.Request(
            self.API_URL,
            data=payload,
            headers={
                "x-api-key":         self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type":      "application/json"
            },
            method="POST"
        )
        try:
            r    = urllib.request.urlopen(req, timeout=30)
            data = json.loads(r.read())
            return data["content"][0]["text"].strip()
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            logger.error(f"Claude API error {e.code}: {body}")
            return self._fallback_reply(language)
        except Exception as e:
            logger.error(f"Claude call failed: {e}")
            return self._fallback_reply(language)

    def _fallback_reply(self, language: str) -> str:
        fallbacks = {
            "en":  "Sorry, I'm having a brief technical issue. Please try again or email us at admin@soonhoe.com.sg",
            "zh":  "抱歉，我遇到了技术问题。请稍后再试，或发邮件至 admin@soonhoe.com.sg",
            "ms":  "Maaf, saya mengalami masalah teknikal. Sila cuba lagi atau emel kami di admin@soonhoe.com.sg",
            "ja":  "申し訳ありません、技術的な問題が発生しました。後ほど再度お試しいただくか、admin@soonhoe.com.sg までご連絡ください。",
            "th":  "ขออภัย เกิดปัญหาทางเทคนิค กรุณาลองใหม่หรือส่งอีเมลมาที่ admin@soonhoe.com.sg",
            "vi":  "Xin lỗi, tôi gặp sự cố kỹ thuật. Vui lòng thử lại hoặc email chúng tôi tại admin@soonhoe.com.sg",
            "fil": "Paumanhin, may teknikal na problema. Pakisubukang muli o mag-email sa admin@soonhoe.com.sg",
        }
        return fallbacks.get(language, fallbacks["en"])
