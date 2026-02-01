from flask import render_template, request, jsonify
from flask_login import login_required, current_user
from ..services.gemini_service import reply as gemini_reply

def register(app):

    @app.route("/chatbot", methods=["GET"])
    @login_required
    def chatbot():
        return render_template("chatbot.html")

    @app.route("/chat", methods=["POST"])
    @login_required
    def chat_compat():
        message = (request.form.get("message") or "").strip()
        return jsonify({"response": gemini_reply(message, role=getattr(current_user, "role", "seeker"),
            fallback_name=(current_user.name or "there").split()[0])})

    @app.route("/api/chatbot", methods=["POST"])
    @login_required
    def api_chatbot():
        data = request.get_json(silent=True) or {}
        user_msg = (data.get("message") or "").strip()
        return jsonify({"reply": gemini_reply(user_msg, role=getattr(current_user, "role", "seeker"),
            fallback_name=(current_user.name or "there").split()[0])})
