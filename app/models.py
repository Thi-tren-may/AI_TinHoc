from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# 1. BẢNG USERS
class User(db.Model, UserMixin):
    __tablename__ = 'Users'
    Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Username = db.Column(db.String, unique=True, nullable=False)
    PasswordHash = db.Column(db.String, nullable=False)
    Role = db.Column(db.String, nullable=False) # 'admin', 'student'
    Grade = db.Column(db.Integer) # 10, 11, 12
    CreatedAt = db.Column(db.String, default=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # Hàm bắt buộc cho Flask-Login (vì bạn đặt tên cột là Id thay vì id)
    def get_id(self):
        return str(self.Id)

# 2. BẢNG TOPICS
class Topic(db.Model):
    __tablename__ = 'Topics'
    Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String, nullable=False)
    ParentId = db.Column(db.Integer, db.ForeignKey('Topics.Id'))
    Level = db.Column(db.String, nullable=False) # 'large', 'small'
    IsActive = db.Column(db.Integer, default=1)

# 3. BẢNG EXERCISES (Câu hỏi)
class Exercise(db.Model):
    __tablename__ = 'Exercises'
    Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    TopicId = db.Column(db.Integer, db.ForeignKey('Topics.Id'), nullable=False)
    Content = db.Column(db.Text, nullable=False)
    OptionA = db.Column(db.Text, nullable=False)
    OptionB = db.Column(db.Text, nullable=False)
    OptionC = db.Column(db.Text, nullable=False)
    OptionD = db.Column(db.Text, nullable=False)
    CorrectOption = db.Column(db.String, nullable=False) # 'A','B','C','D'
    Difficulty = db.Column(db.Integer, nullable=False) # 1, 2, 3
    Grade = db.Column(db.Integer)

# 4. BẢNG EXAMS (Phiên làm bài)
class Exam(db.Model):
    __tablename__ = 'Exams'
    Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserId = db.Column(db.Integer, db.ForeignKey('Users.Id'), nullable=False)
    TopicId = db.Column(db.Integer, db.ForeignKey('Topics.Id'), nullable=False)
    TotalScore = db.Column(db.Float)
    CreatedAt = db.Column(db.String, default=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# 5. BẢNG STUDENTRESULTS (Chi tiết câu trả lời)
class StudentResult(db.Model):
    __tablename__ = 'StudentResults'
    Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ExamId = db.Column(db.Integer, db.ForeignKey('Exams.Id'), nullable=False)
    ExerciseId = db.Column(db.Integer, db.ForeignKey('Exercises.Id'), nullable=False)
    SelectedOption = db.Column(db.String)
    IsCorrect = db.Column(db.Integer) # 0, 1

# 6. BẢNG SKILLPROFILES (Hồ sơ năng lực - S4 dùng)
class SkillProfile(db.Model):
    __tablename__ = 'SkillProfiles'
    Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserId = db.Column(db.Integer, db.ForeignKey('Users.Id'), nullable=False)
    TopicId = db.Column(db.Integer, db.ForeignKey('Topics.Id'), nullable=False)
    Accuracy = db.Column(db.Float)
    SkillLevel = db.Column(db.String) # 'Yeu','TrungBinh','Kha','Tot'
    UpdatedAt = db.Column(db.String, default=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# 7. BẢNG AIREQUESTLOGS (S1 dùng)
class AIRequestLog(db.Model):
    __tablename__ = 'AIRequestLogs'
    Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserId = db.Column(db.Integer, db.ForeignKey('Users.Id'), nullable=False)
    ExerciseId = db.Column(db.Integer, db.ForeignKey('Exercises.Id'), nullable=False)
    Prompt = db.Column(db.Text, nullable=False)
    CreatedAt = db.Column(db.String, default=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))