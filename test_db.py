import os
from sqlalchemy import text, inspect
from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    print("\n--- BẮT ĐẦU KIỂM TRA CHI TIẾT ---")
    
    # 1. Kiểm tra các bảng đang thực sự tồn tại trong file .db
    try:
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"1. Các bảng tìm thấy trong file: {tables}")
    except Exception as e:
        print(f"1. Không thể lấy danh sách bảng: {e}")

    # 2. Thử đếm dữ liệu bằng SQL thuần (không dùng Model)
    # Lưu ý: Chữ 'Users' phải viết đúng như trong danh sách in ra ở bước 1
    try:
        # Thử với 'Users' (có s)
        res = db.session.execute(text("SELECT count(*) FROM Users")).scalar()
        print(f"2. Số dòng trong bảng 'Users' (SQL thuần): {res}")
    except Exception as e:
        print(f"2. Lỗi khi truy vấn SQL thuần bảng 'Users': {e}")

    # 3. Kiểm tra Model Python có khớp không
    try:
        count = User.query.count()
        print(f"3. Số dòng đếm qua Model 'User': {count}")
    except Exception as e:
        print(f"3. Lỗi khi dùng Model (có thể do sai tên cột): {e}")