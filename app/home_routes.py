from flask import Blueprint, render_template, redirect, url_for, flash
# Xóa dòng import current_user nếu chưa làm login, để tránh lỗi
# from flask_login import current_user 
from flask_login import login_required, current_user

home_bp = Blueprint('home', __name__)



# 3. TRANG STUDENT - THÊM MỚI
@home_bp.route('/student')
@login_required
def student_index():
    stats = {
        'total_exams': 0,
        'avg_score': 0,
        'rank': '---'
    }
    return render_template('student/Indexstudent.html', stats=stats)