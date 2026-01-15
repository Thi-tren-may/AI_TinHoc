# app/admin_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
# 👇 IMPORT QUAN TRỌNG: Gọi file service vào để dùng
from app import question_service 
from app import student_service   # 👇 CÁI MỚI (quản lý học sinh)
from app import topic_service
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# =========================================================
# 👇 BẢO MẬT: CHẶN KHÔNG CHO HỌC SINH VÀO ADMIN - THU
# =========================================================
@admin_bp.before_request
@login_required
def require_admin():
    if current_user.Role != 'admin':
        flash('CẢNH BÁO: Bạn không có quyền truy cập trang Quản trị!', 'danger')
        return redirect(url_for('home.student_index'))

# =========================================================
# 👇 TRANG TỔNG QUAN (DASHBOARD)
# =========================================================
@admin_bp.route('/')
@admin_bp.route('/dashboard')
def dashboard():
    # Lấy số lượng từ các service
    student_count = len(student_service.get_all_students())
    topic_count = len(topic_service.get_large_topics())
    question_count = len(question_service.get_all_questions())
    # Lấy danh sách chủ đề lớn để hiển thị động
    large_topics = topic_service.get_large_topics()
    
    return render_template('admin/dashboard.html', 
                           student_count=student_count,
                           topic_count=topic_count,
                           question_count=question_count,
                           large_topics=large_topics)
# =========================================================
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
# =========================================================
# 👇 PHẦN QUẢN LÝ HỌC SINH (GỌI SANG STUDENT_SERVICE)
# =========================================================

# 1. DANH SÁCH HỌC SINH
@admin_bp.route('/students')
def manage_students():
    # Gọi service mới
    students = student_service.get_all_students()
    return render_template('admin/manage_students.html', students=students)

# 2. THÊM HỌC SINH
@admin_bp.route('/student/add', methods=('GET', 'POST'))
def add_student():
    if request.method == 'POST':
        password = request.form['password']

        # Gọi service mới để thêm
        success = student_service.add_new_student(
            username=request.form['username'],
            password=password,
            grade=request.form['grade']
        )
        
        if success:
            flash('Thêm học sinh thành công!', 'success')
            return redirect(url_for('admin.manage_students'))
        else:
            flash('Lỗi! Tên đăng nhập đã tồn tại.', 'danger')
            
    return render_template('admin/add_student.html')

# 3. SỬA HỌC SINH
@admin_bp.route('/student/edit/<int:id>', methods=('GET', 'POST'))
def edit_student(id):
    # Lấy thông tin học sinh cũ
    student = student_service.get_student_by_id(id)
    
    if request.method == 'POST':
        password = request.form['password']

        # Gọi service mới để sửa
        student_service.update_student(
            user_id=id,
            username=request.form['username'],
            grade=request.form['grade'],
            password=password
        )
        flash('Cập nhật thông tin thành công!', 'success')
        return redirect(url_for('admin.manage_students'))
        
    return render_template('admin/edit_student.html', student=student)

# 4. XÓA HỌC SINH
@admin_bp.route('/student/delete/<int:id>')
def delete_student(id):
    student_service.delete_student(id)
    flash('Đã xóa học sinh!', 'success')
    return redirect(url_for('admin.manage_students'))
# =========================================================
# 👇 PHẦN QUẢN LÝ CHỦ ĐỀ (YÊU CẦU CỦA S3)
# =========================================================

# 1. DANH SÁCH CHỦ ĐỀ
@admin_bp.route('/topics')
def manage_topics():
    topics = topic_service.get_all_topics()
    return render_template('admin/manage_topics.html', topics=topics)

# 2. THÊM CHỦ ĐỀ
@admin_bp.route('/topic/add', methods=('GET', 'POST'))
def add_topic():
    if request.method == 'POST':
        name = request.form['name']
        level = request.form['level']
        # Nếu chọn large thì parent_id là None, nếu small thì lấy từ form
        parent_id = request.form.get('parent_id') if level == 'small' else None
        
        topic_service.add_new_topic(name, level, parent_id)
        flash('Thêm chủ đề thành công!', 'success')
        return redirect(url_for('admin.manage_topics'))
        
    # Lấy danh sách chủ đề lớn để hiển thị trong select box
    large_topics = topic_service.get_large_topics()
    return render_template('admin/add_topic.html', large_topics=large_topics)

# 3. SỬA CHỦ ĐỀ
@admin_bp.route('/topic/edit/<int:id>', methods=('GET', 'POST'))
def edit_topic(id):
    topic = topic_service.get_topic_by_id(id)
    
    if request.method == 'POST':
        name = request.form['name']
        level = request.form['level']
        parent_id = request.form.get('parent_id') if level == 'small' else None
        
        topic_service.update_topic(id, name, level, parent_id)
        flash('Cập nhật chủ đề thành công!', 'success')
        return redirect(url_for('admin.manage_topics'))

    large_topics = topic_service.get_large_topics()
    return render_template('admin/edit_topic.html', topic=topic, large_topics=large_topics)

# 4. XÓA CHỦ ĐỀ (Đã sửa logic thành Xóa mềm)
@admin_bp.route('/topic/delete/<int:id>')
def delete_topic(id):
    # Gọi service (Lúc này service đã chạy lệnh UPDATE IsActive=0 rồi)
    success = topic_service.delete_topic(id)
    
    if success:
        # 👇 SỬA CÂU THÔNG BÁO FLASH CHO ĐÚNG NGHIỆP VỤ
        flash('Đã xóa chủ đề khỏi danh sách!', 'success')
    else:
        flash('Đã xảy ra lỗi hệ thống.', 'danger')
        
    return redirect(url_for('admin.manage_topics'))