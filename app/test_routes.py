from flask import Blueprint, render_template, request, redirect, url_for, session
from flask_login import login_required, current_user # <--- IMPORT QUAN TRỌNG
from app import db
from sqlalchemy import text
from datetime import datetime

from app.question_service import generate_exam_questions
test_bp = Blueprint('test', __name__)

# --- 1. TRANG CHỌN CHỦ ĐỀ ---
@test_bp.route('/chon-chu-de')
@login_required  # <--- Bắt buộc đăng nhập
def select_topic():
    try:
        sql = text("SELECT Id, Name FROM Topics WHERE ParentId IS NULL AND IsActive = 1")
        result = db.session.execute(sql).fetchall()
        
        topics = [{'Id': row.Id, 'Name': row.Name} for row in result]
        return render_template('quiz/select_topic.html', topics=topics)
    except Exception as e:
        return f"Lỗi lấy chủ đề: {str(e)}"

# --- 2. TRANG LÀM BÀI ---
@test_bp.route('/lam-bai-thi', methods=['GET', 'POST'])
def do_test():
    # Giả lập & Check Login (Giữ nguyên)
    if 'user_id' not in session: session['user_id'] = 2 
    if 'user_id' not in session: return "Lỗi: Chưa đăng nhập"

    if request.method == 'GET':
        return redirect(url_for('test.select_topic'))
    
    if request.method == 'POST':
        selected_ids = request.form.getlist('topics')
        
        # --- GỌI THUẬT TOÁN TỪ FILE SERVICE ---
        # Code cũ dài dòng đã được thay thế bằng 1 dòng này:
        raw_questions = generate_exam_questions(selected_ids, total_questions=20)
        # --------------------------------------

        if not raw_questions:
            return "Không tạo được đề thi (Có thể do lỗi DB hoặc không đủ câu hỏi)."

        # Chuyển đổi dữ liệu để hiển thị (Mapping key)
        # Vì hàm service trả về dict sẵn rồi, ta chỉ cần map lại cho chắc chắn
        questions = []
        for q in raw_questions:
            questions.append({
                'Id': q['Id'],
                'Content': q['Content'],
                'OptionA': q['OptionA'], 
                'OptionB': q['OptionB'],
                'OptionC': q['OptionC'], 
                'OptionD': q['OptionD']
            })
        
        # Lưu đáp án đúng vào Session
        correct_answers = {str(q['Id']): q['CorrectOption'] for q in raw_questions}
        session['exam_answers'] = correct_answers
        
        return render_template('quiz/do_test.html', questions=questions)

# --- 3. NỘP BÀI & CHẤM ĐIỂM (Đã sửa để dùng User thật) ---
@test_bp.route('/nop-bai', methods=['POST'])
@login_required # <--- Bắt buộc đăng nhập
def submit_test():
    # 1. Kiểm tra session đề thi
    if 'exam_answers' not in session:
        return "Lỗi: Phiên làm bài đã hết hạn. Hãy thử lại."

    correct_answers = session['exam_answers']
    user_answers = request.form.to_dict()
    
    # 2. Tính điểm
    score = 0
    total_questions = len(correct_answers)
    details = []

    for q_id, correct_opt in correct_answers.items():
        user_opt = user_answers.get(q_id)
        is_correct = (user_opt == correct_opt)
        
        if is_correct:
            score += (10 / total_questions) if total_questions > 0 else 0
            
        details.append({
            'ExerciseId': q_id,
            'SelectedOption': user_opt,
            'IsCorrect': 1 if is_correct else 0
        })
    
    final_score = round(score, 2)

    # 3. Lưu vào Database (QUAN TRỌNG: SỬA LẠI ĐOẠN NÀY)
    # 4. Lưu vào Database (Dùng SQLAlchemy của Code mới)
    try:
        user_id = current_user.Id
        
        # 1. Lấy thời gian hiện tại
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
        
        # 2. [SỬA LỖI QUAN TRỌNG] Thêm cột CreatedAt vào câu lệnh INSERT
        # :c là chỗ điền thời gian
        sql_exam = text("INSERT INTO Exams (UserId, TopicId, TotalScore, CreatedAt) VALUES (:u, 1, :s, :c)")
        
        # 3. Truyền biến now_str vào tham số 'c'
        result = db.session.execute(sql_exam, {'u': user_id, 's': final_score, 'c': now_str})
        db.session.commit()
        
        exam_id = result.lastrowid # Lấy ID bài thi vừa tạo
        
        # B. Lưu bảng StudentResults (Chi tiết từng câu)
        for d in details:
            sql_detail = text("""
                INSERT INTO StudentResults (ExamId, ExerciseId, SelectedOption, IsCorrect) 
                VALUES (:eid, :exid, :opt, :corr)
            """)
            db.session.execute(sql_detail, {
                'eid': exam_id,
                'exid': d['ExerciseId'],
                'opt': d['SelectedOption'],
                'corr': d['IsCorrect']
            })
        db.session.commit()

        # Chuyển hướng sang trang kết quả của S4
        return redirect(url_for('report.view_result', exam_id=exam_id))

    except Exception as e:
        db.session.rollback()
        return f"Lỗi lưu điểm vào DB: {str(e)}"