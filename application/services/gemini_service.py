import os, logging
logger = logging.getLogger(__name__)
GEMINI_READY = False
GEMINI_MODEL = None

try:
    import google.generativeai as genai
    _api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if _api_key:
        genai.configure(api_key=_api_key)
        GEMINI_MODEL = genai.GenerativeModel("gemini-1.5-flash")
        GEMINI_READY = True
except Exception:
    GEMINI_READY = False

def reply(user_msg: str, role: str, fallback_name="there") -> str:
    if not user_msg:
        return "Say something and I’ll try to help 😊"
    if GEMINI_READY:
        try:
            sys_prompt = (
                "You are JobMatch's assistant. Be concise, helpful, actionable. "
                f"User role: {role}. If asked for steps, give short bullet points."
            )
            full_prompt = f"{sys_prompt}\n\nUser: {user_msg}\nAssistant:"
            result = GEMINI_MODEL.generate_content(full_prompt)
            text = (getattr(result, 'text', '') or '').strip()
            if text:
                return text
        except Exception:
            logger.exception("Gemini error")
    low = user_msg.lower()
    if "hello" in low or "hi" in low: return f"Hey {fallback_name}! How can I help you today?"
    if "apply" in low: return "Open **Applications**, pick a job, and click **Apply**."
    if "status" in low: return "Check your **Dashboard** tabs: Accepted / Rejected / Under Review."
    if "post" in low and "job" in low: return "As an employer, go to **Dashboard → Post a Job**."
    if "profile" in low: return "Open **Profile** to view/edit details. Password changes are in the Password tab."
    return "Try asking about *applications*, *status*, *posting jobs*, *resources*, or *profile*."
