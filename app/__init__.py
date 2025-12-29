import os
from flask import Flask
from .models import db

# 1. Import các Blueprint đã khai báo ở Bước 1
from .ai_logic import ai_bp
from .auth_routes import auth_bp
from .admin_routes import admin_bp
from .test_routes import test_bp
from .report_routes import report_bp

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')

    # 2. Cấu hình Database (Dùng đường dẫn tuyệt đối như đã fix)
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, '../database/app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'nhom1-bi-mat'

    db.init_app(app)

    # 3. ĐĂNG KÝ BLUEPRINT - Chia đường dẫn web
    app.register_blueprint(ai_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')    # Truy cập qua: /auth/login
    app.register_blueprint(admin_bp, url_prefix='/admin')  # Truy cập qua: /admin/dashboard
    app.register_blueprint(test_bp, url_prefix='/quiz')    # Truy cập qua: /quiz/quiz
    app.register_blueprint(report_bp, url_prefix='/report')# Truy cập qua: /report/view

    # Trang chủ mặc định
    @app.route('/')
    def index():
        return "<h1>Chào mừng đến với Hệ thống Ôn tập - Nhóm 1</h1><a href='/auth/login'>Đến trang Đăng nhập</a>"

    return app