from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, Exam, StudentResult, Exercise, Topic
import json

report_bp = Blueprint('report', __name__)

# --- 1. TRANG KẾT QUẢ CHI TIẾT (Khớp với giao diện đẹp của S4) ---
@report_bp.route('/result/<int:exam_id>')
@login_required
def view_result(exam_id):
    # 1. Lấy bài thi
    exam = Exam.query.get_or_404(exam_id)
    if exam.UserId != current_user.Id:
        return "Không có quyền truy cập", 403

    # 2. Lấy dữ liệu câu trả lời
    details = db.session.query(StudentResult, Exercise)\
        .join(Exercise, StudentResult.ExerciseId == Exercise.Id)\
        .filter(StudentResult.ExamId == exam_id).all()

    # 3. Tính toán thống kê
    # Biến đếm cho 3 mức độ: 1=NB, 2=TH, 3=VD
    stats = {
        1: {'total': 0, 'correct': 0},
        2: {'total': 0, 'correct': 0},
        3: {'total': 0, 'correct': 0}
    }
    
    wrong_answers = []
    total_correct = 0
    total_questions = len(details)

    for result, question in details:
        diff = question.Difficulty
        if diff in stats:
            stats[diff]['total'] += 1
            
            if result.IsCorrect:
                stats[diff]['correct'] += 1
                total_correct += 1
            else:
                # Đóng gói dữ liệu câu sai cho giao diện
                wrong_answers.append({
                    'question': question.Content,
                    'selected': result.SelectedOption,
                    'correct_opt': question.CorrectOption,
                    'difficulty': 'Dễ' if diff == 1 else 'TB' if diff == 2 else 'Khó',
                    'id': question.Id # ID để gọi AI
                })

    # 4. Chuẩn bị dữ liệu cho Biểu đồ (Khớp với HTML của bạn)
    
    # a) Dữ liệu Biểu đồ Cột (bar_data): [% Nhận biết, % Thông hiểu, % Vận dụng]
    bar_data = []
    for i in [1, 2, 3]:
        s = stats[i]
        percent = round((s['correct'] / s['total'] * 100), 1) if s['total'] > 0 else 0
        bar_data.append(percent)

    # b) Dữ liệu Biểu đồ Tròn (pie_data): [Số câu đúng, Số câu sai]
    pie_data = [total_correct, total_questions - total_correct]

    # 5. Feedback & Gợi ý (Object giống HTML yêu cầu)
    if exam.TotalScore >= 8.0:
        feedback = {'msg': 'Xuất sắc! Phong độ rất cao.', 'color': 'text-success', 'icon': 'fas fa-trophy'}
        suggestion = "Bạn đã nắm chắc kiến thức nền tảng. Hãy thử sức với các đề nâng cao hơn nhé!"
    elif exam.TotalScore >= 5.0:
        feedback = {'msg': 'Khá tốt, nhưng cần cẩn thận hơn.', 'color': 'text-warning', 'icon': 'fas fa-check-circle'}
        suggestion = "Hãy xem lại các câu sai bên dưới để rút kinh nghiệm cho lần sau."
    else:
        feedback = {'msg': 'Cần cố gắng nhiều hơn!', 'color': 'text-danger', 'icon': 'fas fa-exclamation-triangle'}
        suggestion = "Bạn nên ôn tập lại kiến thức trong Sách giáo khoa trước khi làm bài tiếp."

    # 6. Render ra file result.html
    return render_template('report/result.html', 
                           exam=exam,
                           bar_data=bar_data, # Gửi mảng Python sang (HTML sẽ dùng tojson)
                           pie_data=pie_data, 
                           wrong_answers=wrong_answers,
                           feedback=feedback,
                           suggestion=suggestion)

# --- 2. TRANG LỊCH SỬ (Giữ nguyên) ---
@report_bp.route('/view')
@login_required
def view_report():
    results = db.session.query(Exam, Topic.Name.label('TopicName'))\
        .join(Topic, Exam.TopicId == Topic.Id)\
        .filter(Exam.UserId == current_user.Id)\
        .order_by(Exam.Id.desc()).all()
    # Trả về file view_result.html (Danh sách)
    return render_template('report/view_result.html', results=results)