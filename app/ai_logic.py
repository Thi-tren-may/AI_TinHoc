from flask import Blueprint, render_template, request

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/')
def index():
    # Đây là trang chủ chính của cả dự án
    return render_template('index.html')

@ai_bp.route('/chat-ai', methods=['POST'])
def chat_ai():
    # S1 sẽ viết logic kết nối Gemini AI ở đây
    return {"reply": "Tôi là trợ lý AI của nhóm 1, tôi sẽ giúp bạn học tập!"}