from flask import Blueprint, render_template
# Xóa dòng import current_user nếu chưa làm login, để tránh lỗi
# from flask_login import current_user 

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def index():
    # Tạm thời bỏ current_user đi để chạy được đã
    return render_template('index.html')