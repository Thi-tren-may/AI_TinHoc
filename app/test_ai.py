from app.ai_logic import LearningAnalytics, get_ai_explanation

def test_learning_analytics():
    la = LearningAnalytics()
    user_id = 1  # ID test trong DB

    report = la.generate_full_report(user_id)

    print("📊 TREND:", report["trend"])
    print("🕳 GAP:", report["gaps"])
    print("🧠 COGNITIVE:", report["cognitive"])

def test_ai_explanation():
    reply = get_ai_explanation(
        user_id=1,
        exercise_id=101,
        question="Thuật toán là gì?",
        student_choice="Là ngôn ngữ lập trình",
        correct_answer="Là dãy hữu hạn các bước giải quyết vấn đề"
    )
    print("🤖 AI EXPLANATION:")
    print(reply)

if __name__ == "__main__":
    test_learning_analytics()
    test_ai_explanation()
