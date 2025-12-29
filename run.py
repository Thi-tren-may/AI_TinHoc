from app import create_app, db

# 1. Khởi tạo ứng dụng từ factory
app = create_app()

if __name__ == '__main__':
    # 2. Tạo ngữ cảnh ứng dụng (App Context) để Flask làm việc với Database
    with app.app_context():
        # Tự động tạo file .db và các bảng nếu chúng chưa tồn tại
        db.create_all()
        print("--- Database đã được khởi tạo/kiểm tra thành công! ---")

    # 3. Chạy server ở chế độ Debug
    app.run(debug=True)