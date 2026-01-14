from flask import Blueprint, render_template, request, redirect, url_for, session
from app import db
from sqlalchemy import text

test_bp = Blueprint('test', __name__)

# --- 1. TRANG CHỌN CHỦ ĐỀ (Giữ nguyên từ code mới của bạn) ---
@test_bp.route('/chon-chu-de')
def select_topic():
    try:
        # Lấy các chủ đề lớn (ParentId IS NULL)
        sql = text("SELECT Id, Name FROM Topics WHERE ParentId IS NULL AND IsActive = 1")
        result = db.session.execute(sql).fetchall()
        
        topics = [{'Id': row.Id, 'Name': row.Name} for row in result]
        return render_template('quiz/select_topic.html', topics=topics)
    except Exception as e:
        return f"Lỗi lấy chủ đề: {str(e)}"

# --- 2. TRANG LÀM BÀI (Hợp nhất: Thêm giả lập User & Check Login) ---
@test_bp.route('/lam-bai-thi', methods=['GET', 'POST'])
def do_test():
    # [TỪ CODE CŨ] Giả lập User ID để bạn test (nếu chưa có module Login)
    if 'user_id' not in session:
        session['user_id'] = 2  # ID giả định
    
    # Check login
    if 'user_id' not in session:
         return "Lỗi: Bạn chưa đăng nhập (Session trống)."

    if request.method == 'GET':
        return redirect(url_for('test.select_topic'))
    
    if request.method == 'POST':
        selected_ids = request.form.getlist('topics')
        
        try:
            if not selected_ids:
                sql = text("SELECT * FROM Exercises ORDER BY RANDOM() LIMIT 20")
                result = db.session.execute(sql).fetchall()
            else:
                # Logic lấy câu hỏi theo chủ đề Cha/Con (Giữ nguyên từ code mới)
                placeholders = ','.join([f':id{i}' for i in range(len(selected_ids))])
                query = f"""
                SELECT e.* FROM Exercises e
                JOIN Topics t ON e.TopicId = t.Id
                WHERE t.Id IN ({placeholders}) OR t.ParentId IN ({placeholders})
                ORDER BY RANDOM() LIMIT 20
                """
                params = {f'id{i}': topic_id for i, topic_id in enumerate(selected_ids)}
                result = db.session.execute(text(query), params).fetchall()

            # Map dữ liệu ra list
            questions = []
            for row in result:
                questions.append({
                    'Id': row.Id,
                    'Content': row.Content,
                    'OptionA': row.OptionA, 'OptionB': row.OptionB,
                    'OptionC': row.OptionC, 'OptionD': row.OptionD
                })
            
            # [QUAN TRỌNG] Lưu đáp án đúng vào Session để chấm điểm sau này
            correct_answers = {str(row.Id): row.CorrectOption for row in result}
            session['exam_answers'] = correct_answers
            
            return render_template('quiz/do_test.html', questions=questions)
            
        except Exception as e:
            return f"Lỗi tạo đề thi: {str(e)}"

# --- 3. NỘP BÀI & CHẤM ĐIỂM (Viết lại logic chấm tại đây vì S4 chưa xong) ---
@test_bp.route('/nop-bai', methods=['POST'])
def submit_test():
    # 1. Kiểm tra đăng nhập
    if 'user_id' not in session:
        return "Lỗi: Bạn chưa đăng nhập!"

    # 2. Lấy đáp án chuẩn từ Session (đã lưu lúc tạo đề)
    if 'exam_answers' not in session:
        return "Lỗi: Không tìm thấy dữ liệu đề thi (Session expired). Hãy thử lại."

    correct_answers = session['exam_answers'] # Dạng {'101': 'A', '102': 'B'}
    user_answers = request.form.to_dict()     # Dạng {'101': 'A', '105': 'C'}
    
    # 3. Tính điểm (Logic từ Code cũ nhưng viết gọn lại)
    score = 0
    total_questions = len(correct_answers)
    correct_count = 0
    details = [] # Lưu chi tiết để insert vào DB

    for q_id, correct_opt in correct_answers.items():
        user_opt = user_answers.get(q_id) # Lấy đáp án user chọn
        is_correct = (user_opt == correct_opt)
        
        if is_correct:
            score += (10 / total_questions) # Thang điểm 10
            correct_count += 1
            
        details.append({
            'ExerciseId': q_id,
            'SelectedOption': user_opt,
            'IsCorrect': 1 if is_correct else 0
        })
    
    final_score = round(score, 2)

    # 4. Lưu vào Database (Dùng SQLAlchemy của Code mới)
    try:
        user_id = session['user_id']
        
        # A. Lưu bảng Exams
        # Lưu ý: TopicId tạm để 1 hoặc lấy từ form nếu có (ở đây ta để mặc định 1 cho code chạy được)
        sql_exam = text("INSERT INTO Exams (UserId, TopicId, TotalScore) VALUES (:u, :t, :s)")
        result = db.session.execute(sql_exam, {'u': user_id, 't': 1, 's': final_score})
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

    except Exception as e:
        db.session.rollback()
        return f"Lỗi lưu điểm vào DB: {str(e)}"

    # 5. TRẢ VỀ MÀN HÌNH KẾT QUẢ TẠM (VÌ S4 CHƯA LÀM XONG)
    # Thay vì redirect, ta trả về HTML luôn để bạn xem điểm
    return f"""
    <div style="font-family: sans-serif; text-align: center; padding: 50px; background: #f8f9fa;">
        <h1 style="color: #6366f1;">🎉 NỘP BÀI THÀNH CÔNG!</h1>
        <div style="background: white; padding: 30px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); display: inline-block;">
            <h3>Điểm số của bạn:</h3>
            <div style="font-size: 4rem; color: #ff4757; font-weight: bold;">{final_score}</div>
            <p style="font-size: 1.2rem;">Số câu đúng: <b>{correct_count}</b> / {total_questions}</p>
            <hr>
            <p style="color: #666;">(Dữ liệu đã được lưu vào Database)</p>
            <p style="color: #888; font-style: italic;">Giao diện xem chi tiết đang chờ S4 hoàn thiện...</p>
            <br>
            <a href="{ url_for('test.select_topic') }" 
               style="text-decoration: none; background: #6366f1; color: white; padding: 12px 25px; border-radius: 50px; font-weight: bold;">
               🔄 Làm đề khác
            </a>
            <a href="/" 
               style="text-decoration: none; background: #e0e7ff; color: #6366f1; padding: 12px 25px; border-radius: 50px; font-weight: bold; margin-left: 10px;">
               🏠 Về trang chủ
            </a>
        </div>
    </div>
    """
    # sau khi S4 xong bạn có thể redirect về trang kết quả chi tiết như bình thường
    #return redirect(url_for('report.view_result', exam_id=exam_id))