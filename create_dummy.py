from app import create_app, db
from app.models import User, Topic, Exercise, Exam, StudentResult # Import đúng tên Class trong models.py của bạn

app = create_app()

with app.app_context():
    # Xóa dữ liệu cũ (nếu có) để tránh trùng lặp
    db.drop_all()
    db.create_all()
    print("⏳ Đang khởi tạo dữ liệu mẫu...")
    
    # 1. Tạo User
    user = User(Username='hocsinh_s4', PasswordHash='123', Role='student', Grade=10)
    db.session.add(user)
    db.session.commit() # Commit để lấy ID

    # 2. Tạo Chủ đề
    topic = Topic(Name='Mạng máy tính', Level='small')
    db.session.add(topic)
    db.session.commit()

    # 3. Tạo Câu hỏi (1 câu Dễ, 1 câu Khó)
    q1 = Exercise(TopicId=topic.Id, Content='1+1=?', OptionA='1', OptionB='2', OptionC='3', OptionD='4', CorrectOption='B', Difficulty=1)
    q2 = Exercise(TopicId=topic.Id, Content='Code Python khó không?', OptionA='Dễ', OptionB='Khó', OptionC='Bình thường', OptionD='Tùy người', CorrectOption='A', Difficulty=3)
    db.session.add_all([q1, q2])
    db.session.commit()

    # 4. Tạo Bài thi (Exam ID sẽ là 1)
    exam = Exam(UserId=user.Id, TopicId=topic.Id, TotalScore=8.5)
    db.session.add(exam)
    db.session.commit()

    # 5. Tạo Kết quả làm bài
    r1 = StudentResult(ExamId=exam.Id, ExerciseId=q1.Id, SelectedOption='B', IsCorrect=1) # Đúng
    r2 = StudentResult(ExamId=exam.Id, ExerciseId=q2.Id, SelectedOption='B', IsCorrect=0) # Sai
    db.session.add_all([r1, r2])
    db.session.commit()

    print("✅ Xong! Đã tạo Bài thi số 1 thành công!")