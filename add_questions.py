from app import create_app, db
from app.models import Topic, Exercise

app = create_app()

with app.app_context():
    print("⏳ Đang thêm câu hỏi vào kho...")

    # BƯỚC 1: Tìm hoặc Tạo chủ đề (Để gắn câu hỏi vào)
    # Chúng ta sẽ thêm vào chủ đề "Mạng máy tính"
    topic_mang = Topic.query.filter_by(Name='Mạng máy tính').first()
    if not topic_mang:
        topic_mang = Topic(Name='Mạng máy tính', Level='small')
        db.session.add(topic_mang)
        db.session.commit()
        print("   + Đã tạo chủ đề: Mạng máy tính")
    
    # BƯỚC 2: Danh sách câu hỏi cần thêm
    # Difficulty: 1=Dễ (Nhận biết), 2=TB (Thông hiểu), 3=Khó (Vận dụng)
    new_questions = [
        # --- Mức độ 1: Dễ ---
        Exercise(TopicId=topic_mang.Id, Content='Thiết bị nào dùng để kết nối mạng không dây?', OptionA='Switch', OptionB='Router Wi-Fi', OptionC='Cáp quang', OptionD='USB', CorrectOption='B', Difficulty=1),
        Exercise(TopicId=topic_mang.Id, Content='WWW là viết tắt của?', OptionA='World Wide Web', OptionB='World Web Wide', OptionC='Web Wide World', OptionD='Wide Web World', CorrectOption='A', Difficulty=1),
        Exercise(TopicId=topic_mang.Id, Content='IoT là gì?', OptionA='Internet of Things', OptionB='Input of Tools', OptionC='Index of Tech', OptionD='Intranet of Things', CorrectOption='A', Difficulty=1),
        
        # --- Mức độ 2: Trung bình ---
        Exercise(TopicId=topic_mang.Id, Content='Phần mềm độc hại (Malware) bao gồm những loại nào?', OptionA='Virus, Trojan, Worm', OptionB='Word, Excel, PowerPoint', OptionC='Chrome, CocCoc', OptionD='Windows, Linux', CorrectOption='A', Difficulty=2),
        Exercise(TopicId=topic_mang.Id, Content='Để bảo mật tài khoản mạng xã hội, ta nên làm gì?', OptionA='Đặt mật khẩu "123456"', OptionB='Chia sẻ mật khẩu cho bạn thân', OptionC='Bật xác thực 2 lớp (2FA)', OptionD='Ghi mật khẩu lên màn hình', CorrectOption='C', Difficulty=2),
        
        # --- Mức độ 3: Khó ---
        Exercise(TopicId=topic_mang.Id, Content='Trong Python, kết quả của lệnh print(10 // 3) là bao nhiêu?', OptionA='3.33', OptionB='3', OptionC='4', OptionD='3.0', CorrectOption='B', Difficulty=3),
        Exercise(TopicId=topic_mang.Id, Content='Hành vi nào vi phạm Luật An ninh mạng?', OptionA='Đăng ảnh đi du lịch', OptionB='Chia sẻ thông tin sai sự thật gây hoang mang', OptionC='Bán hàng online', OptionD='Học trực tuyến', CorrectOption='B', Difficulty=3),
    ]

    # BƯỚC 3: Lưu vào Database
    db.session.add_all(new_questions)
    db.session.commit()
    
    print(f"✅ Đã thêm thành công {len(new_questions)} câu hỏi mới!")