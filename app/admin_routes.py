from flask import Blueprint, render_template, request, redirect, url_for, flash
import sqlite3

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def get_db_connection():
    conn = sqlite3.connect('database/app.db')
    conn.row_factory = sqlite3.Row
    return conn

# 1. TRANG DANH SÁCH
@admin_bp.route('/questions')
def manage_questions():
    conn = get_db_connection()
    query = """
        SELECT e.*, t.Name as TopicName 
        FROM Exercises e
        LEFT JOIN Topics t ON e.TopicId = t.Id
        ORDER BY e.Id DESC
    """
    questions = conn.execute(query).fetchall()
    conn.close()
    return render_template('admin/manage_questions.html', questions=questions)

# 2. CHỨC NĂNG THÊM MỚI (New)
@admin_bp.route('/question/add', methods=('GET', 'POST'))
def add_question():
    conn = get_db_connection()
    
    if request.method == 'POST':
        # Lấy dữ liệu từ Form
        content = request.form['content']
        topic_id = request.form['topic_id']
        level = request.form['difficulty']
        correct = request.form['correct_option']
        
        # Lưu vào Database
        conn.execute("""
            INSERT INTO Exercises (Content, TopicId, Difficulty, CorrectOption, OptionA, OptionB, OptionC, OptionD, Grade)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (content, topic_id, level, correct, 
              request.form['option_a'], request.form['option_b'], 
              request.form['option_c'], request.form['option_d'], 10))
        conn.commit()
        conn.close()
        return redirect(url_for('admin.manage_questions'))

    # Lấy danh sách chủ đề để hiện ra menu chọn
    topics = conn.execute('SELECT * FROM Topics WHERE Level="small"').fetchall()
    conn.close()
    return render_template('admin/add_question.html', topics=topics)
# --- CHỨC NĂNG 3: SỬA CÂU HỎI ---
@admin_bp.route('/question/edit/<int:id>', methods=('GET', 'POST'))
def edit_question(id):
    conn = get_db_connection()
    
    # Lấy thông tin câu hỏi cần sửa
    question = conn.execute('SELECT * FROM Exercises WHERE Id = ?', (id,)).fetchone()
    
    if request.method == 'POST':
        # Cập nhật dữ liệu mới vào DB
        content = request.form['content']
        topic_id = request.form['topic_id']
        level = request.form['difficulty']
        correct = request.form['correct_option']
        
        conn.execute("""
            UPDATE Exercises 
            SET Content = ?, TopicId = ?, Difficulty = ?, CorrectOption = ?,
                OptionA = ?, OptionB = ?, OptionC = ?, OptionD = ?
            WHERE Id = ?
        """, (content, topic_id, level, correct,
              request.form['option_a'], request.form['option_b'],
              request.form['option_c'], request.form['option_d'],
              id))
        conn.commit()
        conn.close()
        flash('Đã cập nhật câu hỏi thành công!', 'success')
        return redirect(url_for('admin.manage_questions'))

    # Lấy danh sách chủ đề để hiện ra menu chọn
    topics = conn.execute('SELECT * FROM Topics WHERE Level="small"').fetchall()
    conn.close()
    return render_template('admin/edit_question.html', question=question, topics=topics)

# --- CHỨC NĂNG 4: XÓA CÂU HỎI ---
@admin_bp.route('/question/delete/<int:id>')
def delete_question(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM Exercises WHERE Id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Đã xóa câu hỏi khỏi kho dữ liệu!', 'success')
    return redirect(url_for('admin.manage_questions'))