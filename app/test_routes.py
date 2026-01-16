from flask import Blueprint, render_template, request, redirect, url_for, session
from app import db
from sqlalchemy import text
from app.question_service import generate_exam_questions
from datetime import datetime

# --- THÊM 2 DÒNG NÀY ĐỂ FIX LỖI 403 BÊN S4 ---
from flask_login import login_user, current_user, login_required
from app.models import User
# ---------------------------------------------

test_bp = Blueprint('test', __name__)

# --- 1. TRANG CHỌN CHỦ ĐỀ ---
@test_bp.route('/chon-chu-de')
@login_required
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
@login_required
def do_test():
    if request.method == 'GET':
        return redirect(url_for('test.select_topic'))
    
    if request.method == 'POST':
        selected_ids = request.form.getlist('topics')
        raw_questions = generate_exam_questions(selected_ids, total_questions=20)

        if not raw_questions:
            return "Không tạo được đề thi (Có thể do lỗi DB hoặc không đủ câu hỏi)."

        questions = []
        for q in raw_questions:
            questions.append({
                'Id': q['Id'],
                'Content': q['Content'],
                'OptionA': q['OptionA'], 'OptionB': q['OptionB'],
                'OptionC': q['OptionC'], 'OptionD': q['OptionD']
            })
        
        correct_answers = {str(q['Id']): q['CorrectOption'] for q in raw_questions}
        session['exam_answers'] = correct_answers
        
        return render_template('quiz/do_test.html', questions=questions)

# --- 3. NỘP BÀI (XỬ LÝ 2 ĐƯỜNG DỮ LIỆU) ---
@test_bp.route('/nop-bai', methods=['POST'])
@login_required
def submit_test():
    user_id = current_user.Id

    if 'exam_answers' not in session:
        return "Lỗi Session: Mất dữ liệu đề thi."

    correct_answers = session['exam_answers']
    user_answers = request.form.to_dict()
    
    # Tính điểm
    score = 0
    total = len(correct_answers)
    details = []

    for q_id, correct_opt in correct_answers.items():
        user_opt = user_answers.get(q_id)
        is_correct = (user_opt == correct_opt)
        if is_correct: score += (10 / total)
        details.append({
            'ex_id': q_id, 'opt': user_opt, 'corr': 1 if is_correct else 0
        })
    
    final_score = round(score, 2)
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    exam_id = None

    try:
        # [ĐƯỜNG 1]: LƯU VÀO DATABASE (LỊCH SỬ)
        # Lưu xong bước này là trang Lịch sử tự động có dữ liệu
        sql_exam = text("INSERT INTO Exams (UserId, TopicId, TotalScore, CreatedAt) VALUES (:u, 1, :s, :t)")
        result = db.session.execute(sql_exam, {'u': user_id, 's': final_score, 't': now_str})
        db.session.commit()
        
        exam_id = result.lastrowid
        
        for d in details:
            sql_detail = text("""
                INSERT INTO StudentResults (ExamId, ExerciseId, SelectedOption, IsCorrect) 
                VALUES (:eid, :exid, :opt, :corr)
            """)
            db.session.execute(sql_detail, {'eid': exam_id, 'exid': d['ex_id'], 'opt': d['opt'], 'corr': d['corr']})
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        return f"Lỗi lưu điểm: {str(e)}"

    # [ĐƯỜNG 2]: CHUYỂN HƯỚNG SANG TRANG THỐNG KÊ (S4)
    if exam_id:
        return redirect(url_for('report.view_result', exam_id=exam_id))
    else:
        return "Lỗi: Không lấy được ID bài thi."

# --- 4. TRANG LỊCH SỬ ---
@test_bp.route('/lich-su')
@login_required
def history():
    user_id = current_user.Id
    try:
        sql_exams = text("SELECT Id, TotalScore, CreatedAt FROM Exams WHERE UserId = :uid AND TotalScore IS NOT NULL ORDER BY Id DESC")
        exams_result = db.session.execute(sql_exams, {'uid': user_id}).fetchall()
        
        history_data = []
        for exam in exams_result:
            sql_details = text("""
                SELECT t.Name, sr.IsCorrect
                FROM StudentResults sr
                JOIN Exercises e ON sr.ExerciseId = e.Id
                JOIN Topics t ON e.TopicId = t.Id
                WHERE sr.ExamId = :eid
            """)
            details = db.session.execute(sql_details, {'eid': exam.Id}).fetchall()
            
            topic_stats = {}
            all_topics = set()
            for row in details:
                t_name = row.Name
                all_topics.add(t_name)
                if t_name not in topic_stats: topic_stats[t_name] = {'total': 0, 'correct': 0}
                topic_stats[t_name]['total'] += 1
                if row.IsCorrect: topic_stats[t_name]['correct'] += 1
            
            weak_topics = []
            for name, stat in topic_stats.items():
                if (stat['correct'] / stat['total']) < 0.5: weak_topics.append(name)

            topic_names = list(all_topics)
            if not topic_names: scope = "Tổng hợp"
            elif len(topic_names) == 1: scope = topic_names[0]
            else: scope = f"Ôn tập ({len(topic_names)} chủ đề)"
            
            score = exam.TotalScore if exam.TotalScore is not None else 0
            if score >= 8: advice = ("Giỏi", "success")
            elif score >= 5: advice = ("Khá", "primary")
            else: advice = ("Yếu", "danger")

            try: date_str = datetime.strptime(str(exam.CreatedAt), '%Y-%m-%d %H:%M:%S').strftime('%d/%m %H:%M')
            except: date_str = str(exam.CreatedAt)

            history_data.append({
                'id': exam.Id, 'scope': scope, 'topics': topic_names,
                'score': score, 'advice_text': advice[0], 'advice_class': advice[1],
                'weak_list': weak_topics, 'date': date_str
            })
        return render_template('quiz/history.html', history_data=history_data)
    except Exception as e:
        return f"Lỗi: {str(e)}"

# --- 5. XEM CHI TIẾT ---
@test_bp.route('/xem-lai-bai/<int:exam_id>')
@login_required
def review_exam(exam_id):
    try:
        sql_exam = text("SELECT * FROM Exams WHERE Id = :eid")
        exam = db.session.execute(sql_exam, {'eid': exam_id}).fetchone()
        if not exam: return "Không tìm thấy."

        sql_details = text("""
            SELECT sr.SelectedOption, sr.IsCorrect,
                   e.Content, e.OptionA, e.OptionB, e.OptionC, e.OptionD, 
                   e.CorrectOption, e.Difficulty
            FROM StudentResults sr
            JOIN Exercises e ON sr.ExerciseId = e.Id
            WHERE sr.ExamId = :eid
        """)
        results = db.session.execute(sql_details, {'eid': exam_id}).fetchall()
        
        questions = []
        for row in results:
            questions.append({
                'Content': row.Content,
                'Options': {'A': row.OptionA, 'B': row.OptionB, 'C': row.OptionC, 'D': row.OptionD},
                'Selected': row.SelectedOption, 'Correct': row.CorrectOption, 'IsRight': row.IsCorrect
            })
        return render_template('quiz/review_exam.html', exam=exam, questions=questions)
    except Exception as e:
        return f"Lỗi: {str(e)}"

# --- 6. XÓA LỊCH SỬ ---
@test_bp.route('/xoa-lich-su/<int:exam_id>', methods=['POST'])
@login_required
def delete_history(exam_id):
    try:
        db.session.execute(text("DELETE FROM StudentResults WHERE ExamId = :eid"), {'eid': exam_id})
        db.session.execute(text("DELETE FROM Exams WHERE Id = :eid"), {'eid': exam_id})
        db.session.commit()
        return redirect(url_for('test.history'))
    except Exception as e:
        db.session.rollback()
        return f"Lỗi: {str(e)}"