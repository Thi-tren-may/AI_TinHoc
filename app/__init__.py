import os
from flask import Flask
from .models import db

# 1. Import các Blueprint (Đã import admin_bp ở đây là ĐÚNG)
from .ai_logic import ai_bp
from .auth_routes import auth_bp
from .admin_routes import admin_bp
from .test_routes import test_bp
from .report_routes import report_bp

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')

    # 2. Cấu hình Database
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, '../database/app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'nhom1-bi-mat'

    db.init_app(app)

    # 3. ĐĂNG KÝ BLUEPRINT
    app.register_blueprint(ai_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # SỬA DÒNG NÀY: Chỉ đăng ký tên, không thêm prefix nữa (vì file kia có rồi)
    app.register_blueprint(admin_bp)
    
    app.register_blueprint(test_bp, url_prefix='/quiz')
    app.register_blueprint(report_bp, url_prefix='/report')

    # Trang chủ
    @app.route('/')
    def index():
        return "<h1>Chào mừng - Nhóm 1</h1><a href='/admin/questions'>Vào trang Admin (S3)</a>"

    return app