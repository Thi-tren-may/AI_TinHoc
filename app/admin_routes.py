from flask import Blueprint, render_template
import sqlite3

# Chú ý: url_prefix='/admin' để đường dẫn là /admin/questions
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def get_db_connection():
    # Kết nối đến file database/app.db (nằm cùng cấp với thư mục app)
    conn = sqlite3.connect('database/app.db')
    conn.row_factory = sqlite3.Row
    return conn

@admin_bp.route('/questions')
def manage_questions():
    conn = get_db_connection()
    # Lấy câu hỏi kèm tên chủ đề
    query = """
        SELECT e.*, t.Name as TopicName 
        FROM Exercises e
        LEFT JOIN Topics t ON e.TopicId = t.Id
        ORDER BY e.Id DESC
    """
    questions = conn.execute(query).fetchall()
    conn.close()
    return render_template('admin/manage_questions.html', questions=questions)