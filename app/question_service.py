# app/question_service.py
# import sqlite3
from app import db                  # Để dùng db.session
from sqlalchemy import text         # Để dùng câu lệnh SQL text()
import random                       # Để dùng random.shuffle
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

# 8. THUẬT TOÁN SINH ĐỀ NÂNG CẤP (Hỗ trợ nhiều chủ đề + Tỷ lệ vàng)
def generate_exam_questions(selected_topic_ids, total_questions=20):
    """
    selected_topic_ids: Danh sách ID chủ đề (VD: ['1', '2'])
    total_questions: Tổng số câu (Mặc định 20)
    """
    try:
        # 1. Tính toán tỷ lệ
        num_easy = int(total_questions * 0.4)   # 8 câu
        num_medium = int(total_questions * 0.3) # 6 câu
        num_hard = total_questions - num_easy - num_medium # 6 câu

        # 2. Xử lý danh sách ID để đưa vào SQL
        if not selected_topic_ids:
            # Nếu không chọn gì -> Lấy tất cả
            where_clause = "1=1" 
            params = {}
        else:
            # Logic tìm cả cha lẫn con
            placeholders = ','.join([f':id{i}' for i in range(len(selected_topic_ids))])
            where_clause = f"""
                (t.Id IN ({placeholders}) OR t.ParentId IN ({placeholders}))
            """
            params = {f'id{i}': topic_id for i, topic_id in enumerate(selected_topic_ids)}

        # 3. Hàm con lấy câu hỏi theo độ khó
        def get_by_diff(difficulty, limit):
            current_params = params.copy()
            current_params['diff'] = difficulty
            current_params['lim'] = limit
            
            sql = f"""
                SELECT e.* FROM Exercises e
                JOIN Topics t ON e.TopicId = t.Id
                WHERE {where_clause} AND e.Difficulty = :diff
                ORDER BY RANDOM() LIMIT :lim
            """
            result = db.session.execute(text(sql), current_params).fetchall()
            return [dict(row._mapping) for row in result] # Chuyển về dạng Dictionary

        # 4. Thực thi lấy câu hỏi
        questions = []
        questions.extend(get_by_diff(1, num_easy))      # Lấy câu Dễ
        questions.extend(get_by_diff(2, num_medium))    # Lấy câu Vừa
        questions.extend(get_by_diff(3, num_hard))      # Lấy câu Khó

        # 5. Logic bù đắp (Anti-Crash): Nếu thiếu thì lấy bù ngẫu nhiên
        current_count = len(questions)
        if current_count < total_questions:
            missing = total_questions - current_count
            # Lấy thêm các câu chưa có trong danh sách (bất kể độ khó)
            exclude_ids = [q['Id'] for q in questions]
            
            if exclude_ids:
                exclude_placeholders = ','.join([f':ex{i}' for i in range(len(exclude_ids))])
                exclude_sql = f"AND e.Id NOT IN ({exclude_placeholders})"
                exclude_params = {f'ex{i}': eid for i, eid in enumerate(exclude_ids)}
                params.update(exclude_params)
            else:
                exclude_sql = ""

            params['lim'] = missing
            
            fill_sql = f"""
                SELECT e.* FROM Exercises e
                JOIN Topics t ON e.TopicId = t.Id
                WHERE {where_clause} {exclude_sql}
                ORDER BY RANDOM() LIMIT :lim
            """
            more_questions = db.session.execute(text(fill_sql), params).fetchall()
            questions.extend([dict(row._mapping) for row in more_questions])

        # 6. Trộn ngẫu nhiên lần cuối
        random.shuffle(questions)
        
        return questions

    except Exception as e:
        print(f"Lỗi sinh đề: {e}")
        return []