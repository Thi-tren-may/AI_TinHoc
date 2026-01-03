from app import create_app, db
from app.models import User, Topic, Exercise, Exam, StudentResult

app = create_app()

with app.app_context():
    # 1. Xóa sạch dữ liệu cũ để tạo mới từ đầu (Tránh lỗi trùng lặp)
    db.drop_all()
    db.create_all()
    print("🧹 Đã dọn sạch Database cũ...")

    # 2. Tạo User mẫu
    user = User(Username='hocsinh_s4', PasswordHash='secret', Role='student', Grade=10)
    db.session.add(user)
    db.session.commit()
    print("👤 Đã tạo User mẫu (ID: 1)")

    # 3. Tạo Chủ đề mẫu
    topic = Topic(Name='Mạng máy tính', Level='small')
    db.session.add(topic)
    db.session.commit()

    # 4. Tạo Câu hỏi mẫu
    q1 = Exercise(TopicId=topic.Id, Content='1 + 1 = ?', OptionA='1', OptionB='2', OptionC='3', OptionD='4', CorrectOption='B', Difficulty=1)
    q2 = Exercise(TopicId=topic.Id, Content='Python là ngôn ngữ gì?', OptionA='Lập trình', OptionB='Nấu ăn', OptionC='Xây dựng', OptionD='Y tế', CorrectOption='A', Difficulty=1)
    q3 = Exercise(TopicId=topic.Id, Content='Câu hỏi khó nè?', OptionA='A', OptionB='B', OptionC='C', OptionD='D', CorrectOption='C', Difficulty=3)
    db.session.add_all([q1, q2, q3])
    db.session.commit()

    # 5. Tạo Bài thi mẫu (QUAN TRỌNG: ID SẼ LÀ 1)
    exam = Exam(UserId=user.Id, TopicId=topic.Id, TotalScore=9.0)
    db.session.add(exam)
    db.session.commit()
    print(f"📝 Đã tạo Bài thi mẫu (ID: {exam.Id})")

    # 6. Tạo Kết quả chi tiết (Để vẽ biểu đồ)
    r1 = StudentResult(ExamId=exam.Id, ExerciseId=q1.Id, SelectedOption='B', IsCorrect=1) # Đúng
    r2 = StudentResult(ExamId=exam.Id, ExerciseId=q2.Id, SelectedOption='A', IsCorrect=1) # Đúng
    r3 = StudentResult(ExamId=exam.Id, ExerciseId=q3.Id, SelectedOption='A', IsCorrect=0) # Sai
    db.session.add_all([r1, r2, r3])
    db.session.commit()

    print("\n✅ THÀNH CÔNG RỰC RỠ! ĐÃ CÓ DỮ LIỆU ĐỂ TEST.")