from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

home_bp = Blueprint('home', __name__)

# --- BỔ SUNG ĐOẠN NÀY ĐỂ HẾT LỖI 404 ---
@home_bp.route('/')
def index():
    # Nếu học sinh đã đăng nhập rồi, tự động chuyển vào dashboard
    if current_user.is_authenticated:
        return redirect(url_for('home.student_index'))
    
    # Nếu chưa đăng nhập, trả về trang giới thiệu chung index.html
    # (File này nằm trực tiếp trong thư mục templates/)
    return render_template('index.html')

# --- TRANG STUDENT CỦA BẠN (GIỮ NGUYÊN) ---
@home_bp.route('/student')
@login_required
def student_index():
    stats = {
        'total_exams': 0,
        'avg_score': 0,
        'rank': '---'
    }
    return render_template('student/Indexstudent.html', stats=stats)