import sqlite3
from flask import Blueprint, render_template, request, redirect, url_for, session, g
from app.grading import tinh_diem # Import hàm tính điểm bạn vừa viết

# Tạo Blueprint tên là 'test'
test_bp = Blueprint('test', __name__)

# Cấu hình đường dẫn DB (Sửa lại cho đúng đường dẫn máy bạn nếu cần)
DB_PATH = 'database/app.db'

def get_db_connection():
    """Hàm phụ trợ để kết nối Database"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # Để lấy dữ liệu dạng Dictionary (key-value)
    return conn

# 1. Route hiển thị bài thi
@test_bp.route('/lam-bai-thi')
def do_test():
    # --- GIẢ LẬP USER ID (Nếu S5 chưa xong Login thì dùng dòng này để test) ---
    session['user_id'] = 2 
    # -------------------------------------------------------------------------
    
    if 'user_id' not in session:
        return "Bạn chưa đăng nhập! (Bảo S5 làm lẹ lên hoặc bỏ comment dòng giả lập trong code S2)"

    conn = get_db_connection()
    
    # Lấy ngẫu nhiên 20 câu hỏi (Logic tạm thời thay cho S3)
    # ORDER BY RANDOM() LIMIT 20 là cách lấy ngẫu nhiên trong SQLite
    questions = conn.execute('SELECT * FROM Exercises ORDER BY RANDOM() LIMIT 20').fetchall()
    
    conn.close()

    # Render giao diện và truyền danh sách câu hỏi qua
    return render_template('quiz/do_test.html', questions=questions)

# 2. Route xử lý nộp bài
@test_bp.route('/nop-bai', methods=['POST'])
def submit_test():
    if 'user_id' not in session:
        return redirect(url_for('auth.login')) # Giả sử S5 đặt tên route là auth.login

    user_id = session['user_id']
    
    # Lấy dữ liệu từ Form học sinh gửi lên
    # request.form sẽ có dạng: {'101': 'A', '102': 'C'...} với key là ID câu hỏi
    data_form = request.form.to_dict()
    
    # Lấy lại danh sách câu hỏi từ DB dựa trên các ID mà form gửi về để chấm
    # (Lý do: Để đảm bảo bảo mật, phải lấy đáp án đúng từ DB so sánh)
    question_ids = list(data_form.keys())
    
    if not question_ids:
        return "Bạn chưa chọn câu nào cả!"

    # Tạo chuỗi query động: SELECT * FROM Exercises WHERE Id IN (1, 5, 9...)
    placeholders = ','.join('?' * len(question_ids))
    query = f'SELECT * FROM Exercises WHERE Id IN ({placeholders})'
    
    conn = get_db_connection()
    questions_db = conn.execute(query, question_ids).fetchall()

    # --- GỌI HÀM CHẤM ĐIỂM (Của file grading.py) ---
    diem_so, so_cau_dung, chi_tiet_ket_qua = tinh_diem(questions_db, data_form)

    # --- LƯU VÀO DATABASE (Phần quan trọng nhất) ---
    cursor = conn.cursor()

    # 1. Lưu vào bảng Exams (Lịch sử tổng quát)
    # TopicId tạm để số 1 (sau này S3 sẽ truyền topic vào)
    cursor.execute('''
        INSERT INTO Exams (UserId, TopicId, TotalScore)
        VALUES (?, ?, ?)
    ''', (user_id, 1, diem_so))
    
    # Lấy ID của bài thi vừa tạo để lưu vào bảng chi tiết
    exam_id = cursor.lastrowid 

    # 2. Lưu vào bảng StudentResults (Chi tiết từng câu đúng/sai)
    for item in chi_tiet_ket_qua:
        cursor.execute('''
            INSERT INTO StudentResults (ExamId, ExerciseId, SelectedOption, IsCorrect)
            VALUES (?, ?, ?, ?)
        ''', (exam_id, item['exercise_id'], item['selected_option'], item['is_correct']))

    conn.commit()
    conn.close()

    # Chuyển hướng sang trang kết quả của S4 (Report)
    # S4 cần tạo route tên là 'view_result' nhận vào exam_id
    return f"Nộp bài thành công! Điểm: {diem_so}. (Chờ S4 làm trang kết quả để chuyển hướng)"
    # Khi S4 làm xong, đổi dòng trên thành:
    # return redirect(url_for('report.view_result', exam_id=exam_id))