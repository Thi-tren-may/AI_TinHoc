from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .  models import db, User
import re

auth_bp = Blueprint('auth', __name__)

# ==========================
# LOGIN
# ==========================
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST': 
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(Username=username).first()

        if user and check_password_hash(user.PasswordHash, password):
            login_user(user)  # đăng nhập Flask-Login
            flash('Đăng nhập thành công!', 'success')

            if user.Role == 'admin':
                return redirect(url_for('admin.manage_questions'))
            else:
                # ← SỬA DÒNG NÀY:  Chuyển đến trang student thay vì profile
                return redirect(url_for('home.student_index'))

        flash('Tên đăng nhập hoặc mật khẩu không đúng.', 'error')

    return render_template('login.html')


# ==========================
# REGISTER (STUDENT)
# ==========================
@auth_bp. route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        grade = request.form.get('grade')

        # Kiểm tra trống
        if not username or not password:
            flash('Vui lòng nhập đầy đủ thông tin. ', 'error')
            return redirect(url_for('auth.register'))

        # Kiểm tra độ dài
        if len(password) < 6:
            flash('Mật khẩu phải có ít nhất 6 ký tự.', 'error')
            return redirect(url_for('auth.register'))

        # Kiểm tra chữ hoa
        if not re. search(r'[A-Z]', password):
            flash('Mật khẩu phải chứa ít nhất 1 chữ cái viết hoa (A-Z).', 'error')
            return redirect(url_for('auth.register'))

        # Kiểm tra chữ số
        if not re.search(r'\d', password):
            flash('Mật khẩu phải chứa ít nhất 1 chữ số (0-9).', 'error')
            return redirect(url_for('auth.register'))

        # Kiểm tra user tồn tại
        existing_user = User.query.filter_by(Username=username).first()
        if existing_user: 
            flash('Tên đăng nhập đã tồn tại.', 'error')
            return redirect(url_for('auth.register'))

        # Tạo user mới
        new_user = User(
            Username=username,
            PasswordHash=generate_password_hash(password),
            Role='student',
            Grade=int(grade) if grade else 10
        )

        db.session. add(new_user)
        db.session.commit()

        flash('Đăng ký thành công! Vui lòng đăng nhập. ', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


# ==========================
# LOGOUT
# ==========================
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Bạn đã đăng xuất.', 'info')
    return redirect(url_for('auth.login'))


# ==========================
# PROFILE (STUDENT) – chỉ hiển thị thông tin
# ==========================
@auth_bp.route('/profile')
@login_required
def profile():
    # ← SỬA:  Thêm user=current_user để tránh lỗi 'user' is undefined
    return render_template('profile.html', user=current_user)