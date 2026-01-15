from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models import db, Exam
from sqlalchemy import func

home_bp = Blueprint('home', __name__)

# --- 1. TRANG MẶC ĐỊNH (Redirect nếu đã đăng nhập) ---
@home_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home.student_index'))
    return render_template('index.html')

# --- 2. TRANG DASHBOARD HỌC SINH (Logic tính toán chuẩn) ---
@home_bp.route('/student')
@login_required
def student_index():
    # A. Tính TỔNG SỐ BÀI đã làm (Đếm trong Database)
    total_exams = Exam.query.filter_by(UserId=current_user.Id).count()

    # B. Tính ĐIỂM TRUNG BÌNH (Dùng hàm AVG của SQL)
    avg_result = db.session.query(func.avg(Exam.TotalScore)).filter_by(UserId=current_user.Id).scalar()
    # Nếu có điểm thì làm tròn 1 số lẻ, chưa có thì bằng 0
    avg_score = round(avg_result, 1) if avg_result else 0

    # C. Tính DANH HIỆU (Ranking)
    if avg_score >= 9.0:
        rank = "Chiến Thần 🏆"
    elif avg_score >= 8.0:
        rank = "Cao Thủ 💎"
    elif avg_score >= 6.5:
        rank = "Tinh Anh ⚔️"
    elif avg_score >= 5.0:
        rank = "Tập Sự 🛡️"
    elif total_exams == 0:
        rank = "Tân Binh (Chưa thi)"
    else:
        rank = "Cần Cố Gắng 💪"

    # D. Render giao diện (Gửi số liệu sang HTML)
    # QUAN TRỌNG: Đường dẫn file HTML phải chính xác là 'student/Indexstudent.html'
    return render_template('student/Indexstudent.html', 
                           total_exams=total_exams, 
                           avg_score=avg_score, 
                           rank=rank)