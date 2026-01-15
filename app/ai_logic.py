import google.generativeai as genai
import os
from dotenv import load_dotenv
import sqlite3
from collections import Counter

# ===============================================================
# CẤU HÌNH BAN ĐẦU
# ===============================================================
load_dotenv() # Nạp biến môi trường từ file .env (chứa API Key)
genai.configure(api_key=os.getenv("GEMINI_API_KEY")) # Xác thực với Google

MODEL_NAME = 'models/gemini-2.5-flash' # Tên mô hình AI sử dụng
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)   # đi lên thư mục gốc DA_TinHocTHPT
DB_PATH = os.path.join(PROJECT_DIR, "database", "app.db")       # Đường dẫn cơ sở dữ liệu

# ===============================================================
# TẦNG AI LỚP 2: PHÂN TÍCH TIẾN ĐỘ (DÙNG SQL & LOGIC)
# Nhiệm vụ: Biến số liệu thô thành lời khuyên cho trang tiến độ học tập
# ===============================================================
class LearningAnalytics:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path

    def _get_connection(self):
        """Hàm phụ: Tạo kết nối và cho phép truy xuất dữ liệu theo tên cột"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # --- HÀM 1: PHÂN TÍCH PHONG ĐỘ (TREND) ---
    def get_score_trend(self, user_id):
        """
        Logic: Lấy điểm bài mới nhất trừ bài kề trước.
        Mở rộng: Có thể tính trung bình 3 bài gần nhất so với 3 bài trước đó để chính xác hơn.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        # Lấy điểm 5 bài gần nhất, bài mới nhất nằm ở đầu danh sách
        cursor.execute("SELECT TotalScore FROM Exams WHERE UserId = ? ORDER BY CreatedAt DESC LIMIT 5", (user_id,))
        scores = [row['TotalScore'] for row in cursor.fetchall()]
        conn.close()

        if len(scores) < 2:
            return "Cần làm tối thiểu 2 bài để phân tích xu hướng."

        latest = scores[0]    # Bài vừa làm xong
        previous = scores[1]  # Bài làm trước đó
        diff = latest - previous

        if diff > 1.0: 
            return f"Xu hướng tăng mạnh (+{diff}đ). Bạn đang hấp thụ kiến thức rất tốt!"
        elif diff < -1.0:
            return f"Xu hướng giảm ({diff}đ). Hãy kiểm tra lại các phần kiến thức mới học."
        return "Phong độ ổn định. Hãy tiếp tục duy trì đà học tập này."

    # --- HÀM 2: TÌM LỖ HỔNG KIẾN THỨC (GAP DETECTION) ---
    def get_knowledge_gaps(self, user_id):
        """
        Logic: Tìm các chủ đề (Topic) mà học sinh làm sai nhiều nhất (IsCorrect = 0).
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        # Truy vấn kết hợp (JOIN) 4 bảng: Kết quả bài làm -> Câu hỏi -> Chủ đề -> Bài thi
        cursor.execute("""
            SELECT T.Name FROM StudentResults SR
            JOIN Exercises E ON SR.ExerciseId = E.Id
            JOIN Topics T ON E.TopicId = T.Id
            JOIN Exams EX ON SR.ExamId = EX.Id
            WHERE EX.UserId = ? AND SR.IsCorrect = 0
            ORDER BY EX.CreatedAt DESC LIMIT 40
        """, (user_id,))
        
        wrong_topics = [row['Name'] for row in cursor.fetchall()]
        conn.close()

        if not wrong_topics:
            return "Tuyệt vời! Hiện tại không phát hiện lỗ hổng kiến thức nào."

        # Đếm số lần sai của từng chủ đề
        occurence = Counter(wrong_topics)
        # Lấy 2 chủ đề sai nhiều nhất
        most_wrong = occurence.most_common(2) 

        # Nếu sai >= 3 lần mới coi là hổng kiến thức thực sự (tránh sai sót ngẫu nhiên)
        gaps = [f"{topic} (sai {count} lần)" for topic, count in most_wrong if count >= 3]

        if gaps:
            return "Lỗ hổng cần vá: " + ", ".join(gaps)
        return "Bạn chỉ sai vài câu nhỏ lẻ, chưa tạo thành lỗ hổng hệ thống."

    # --- HÀM 3: PHÂN TÍCH TƯ DUY (COGNITIVE LEVEL) ---
    def get_cognitive_analysis(self, user_id):
        """
        Logic: Tính tỷ lệ đúng trung bình theo độ khó (Difficulty).
        Difficulty: 1 (Nhận biết), 2 (Thông hiểu), 3 (Vận dụng).
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT E.Difficulty, AVG(SR.IsCorrect) as Accuracy
            FROM StudentResults SR
            JOIN Exercises E ON SR.ExerciseId = E.Id
            JOIN Exams EX ON SR.ExamId = EX.Id
            WHERE EX.UserId = ?
            GROUP BY E.Difficulty
        """, (user_id,))
        
        # Chuyển kết quả thành từ điển để dễ so sánh: {1: 0.85, 2: 0.40...}
        results = {row['Difficulty']: row['Accuracy'] for row in cursor.fetchall()}
        conn.close()

        easy = results.get(1, 0)   # Tỷ lệ đúng câu Nhận biết
        medium = results.get(2, 0) # Tỷ lệ đúng câu Thông hiểu
        hard = results.get(3, 0)   # Tỷ lệ đúng câu Vận dụng

        if easy < 0.6:
            return "Kiến thức nền (Nhận biết) còn yếu. Bạn nên đọc lại SGK kỹ hơn."
        if medium < 0.5:
            return "Bạn hiểu bài nhưng chưa sâu (Thông hiểu). Cần làm thêm các ví dụ minh họa."
        if hard < 0.4:
            return "Kỹ năng Vận dụng còn hạn chế. Hãy tập trung giải các bài toán thực tế."
        return "Khả năng tư duy các cấp độ của bạn rất đồng đều."

    def generate_full_report(self, user_id):
        """Hàm tổng hợp để API gọi 1 lần lấy được tất cả phân tích"""
        return {
            "trend": self.get_score_trend(user_id),
            "gaps": self.get_knowledge_gaps(user_id),
            "cognitive": self.get_cognitive_analysis(user_id)
        }

# ===============================================================
# TẦNG AI LỚP 3: GIẢI THÍCH CHI TIẾT (DÙNG GOOGLE GEMINI)
# Nhiệm vụ: Trả lời câu hỏi tại sao sai cho học sinh (S4)
# ===============================================================

def check_ai_usage(user_id, limit=20):
    """
    Hàm kiểm soát chi phí: Giới hạn số lượt gọi AI thực tế trong 1 ngày.
    Lấy ngày hiện tại (date('now')) để đếm số bản ghi mới trong bảng Logs.
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM AIRequestLogs 
            WHERE UserId = ? AND date(CreatedAt) = date('now')
        """, (user_id,))
        count = cursor.fetchone()[0]
        return count < limit, count
    except: return True, 0 # Nếu lỗi DB, mặc định cho phép dùng
    finally:
        if conn: conn.close()

def get_ai_explanation(user_id, exercise_id, question, student_choice, correct_answer):
    """
    Hàm lõi gọi AI: Có cơ chế Cache (Lưu trữ cũ) để tiết kiệm API.
    """
    if not question: return "Dữ liệu câu hỏi trống."
    
    conn = None
    # --- BƯỚC 1: KIỂM TRA BỘ NHỚ ĐỆM (CACHE) ---
    # Nếu câu này đã được giải thích cho User này trước đó, lấy luôn từ DB ra.
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Prompt FROM AIRequestLogs 
            WHERE UserId=? AND ExerciseId=? 
            ORDER BY CreatedAt DESC LIMIT 1
        """, (user_id, exercise_id))
        row = cursor.fetchone()
        if row: return row['Prompt'] # Trả về lời giải cũ ngay lập tức
    except Exception as e: print(f"Lỗi Cache: {e}")
    finally:
        if conn: conn.close()

    # --- BƯỚC 2: KIỂM TRA HẠN MỨC NGÀY ---
    can_use, _ = check_ai_usage(user_id)
    if not can_use: 
        return "Bạn đã hết 20 lượt dùng AI mới trong ngày. Hãy xem lại các câu cũ đã giải nhé!"

    # --- BƯỚC 3: GỌI GOOGLE AI ---
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        # Prompt (Lời nhắc): Quyết định độ thông minh và giọng văn của AI
        # Prompt (Lời nhắc) phiên bản "Siêu ngắn gọn"
        prompt = f"""
        Bạn là gia sư Tin học vui tính. Hãy giải thích CỰC NGẮN (tối đa 3 dòng) cho học sinh:
        
        - Câu hỏi: "{question}"
        - Học sinh chọn sai: "{student_choice}"
        - Đáp án đúng: "{correct_answer}"

        Yêu cầu bắt buộc:
        1. ❌ Tại sao câu học sinh chọn lại sai? (1 câu ngắn).
        2. ✅ Tại sao đáp án kia mới đúng? (1 câu ngắn).
        3. Dùng icon (💡, 🚫, ✅) đầu dòng cho dễ đọc. Không chào hỏi rườm rà.
        """
        
        response = model.generate_content(prompt)
        ai_reply = response.text

        # --- BƯỚC 4: LƯU LẠI NHẬT KÝ (Ghi Log) ---
        # Bọc try riêng: Nếu lưu vào DB thất bại, vẫn phải trả về ai_reply cho học sinh
        try:
            conn_log = sqlite3.connect(DB_PATH) # Tạo kết nối riêng tên là conn_log
            cursor_log = conn_log.cursor()
            cursor_log.execute("""
                INSERT INTO AIRequestLogs (UserId, ExerciseId, Prompt) 
                VALUES (?, ?, ?)
            """, (user_id, exercise_id, ai_reply))
            conn_log.commit()
            conn_log.close() # Đóng cửa conn_log ngay lập tức
        except Exception as log_error:
            # Chỉ in lỗi ra màn hình đen (terminal) để mình biết, không báo cho học sinh
            print(f"⚠️ Lỗi lưu Log: {log_error}")
        
        # TRẢ VỀ KẾT QUẢ: Dù lưu log thành công hay thất bại, học sinh vẫn nhận được lời giải
        return ai_reply

    except Exception as e:
        # Lỗi này mới là lỗi nặng (mất mạng, hết tiền API...), lúc này mới báo AI bận
        return f"Đáp án đúng là: {correct_answer}. (Hiện tại AI đang bận, bạn vui lòng xem lại SGK nhé!)"
