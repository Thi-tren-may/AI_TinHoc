import os
from flask import Flask
from .models import db

# 1. Import các Blueprint
from .ai_logic import ai_bp
from .auth_routes import auth_bp
from .admin_routes import admin_bp
from .test_routes import test_bp
from .report_routes import report_bp
from .home_routes import home_bp  # Import blueprint trang chủ của S4

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')

    # 2. Cấu hình Database
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, '../database/app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'nhom1-bi-mat'

    db.init_app(app)

    # 3. ĐĂNG KÝ BLUEPRINT
    
    # Blueprint của AI và Auth
    app.register_blueprint(ai_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Blueprint Admin (Cập nhật theo develop: Bỏ prefix ở đây)
    app.register_blueprint(admin_bp)
    
    # Blueprint của Test và Report
    app.register_blueprint(test_bp, url_prefix='/quiz')
    app.register_blueprint(report_bp, url_prefix='/report')
    
    # Blueprint TRANG CHỦ (Của S4 - QUAN TRỌNG)
    # Không cần url_prefix vì nó là trang gốc (/)
    app.register_blueprint(home_bp) 

    # (Đã xóa đoạn @app.route('/') cũ để tránh xung đột với home_bp)

    return app