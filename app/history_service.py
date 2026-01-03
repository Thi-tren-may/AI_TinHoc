from .models import db, Exam, Topic

def get_user_history(user_id):
    """
    S5: Hàm lấy danh sách các bài thi cũ của user.
    Kết nối bảng Exam và Topic để lấy tên chủ đề.
    """
    # Truy vấn: Lấy bài thi của user, sắp xếp mới nhất lên đầu
    # Trong thực tế sẽ join với bảng Topic để lấy tên, ở đây giả lập hoặc query đơn giản
    exams = db.session.query(Exam, Topic.Name).join(Topic, Exam.TopicId == Topic.Id)\
        .filter(Exam.UserId == user_id)\
        .order_by(Exam.CreatedAt.desc()).all()
    
    return exams

def save_exam_result(user_id, topic_id, score):
    """S5: Hàm lưu kết quả bài thi mới (Sẽ được gọi bởi S2)"""
    pass