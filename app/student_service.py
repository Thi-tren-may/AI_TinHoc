# app/student_service.py
import sqlite3
from werkzeug.security import generate_password_hash # Thư viện mã hóa mật khẩu

# 1. CẤU HÌNH KẾT NỐI DB (Riêng cho file này)
def get_db_connection():
    conn = sqlite3.connect('database/app.db')
    conn.row_factory = sqlite3.Row
    return conn

# 2. LẤY DANH SÁCH HỌC SINH
def get_all_students():
    conn = get_db_connection()
    # Chỉ lấy những tài khoản có Role là 'student', sắp xếp mới nhất lên đầu
    students = conn.execute("SELECT * FROM Users WHERE Role = 'student' ORDER BY Id DESC").fetchall()
    conn.close()
    return students

# 3. THÊM HỌC SINH MỚI
def add_new_student(username, password, grade):
    conn = get_db_connection()
    try:
        # Mã hóa mật khẩu trước khi lưu (Bắt buộc để bảo mật)
        hashed_pw = generate_password_hash(password)
        
        conn.execute("""
            INSERT INTO Users (Username, PasswordHash, Role, Grade)
            VALUES (?, ?, 'student', ?)
        """, (username, hashed_pw, grade))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Lỗi thêm học sinh: {e}")
        return False # Trả về False nếu lỗi (ví dụ trùng tên đăng nhập)
    finally:
        conn.close()

# 4. LẤY CHI TIẾT 1 HỌC SINH (Để hiển thị lên form sửa)
def get_student_by_id(user_id):
    conn = get_db_connection()
    student = conn.execute("SELECT * FROM Users WHERE Id = ?", (user_id,)).fetchone()
    conn.close()
    return student

# 5. CẬP NHẬT THÔNG TIN HỌC SINH
def update_student(user_id, username, grade, password=None):
    conn = get_db_connection()
    if password:
        # Nếu người dùng nhập pass mới -> Mã hóa và cập nhật
        hashed_pw = generate_password_hash(password)
        conn.execute("""
            UPDATE Users SET Username = ?, Grade = ?, PasswordHash = ? WHERE Id = ?
        """, (username, grade, hashed_pw, user_id))
    else:
        # Nếu để trống pass -> Chỉ cập nhật thông tin khác
        conn.execute("""
            UPDATE Users SET Username = ?, Grade = ? WHERE Id = ?
        """, (username, grade, user_id))
    
    conn.commit()
    conn.close()

# 6. XÓA HỌC SINH
def delete_student(user_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM Users WHERE Id = ?", (user_id,))
    conn.commit()
    conn.close()