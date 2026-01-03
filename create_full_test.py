from app import create_app, db
from app.models import User, Topic, Exercise, Exam, StudentResult

app = create_app()

with app.app_context():
    print("⏳ Đang tạo bài thi mới với dữ liệu xịn...")

    # 1. Lấy User và Topic cũ (đỡ phải tạo lại)
    user = User.query.first()
    if not user:
        print("❌ Lỗi: Chưa có User nào. Hãy chạy init_db.py trước!")
        exit()
        
    topic = Topic.query.first() # Lấy chủ đề Mạng máy tính

    # 2. TẠO 5 CÂU HỎI MỚI (Đủ 3 mức độ)
    q1 = Exercise(TopicId=topic.Id, Content='RAM là bộ nhớ gì?', OptionA='Chỉ đọc', OptionB='Truy cập ngẫu nhiên', OptionC='Lưu trữ lâu dài', OptionD='Ảo', CorrectOption='B', Difficulty=1)
    q2 = Exercise(TopicId=topic.Id, Content='Phím tắt Copy là gì?', OptionA='Ctrl+V', OptionB='Ctrl+X', OptionC='Ctrl+C', OptionD='Alt+F4', CorrectOption='C', Difficulty=1)
    q3 = Exercise(TopicId=topic.Id, Content='AI là viết tắt của?', OptionA='Apple Inc', OptionB='Artificial Intelligence', OptionC='Adobe Illustrator', OptionD='All In', CorrectOption='B', Difficulty=2)
    q4 = Exercise(TopicId=topic.Id, Content='Python ra đời năm nào?', OptionA='1990', OptionB='1991', OptionC='2000', OptionD='1989', CorrectOption='B', Difficulty=2)
    q5 = Exercise(TopicId=topic.Id, Content='Độ phức tạp thuật toán sắp xếp nhanh (QuickSort) trung bình là?', OptionA='O(n)', OptionB='O(n^2)', OptionC='O(n log n)', OptionD='O(1)', CorrectOption='C', Difficulty=3)
    
    db.session.add_all([q1, q2, q3, q4, q5])
    db.session.commit()
    print("   + Đã thêm 5 câu hỏi vào kho.")

    # 3. TẠO BÀI THI SỐ 2 (Exam ID sẽ tự tăng lên)
    # Giả sử học sinh làm được 6 điểm
    exam = Exam(UserId=user.Id, TopicId=topic.Id, TotalScore=6.0)
    db.session.add(exam)
    db.session.commit()

    # 4. TẠO KẾT QUẢ LÀM BÀI (Giả lập học sinh chọn đáp án)
    results = [
        # Câu 1 (Dễ): Đúng
        StudentResult(ExamId=exam.Id, ExerciseId=q1.Id, SelectedOption='B', IsCorrect=1),
        # Câu 2 (Dễ): Sai (Chọn A thay vì C)
        StudentResult(ExamId=exam.Id, ExerciseId=q2.Id, SelectedOption='A', IsCorrect=0),
        # Câu 3 (TB): Đúng
        StudentResult(ExamId=exam.Id, ExerciseId=q3.Id, SelectedOption='B', IsCorrect=1),
        # Câu 4 (TB): Sai (Chọn A thay vì B)
        StudentResult(ExamId=exam.Id, ExerciseId=q4.Id, SelectedOption='A', IsCorrect=0),
        # Câu 5 (Khó): Sai (Chọn B thay vì C)
        StudentResult(ExamId=exam.Id, ExerciseId=q5.Id, SelectedOption='B', IsCorrect=0)
    ]
    db.session.add_all(results)
    db.session.commit()

    print(f"\n✅ XONG! Đã tạo Bài thi số {exam.Id}")
    print(f"👉 Hãy vào đường link này: http://127.0.0.1:5000/report/result/{exam.Id}")