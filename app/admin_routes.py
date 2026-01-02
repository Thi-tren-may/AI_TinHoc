# app/admin_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
# 👇 IMPORT QUAN TRỌNG: Gọi file service vào để dùng
from app import question_service 

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# 1. TRANG DANH SÁCH
@admin_bp.route('/questions')
def manage_questions():
    # Gọi service lấy dữ liệu
    questions = question_service.get_all_questions()
    return render_template('admin/manage_questions.html', questions=questions)

# 2. CHỨC NĂNG THÊM MỚI
@admin_bp.route('/question/add', methods=('GET', 'POST'))
def add_question():
    if request.method == 'POST':
        # Gọi service để lưu (truyền tham số từ form vào)
        question_service.add_new_question(
            content=request.form['content'],
            topic_id=request.form['topic_id'],
            difficulty=request.form['difficulty'],
            correct=request.form['correct_option'],
            optA=request.form['option_a'],
            optB=request.form['option_b'],
            optC=request.form['option_c'],
            optD=request.form['option_d']
        )
        flash('Thêm câu hỏi mới thành công!', 'success')
        return redirect(url_for('admin.manage_questions'))

    # Gọi service lấy danh sách chủ đề để hiện menu
    topics = question_service.get_small_topics()
    return render_template('admin/add_question.html', topics=topics)

# 3. CHỨC NĂNG SỬA CÂU HỎI
@admin_bp.route('/question/edit/<int:id>', methods=('GET', 'POST'))
def edit_question(id):
    # Lấy thông tin câu hỏi cũ
    question = question_service.get_question_by_id(id)
    
    if request.method == 'POST':
        # Gọi service để cập nhật
        question_service.update_question(
            question_id=id,
            content=request.form['content'],
            topic_id=request.form['topic_id'],
            difficulty=request.form['difficulty'],
            correct=request.form['correct_option'],
            optA=request.form['option_a'],
            optB=request.form['option_b'],
            optC=request.form['option_c'],
            optD=request.form['option_d']
        )
        flash('Đã cập nhật câu hỏi thành công!', 'success')
        return redirect(url_for('admin.manage_questions'))

    # Lấy danh sách chủ đề
    topics = question_service.get_small_topics()
    return render_template('admin/edit_question.html', question=question, topics=topics)

# 4. CHỨC NĂNG XÓA CÂU HỎI
@admin_bp.route('/question/delete/<int:id>')
def delete_question(id):
    question_service.delete_question(id)
    flash('Đã xóa câu hỏi khỏi kho dữ liệu!', 'success')
    return redirect(url_for('admin.manage_questions'))

# 5. TEST THUẬT TOÁN SINH ĐỀ
@admin_bp.route('/test-generate/<int:topic_id>')
def test_generate(topic_id):
    # Gọi thuật toán từ Service (S2 sau này cũng sẽ gọi hàm y hệt thế này)
    questions = question_service.generate_exam_questions(topic_id)
    return {
        "message": f"Sinh thành công {len(questions)} câu hỏi",
        "questions": questions
    }