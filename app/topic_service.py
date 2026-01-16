# app/topic_service.py
import sqlite3

def get_db_connection():
    conn = sqlite3.connect('database/app.db')
    conn.row_factory = sqlite3.Row
    return conn

# 1. LẤY TẤT CẢ CHỦ ĐỀ (Kèm tên chủ đề cha nếu có)
def get_all_topics():
    conn = get_db_connection()
    # Kỹ thuật Self-Join để lấy tên chủ đề cha
    query = """
        SELECT t1.*, t2.Name as ParentName 
        FROM Topics t1
        LEFT JOIN Topics t2 ON t1.ParentId = t2.Id
        WHERE t1.IsActive = 1
        ORDER BY t1.Level, t1.Id
    """
    topics = conn.execute(query).fetchall()
    conn.close()
    return topics

# 2. LẤY DANH SÁCH CHỦ ĐỀ LỚN (Để nạp vào menu thả xuống khi tạo chủ đề nhỏ)
def get_large_topics():
    conn = get_db_connection()
    topics = conn.execute("SELECT * FROM Topics WHERE Level = 'large' AND IsActive = 1").fetchall()
    conn.close()
    return topics

# 3. LẤY 1 CHỦ ĐỀ THEO ID
def get_topic_by_id(topic_id):
    conn = get_db_connection()
    topic = conn.execute("SELECT * FROM Topics WHERE Id = ?", (topic_id,)).fetchone()
    conn.close()
    return topic

# 4. THÊM CHỦ ĐỀ MỚI
def add_new_topic(name, level, parent_id=None):
    conn = get_db_connection()
    try:
        if level == 'large':
            parent_id = None # Chủ đề lớn thì không có cha
        
        conn.execute("""
            INSERT INTO Topics (Name, Level, ParentId, IsActive)
            VALUES (?, ?, ?, 1)
        """, (name, level, parent_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Lỗi thêm chủ đề: {e}")
        return False
    finally:
        conn.close()

# 5. CẬP NHẬT CHỦ ĐỀ
def update_topic(topic_id, name, level, parent_id=None):
    conn = get_db_connection()
    if level == 'large':
        parent_id = None
        
    conn.execute("""
        UPDATE Topics SET Name = ?, Level = ?, ParentId = ? WHERE Id = ?
    """, (name, level, parent_id, topic_id))
    conn.commit()
    conn.close()

# 6. XÓA CHỦ ĐỀ
def delete_topic(topic_id):
    try:
        conn = get_db_connection()
        # Chuyển trạng thái IsActive về 0 (Ẩn đi)
        # Không cần kiểm tra câu hỏi vì Ẩn đi thì không bị lỗi khóa ngoại
        conn.execute("UPDATE Topics SET IsActive = 0 WHERE Id = ?", (topic_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Lỗi xóa mềm: {e}")
        return False
    finally:
        conn.close()