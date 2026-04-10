"""
Conversation Manager — state machine
Stages: greeting → language_select → main_menu → enquiry → appointment → lead_capture → handoff
"""
import logging
from .config import Config
from .database import Database
from .whatsapp import WhatsAppClient
from .ai_engine import AIEngine

logger = logging.getLogger(__name__)

# ── Greeting messages ──────────────────────────────────────────────────────
GREETINGS = {
    "en":  "👋 Hello! I'm *Soo*, the AI assistant for *Soon Hoe Group* & *GAIAGenX*.\n\nI can help you with:\n• Immigration & PR applications 🏠\n• Company setup in Singapore 🏢\n• Education & real estate 📚\n• AI enterprise solutions 🤖\n• Accounting, tax & audit 📊\n\nHow can I help you today?",
    "zh":  "👋 您好！我是*顺和集团*和*GAIAGenX*的AI助理*Soo*。\n\n我可以帮您：\n• 移民及PR申请 🏠\n• 新加坡公司注册 🏢\n• 教育及地产咨询 📚\n• AI企业解决方案 🤖\n• 会计、税务及审计 📊\n\n请问有什么可以帮您？",
    "ms":  "👋 Hai! Saya *Soo*, pembantu AI untuk *Soon Hoe Group* & *GAIAGenX*.\n\nSaya boleh membantu anda:\n• Permohonan imigresen & PR 🏠\n• Penubuhan syarikat di Singapura 🏢\n• Pendidikan & hartanah 📚\n• Penyelesaian AI perusahaan 🤖\n• Perakaunan, cukai & audit 📊\n\nBagaimana saya boleh membantu anda hari ini?",
    "ja":  "👋 こんにちは！私は*顺和グループ*と*GAIAGenX*のAIアシスタント*Soo*です。\n\nご相談内容：\n• 移民・PR申請 🏠\n• シンガポール会社設立 🏢\n• 教育・不動産 📚\n• AI企業ソリューション 🤖\n• 会計・税務・監査 📊\n\n本日はどのようなご用件でしょうか？",
    "th":  "👋 สวัสดีครับ/ค่ะ! ผม/หนูชื่อ *Soo* ผู้ช่วย AI ของ *Soon Hoe Group* และ *GAIAGenX*\n\nช่วยคุณได้เรื่อง:\n• วีซ่าและ PR 🏠\n• จัดตั้งบริษัทในสิงคโปร์ 🏢\n• การศึกษาและอสังหาริมทรัพย์ 📚\n• โซลูชัน AI สำหรับองค์กร 🤖\n• บัญชี ภาษี และตรวจสอบ 📊\n\nวันนี้ต้องการความช่วยเหลืออะไรคะ/ครับ?",
    "vi":  "👋 Xin chào! Tôi là *Soo*, trợ lý AI của *Soon Hoe Group* và *GAIAGenX*.\n\nTôi có thể giúp bạn:\n• Visa & PR Singapore 🏠\n• Thành lập công ty tại Singapore 🏢\n• Giáo dục & bất động sản 📚\n• Giải pháp AI doanh nghiệp 🤖\n• Kế toán, thuế & kiểm toán 📊\n\nHôm nay tôi có thể giúp gì cho bạn?",
    "fil": "👋 Kamusta! Ako si *Soo*, ang AI assistant ng *Soon Hoe Group* at *GAIAGenX*.\n\nMatutulungan kita sa:\n• Immigration at PR applications 🏠\n• Pagtatayo ng kumpanya sa Singapore 🏢\n• Edukasyon at real estate 📚\n• AI enterprise solutions 🤖\n• Accounting, buwis at audit 📊\n\nPaano kita matutulungan ngayon?",
}

HANDOFF_MSG = {
    "en":  "I'll connect you with one of our consultants shortly. You can also reach us directly:\n📧 admin@soonhoe.com.sg\n🌐 www.soonhoe.com.sg\n\nOur team will be in touch within 1 business day. Thank you! 🙏",
    "zh":  "我将为您转接人工顾问。您也可以直接联系我们：\n📧 admin@soonhoe.com.sg\n🌐 www.soonhoe.com.sg\n\n我们的团队将在1个工作日内与您联系。感谢！🙏",
    "ms":  "Saya akan menghubungkan anda dengan salah seorang perunding kami. Anda juga boleh menghubungi kami terus:\n📧 admin@soonhoe.com.sg\n🌐 www.soonhoe.com.sg\n\nPasukan kami akan menghubungi anda dalam 1 hari perniagaan. Terima kasih! 🙏",
    "ja":  "担当コンサルタントにおつなぎします。直接ご連絡もいただけます：\n📧 admin@soonhoe.com.sg\n🌐 www.soonhoe.com.sg\n\n1営業日以内にご連絡いたします。ありがとうございます！🙏",
    "th":  "ฉันจะเชื่อมต่อคุณกับที่ปรึกษาของเรา คุณยังสามารถติดต่อเราโดยตรงได้ที่:\n📧 admin@soonhoe.com.sg\n🌐 www.soonhoe.com.sg\n\nทีมของเราจะติดต่อกลับภายใน 1 วันทำการ ขอบคุณ! 🙏",
    "vi":  "Tôi sẽ kết nối bạn với chuyên viên tư vấn. Bạn cũng có thể liên hệ trực tiếp:\n📧 admin@soonhoe.com.sg\n🌐 www.soonhoe.com.sg\n\nĐội ngũ sẽ liên hệ trong vòng 1 ngày làm việc. Cảm ơn! 🙏",
    "fil": "Ikikonekta kita sa aming consultant. Maaari ka ring makipag-ugnayan nang direkta:\n📧 admin@soonhoe.com.sg\n🌐 www.soonhoe.com.sg\n\nMakikipag-ugnayan ang aming team sa loob ng 1 araw ng trabaho. Salamat! 🙏",
}

APPT_CONFIRM = {
    "en":  "✅ *Consultation Request Received!*\n\nDetails:\n• *Name:* {name}\n• *Interest:* {interest}\n• *Preferred time:* {time}\n• *Contact:* {contact}\n\nOur team will confirm your appointment within 1 business day.\n📧 admin@soonhoe.com.sg",
    "zh":  "✅ *咨询预约已收到！*\n\n详情：\n• *姓名：* {name}\n• *咨询方向：* {interest}\n• *希望时间：* {time}\n• *联系方式：* {contact}\n\n我们的团队将在1个工作日内确认您的预约。\n📧 admin@soonhoe.com.sg",
}
for lang in ["ms","ja","th","vi","fil"]:
    APPT_CONFIRM[lang] = APPT_CONFIRM["en"]

ASK_NAME = {
    "en":"Great! Could you share your *name* so I can address you properly?",
    "zh":"好的！请问您的*姓名*是？",
    "ms":"Baik! Boleh kongsikan *nama* anda?",
    "ja":"了解しました。お*名前*を教えていただけますか？",
    "th":"ได้เลย! ขอทราบ*ชื่อ*ของคุณด้วยนะคะ/ครับ",
    "vi":"Tuyệt! Bạn có thể cho tôi biết *tên* của bạn không?",
    "fil":"Sige! Maari bang ibahagi ang iyong *pangalan*?",
}
ASK_TIME = {
    "en":"What's your *preferred date and time* for the consultation? (e.g. Tuesday 3pm SGT)\nOur hours: Mon–Fri 9am–6pm SGT",
    "zh":"您希望什么*时间*进行咨询？（例如：周二下午3点 SGT）\n办公时间：周一至周五 9am–6pm SGT",
    "ms":"Apakah *tarikh dan masa* yang sesuai untuk anda? (cth: Selasa 3ptg SGT)\nWaktu pejabat: Isnin–Jumaat 9pg–6ptg SGT",
    "ja":"ご都合のよい*日時*を教えてください（例：火曜 午後3時 SGT）\n営業時間：月〜金 9am–6pm SGT",
    "th":"คุณสะดวก*วันและเวลา*ใดสำหรับการนัดหมาย? (เช่น อังคาร 15:00 SGT)\nเวลาทำการ: จันทร์–ศุกร์ 9:00–18:00 SGT",
    "vi":"*Ngày và giờ* nào phù hợp với bạn? (vd: Thứ Ba 3 giờ chiều SGT)\nGiờ làm việc: T2–T6 9am–6pm SGT",
    "fil":"Anong *petsa at oras* ang maginhawa para sa iyo? (hal: Martes 3pm SGT)\nOras ng trabaho: Lunes–Biyernes 9am–6pm SGT",
}
ASK_CONTACT = {
    "en":"And your *email address* for confirmation?",
    "zh":"请提供您的*电邮地址*以便确认预约。",
    "ms":"Dan *alamat emel* anda untuk pengesahan?",
    "ja":"確認のため*メールアドレス*を教えてください。",
    "th":"*อีเมล*ของคุณสำหรับยืนยันการนัดหมาย?",
    "vi":"*Email* của bạn để xác nhận?",
    "fil":"At ang iyong *email address* para sa kumpirmasyon?",
}


class ConversationManager:
    def __init__(self, cfg: Config, db: Database, wa: WhatsAppClient):
        self.cfg = cfg
        self.db  = db
        self.wa  = wa
        self.ai  = AIEngine(cfg)

    def handle(self, msg: dict, contact: dict):
        """Main entry point for incoming message"""
        msg_type = msg.get("type", "")
        phone    = msg.get("from", "")
        name     = contact.get("profile", {}).get("name", "")

        # Extract text content
        if msg_type == "text":
            text = msg["text"]["body"].strip()
        elif msg_type == "interactive":
            inter = msg.get("interactive", {})
            if inter.get("type") == "button_reply":
                text = inter["button_reply"]["id"]
            elif inter.get("type") == "list_reply":
                text = inter["list_reply"]["id"]
            else:
                text = ""
        else:
            # Audio, image, etc — acknowledge
            self.wa.send_text(phone, "📎 I can only process text messages for now. Please type your question!")
            return

        if not text or not phone:
            return

        logger.info(f"MSG from {phone}: {text[:80]}")

        # Save incoming message
        self.db.add_message(phone, "in", text)

        # Get or create conversation
        conv = self.db.get_conversation(phone)
        stage = conv.get("stage", "greeting")

        # Session timeout → reset
        if conv and self.db.is_session_expired(phone, self.cfg.SESSION_TIMEOUT):
            logger.info(f"Session expired for {phone}, resetting")
            self.db.set_stage(phone, "greeting")
            self.db.clear_history(phone)
            stage = "greeting"

        # Detect or use stored language
        if not conv.get("language"):
            lang = self.ai.detect_language(text)
            self.db.upsert_conversation(phone, name=name, language=lang)
        else:
            lang = conv.get("language", "en")

        # Store name if we have it
        if name and not conv.get("name"):
            self.db.upsert_conversation(phone, name=name)

        # ── Dispatch to stage handler ──────────────────────────────────────
        handler = {
            "greeting":     self._handle_greeting,
            "main_menu":    self._handle_ai,
            "enquiry":      self._handle_ai,
            "appointment_interest": self._handle_appt_interest,
            "appointment_name":     self._handle_appt_name,
            "appointment_time":     self._handle_appt_time,
            "appointment_contact":  self._handle_appt_contact,
            "handoff":      self._handle_handoff,
        }.get(stage, self._handle_ai)

        handler(phone, text, lang, name)

    # ── Stage handlers ────────────────────────────────────────────────────
    def _handle_greeting(self, phone, text, lang, name):
        greeting = GREETINGS.get(lang, GREETINGS["en"])
        if name:
            greeting = greeting.replace("Hello!", f"Hello, {name}!").replace("您好！", f"您好，{name}！")
        self._send(phone, greeting)
        self.db.set_stage(phone, "enquiry")
        # Record lead
        self.db.upsert_lead(phone, name=name, language=lang, stage="contacted")

    def _handle_ai(self, phone, text, lang, name):
        # Check for appointment intent
        intent = self.ai.detect_intent(text)

        if intent == "appointment":
            self.db.set_stage(phone, "appointment_interest")
            self._handle_appt_interest(phone, text, lang, name)
            return

        if intent == "handoff":
            self.db.set_stage(phone, "handoff")
            self._handle_handoff(phone, text, lang, name)
            return

        # Regular AI enquiry
        history = self.db.get_history(phone)
        session = self.db.get_session_data(phone)
        reply   = self.ai.generate_reply(text, history, lang, session)
        self._send(phone, reply)
        self.db.upsert_lead(phone, interest=text[:100], stage="enquiring")

    def _handle_appt_interest(self, phone, text, lang, name):
        """Ask which service area they want to consult about"""
        self.wa.send_buttons(
            phone,
            body={
                "en": "Which service would you like to book a consultation for?",
                "zh": "您希望咨询哪方面的服务？",
                "ms": "Perkhidmatan mana yang anda ingin buat temujanji?",
                "ja": "どのサービスについてご相談されますか？",
                "th": "คุณต้องการนัดหมายเรื่องบริการใด?",
                "vi": "Bạn muốn đặt lịch tư vấn về dịch vụ nào?",
                "fil": "Anong serbisyo ang gusto mong i-konsulta?",
            }.get(lang, "Which service would you like to book a consultation for?"),
            buttons=[
                {"id": "appt_immigration", "title": "🏠 Immigration/PR"},
                {"id": "appt_business",    "title": "🏢 Business Setup"},
                {"id": "appt_other",       "title": "📋 Other Services"},
            ]
        )
        self.db.set_stage(phone, "appointment_name")

    def _handle_appt_name(self, phone, text, lang, name):
        # Save their interest selection if it's a button reply
        if text.startswith("appt_"):
            interest_map = {
                "appt_immigration": "Immigration & PR",
                "appt_business":    "Business Setup",
                "appt_other":       "Other Services"
            }
            interest = interest_map.get(text, "General")
            session = self.db.get_session_data(phone)
            session["appt_interest"] = interest
            self.db.set_session_data(phone, session)

        # Ask for name
        if name:
            # We already have the name
            session = self.db.get_session_data(phone)
            session["appt_name"] = name
            self.db.set_session_data(phone, session)
            ask = ASK_TIME.get(lang, ASK_TIME["en"])
            self._send(phone, ask)
            self.db.set_stage(phone, "appointment_time")
        else:
            ask = ASK_NAME.get(lang, ASK_NAME["en"])
            self._send(phone, ask)

    def _handle_appt_time(self, phone, text, lang, name):
        # Save name if this is the name reply
        conv = self.db.get_conversation(phone)
        session = self.db.get_session_data(phone)

        if "appt_name" not in session:
            session["appt_name"] = text
            self.db.set_session_data(phone, session)
            ask = ASK_TIME.get(lang, ASK_TIME["en"])
            self._send(phone, ask)
            return

        # Save preferred time
        session["appt_time"] = text
        self.db.set_session_data(phone, session)
        ask = ASK_CONTACT.get(lang, ASK_CONTACT["en"])
        self._send(phone, ask)
        self.db.set_stage(phone, "appointment_contact")

    def _handle_appt_contact(self, phone, text, lang, name):
        session = self.db.get_session_data(phone)
        session["appt_contact"] = text
        self.db.set_session_data(phone, session)

        # Confirm booking
        appt_name    = session.get("appt_name", name or "")
        appt_interest = session.get("appt_interest", "General Consultation")
        appt_time    = session.get("appt_time", "TBD")
        appt_contact = session.get("appt_contact", text)

        tmpl = APPT_CONFIRM.get(lang, APPT_CONFIRM["en"])
        confirm = tmpl.format(
            name=appt_name, interest=appt_interest,
            time=appt_time, contact=appt_contact
        )
        self._send(phone, confirm)

        # Save to leads DB
        self.db.upsert_lead(phone,
            name=appt_name, language=lang,
            interest=appt_interest,
            notes=f"Appt: {appt_time} | Contact: {appt_contact}",
            stage="appointment_booked"
        )

        # Reset to main
        self.db.set_stage(phone, "enquiry")
        self.db.set_session_data(phone, {})

    def _handle_handoff(self, phone, text, lang, name):
        msg = HANDOFF_MSG.get(lang, HANDOFF_MSG["en"])
        self._send(phone, msg)
        self.db.upsert_lead(phone, stage="handoff_requested")
        self.db.set_stage(phone, "enquiry")

    def _send(self, phone: str, text: str):
        result = self.wa.send_text(phone, text)
        self.db.add_message(phone, "out", text)
        if "error" in result:
            logger.error(f"Send failed to {phone}: {result}")
