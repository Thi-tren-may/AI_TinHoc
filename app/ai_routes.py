from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from flask_login import login_required, current_user 
# Nhớ import model Exams để lấy dữ liệu lịch sử bài làm
from app.models import Exam
# Import cả Class phân tích (Lớp 2) và hàm giải thích (Lớp 3)
from app.ai_logic import LearningAnalytics, get_ai_explanation 

ai_bp = Blueprint('ai', __name__)

# --- CỔNG 1: GIẢI THÍCH CÂU SAI (Dùng cho S4 - Trang Kết Quả) ---
@ai_bp.route('/chat-ai', methods=['POST'])
def chat_ai():
    data = request.json
    # Phải lấy thêm 2 cái này để chạy được Cache và Check Limit (Hạn mức)
    user_id = data.get('user_id')
    exercise_id = data.get('exercise_id')
    
    question = data.get('question')
    student_ans = data.get('student_ans')
    correct_ans = data.get('correct_ans')

    if all([user_id, exercise_id, question, student_ans, correct_ans]):
        # Truyền ĐỦ 5 tham số như bạn đã định nghĩa trong ai_logic.py
        reply = get_ai_explanation(user_id, exercise_id, question, student_ans, correct_ans)
        return jsonify({"reply": reply})
    
    return jsonify({"reply": "Thiếu dữ liệu (ID người dùng, ID câu hỏi hoặc nội dung) để AI phân tích."})

# --- CỔNG 2: TRANG TIẾN ĐỘ HỌC TẬP (SỬA LẠI Ở ĐÂY) ---
@ai_bp.route('/progress')
@login_required
def progress():
    # 1. Lấy ID người dùng
    user_id = current_user.Id
    
    # 2. Lấy báo cáo phân tích từ AI Lớp 2
    analytics = LearningAnalytics()
    report = analytics.generate_full_report(user_id) 
    
    # 3. Lấy danh sách 10 bài thi gần nhất để hiện lên bảng lịch sử
    # Chúng ta lọc theo UserId và sắp xếp bài mới nhất lên đầu
    exams = Exam.query.filter_by(UserId=user_id).order_by(Exam.CreatedAt.desc()).limit(10).all()
    
    # 4. Chuẩn bị danh sách điểm cho biểu đồ (Chart.js)
    # Lấy điểm số từ danh sách bài thi và đảo ngược lại để biểu đồ chạy từ cũ đến mới
    score_list = [e.TotalScore for e in exams][::-1]
    
    # 5. Debug kiểm tra dữ liệu trước khi render (Kiểm tra ở Terminal VSCode)
    print(f"--- DEBUG PROGRESS ---")
    print(f"Report: {report}")
    print(f"Score List: {score_list}")
    print(f"Num Exams: {len(exams)}")
    
    # 6. Gửi TẤT CẢ dữ liệu sang HTML
    return render_template('student/progress.html', 
                           report=report, 
                           exams=exams, 
                           score_list=score_list)