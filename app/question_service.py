# app/question_service.py
import sqlite3

# 1. CẤU HÌNH KẾT NỐI DATABASE
def get_db_connection():
    conn = sqlite3.connect('database/app.db')
    conn.row_factory = sqlite3.Row # Để lấy dữ liệu dạng từ điển (key-value)
    return conn

# 2. LẤY DANH SÁCH CÂU HỎI (KÈM TÊN CHỦ ĐỀ)
def get_all_questions():
    conn = get_db_connection()
    query = """
        SELECT e.*, t.Name as TopicName 
        FROM Exercises e
        LEFT JOIN Topics t ON e.TopicId = t.Id
        ORDER BY e.Id DESC
    """
    questions = conn.execute(query).fetchall()
    conn.close()
    return questions

# 3. LẤY DANH SÁCH CHỦ ĐỀ NHỎ (ĐỂ HIỂN THỊ MENU CHỌN)
def get_small_topics():
    conn = get_db_connection()
    topics = conn.execute('SELECT * FROM Topics WHERE Level="small"').fetchall()
    conn.close()
    return topics

# 4. THÊM CÂU HỎI MỚI
def add_new_question(content, topic_id, difficulty, correct, optA, optB, optC, optD):
    conn = get_db_connection()
    conn.execute("""
        INSERT INTO Exercises (Content, TopicId, Difficulty, CorrectOption, OptionA, OptionB, OptionC, OptionD, Grade)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (content, topic_id, difficulty, correct, optA, optB, optC, optD, 10))
    conn.commit()
    conn.close()

# 5. LẤY 1 CÂU HỎI THEO ID (ĐỂ SỬA)
def get_question_by_id(question_id):
    conn = get_db_connection()
    question = conn.execute('SELECT * FROM Exercises WHERE Id = ?', (question_id,)).fetchone()
    conn.close()
    return question

# 6. CẬP NHẬT (SỬA) CÂU HỎI
def update_question(question_id, content, topic_id, difficulty, correct, optA, optB, optC, optD):
    conn = get_db_connection()
    conn.execute("""
        UPDATE Exercises 
        SET Content = ?, TopicId = ?, Difficulty = ?, CorrectOption = ?,
            OptionA = ?, OptionB = ?, OptionC = ?, OptionD = ?
        WHERE Id = ?
    """, (content, topic_id, difficulty, correct, optA, optB, optC, optD, question_id))
    conn.commit()
    conn.close()

# 7. XÓA CÂU HỎI
def delete_question(question_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM Exercises WHERE Id = ?', (question_id,))
    conn.commit()
    conn.close()

# 8. THUẬT TOÁN SINH ĐỀ (QUAN TRỌNG - S2 SẼ DÙNG HÀM NÀY)
def generate_exam_questions(topic_id, total_questions=20):
    conn = get_db_connection()
    
    # Cấu hình tỷ lệ: 40% Dễ (1), 30% Vừa (2), 30% Khó (3)
    num_easy = int(total_questions * 0.4)   # 8 câu
    num_medium = int(total_questions * 0.3) # 6 câu
    num_hard = total_questions - num_easy - num_medium # 6 câu

    # Hàm con lấy ngẫu nhiên
    def get_questions_by_diff(diff, limit):
        return conn.execute("""
            SELECT * FROM Exercises 
            WHERE TopicId = ? AND Difficulty = ? 
            ORDER BY RANDOM() LIMIT ?
        """, (topic_id, diff, limit)).fetchall()

    exam_questions = []
    exam_questions.extend(get_questions_by_diff(1, num_easy))
    exam_questions.extend(get_questions_by_diff(2, num_medium))
    exam_questions.extend(get_questions_by_diff(3, num_hard))

    # Logic bù trừ nếu thiếu câu hỏi
    current_count = len(exam_questions)
    if current_count < total_questions:
        missing = total_questions - current_count
        ids_selected = tuple([q['Id'] for q in exam_questions])
        
        if not ids_selected:
             more_questions = conn.execute("SELECT * FROM Exercises WHERE TopicId = ? ORDER BY RANDOM() LIMIT ?", (topic_id, missing)).fetchall()
        else:
            # Tạo chuỗi placeholder ?,?,? cho SQL IN clause
            placeholders = ','.join(['?'] * len(ids_selected))
            query = f"SELECT * FROM Exercises WHERE TopicId = ? AND Id NOT IN ({placeholders}) ORDER BY RANDOM() LIMIT ?"
            params = [topic_id] + list(ids_selected) + [missing]
            more_questions = conn.execute(query, params).fetchall()
            
        exam_questions.extend(more_questions)

    conn.close()
    return [dict(q) for q in exam_questions]