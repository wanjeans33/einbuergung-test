from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# 数据库配置
SQLALCHEMY_DATABASE_URL = "sqlite:///./einbuergung.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 数据库依赖
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 数据库模型
class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    german_text = Column(Text, nullable=False)
    chinese_translation = Column(Text)
    category = Column(String(50))
    difficulty = Column(String(20), default="medium")
    options = Column(Text)
    correct_answer = Column(String(200))
    explanation = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    study_records = relationship("StudyRecord", back_populates="question")

    @classmethod
    def get_questions(cls, db, skip: int = 0, limit: int = 50, category: str = None, difficulty: str = None):
        query = db.query(cls)
        if category:
            query = query.filter(cls.category == category)
        if difficulty:
            query = query.filter(cls.difficulty == difficulty)
        return query.offset(skip).limit(limit).all()

    @classmethod
    def get_question(cls, db, question_id: int):
        return db.query(cls).filter(cls.id == question_id).first()

    @classmethod
    def create_question(cls, db, question_data):
        db_question = cls(**question_data.dict())
        db.add(db_question)
        db.commit()
        db.refresh(db_question)
        return db_question

    @classmethod
    def update_question(cls, db, question_id: int, question_data):
        db_question = db.query(cls).filter(cls.id == question_id).first()
        if db_question:
            for key, value in question_data.dict(exclude_unset=True).items():
                setattr(db_question, key, value)
            db_question.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(db_question)
        return db_question

    @classmethod
    def delete_question(cls, db, question_id: int):
        db_question = db.query(cls).filter(cls.id == question_id).first()
        if db_question:
            db.delete(db_question)
            db.commit()
            return True
        return False

    @classmethod
    def get_stats(cls, db):
        from sqlalchemy import func
        total = db.query(func.count(cls.id)).scalar()
        categorized = db.query(func.count(cls.id)).filter(cls.category.isnot(None)).scalar()
        easy = db.query(func.count(cls.id)).filter(cls.difficulty == "easy").scalar()
        medium = db.query(func.count(cls.id)).filter(cls.difficulty == "medium").scalar()
        hard = db.query(func.count(cls.id)).filter(cls.difficulty == "hard").scalar()
        
        return {
            "total_questions": total,
            "categorized_questions": categorized,
            "easy_questions": easy,
            "medium_questions": medium,
            "hard_questions": hard
        }

class Vocabulary(Base):
    __tablename__ = "vocabulary"

    id = Column(Integer, primary_key=True, index=True)
    german_word = Column(String(100), nullable=False)
    chinese_translation = Column(String(200))
    part_of_speech = Column(String(50))
    difficulty = Column(String(10), default="B1")
    example_sentence = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_reviewed = Column(DateTime)
    review_count = Column(Integer, default=0)
    next_review = Column(DateTime)

    # 关系
    study_records = relationship("StudyRecord", back_populates="vocabulary")

    @classmethod
    def get_vocabulary(cls, db, skip: int = 0, limit: int = 50, difficulty: str = None):
        query = db.query(cls)
        if difficulty:
            query = query.filter(cls.difficulty == difficulty)
        return query.offset(skip).limit(limit).all()

    @classmethod
    def get_review_vocabulary(cls, db, limit: int = 20):
        from sqlalchemy import or_
        return db.query(cls).filter(
            or_(cls.next_review.is_(None), cls.next_review <= datetime.utcnow())
        ).order_by(cls.last_reviewed.asc().nullsfirst()).limit(limit).all()

    @classmethod
    def get_vocabulary_item(cls, db, vocabulary_id: int):
        return db.query(cls).filter(cls.id == vocabulary_id).first()

    @classmethod
    def create_vocabulary(cls, db, vocabulary_data):
        # 检查是否已存在相同的德语单词
        existing = db.query(cls).filter(cls.german_word == vocabulary_data.german_word).first()
        if existing:
            # 如果已存在，更新翻译和其他信息（如果新数据有提供）
            for key, value in vocabulary_data.dict(exclude_unset=True).items():
                if value and key != 'german_word':  # 不更新德语单词本身
                    setattr(existing, key, value)
            db.commit()
            db.refresh(existing)
            return existing
        
        # 如果不存在，创建新词汇
        db_vocabulary = cls(**vocabulary_data.dict())
        db.add(db_vocabulary)
        db.commit()
        db.refresh(db_vocabulary)
        return db_vocabulary

    @classmethod
    def update_vocabulary(cls, db, vocabulary_id: int, vocabulary_data):
        db_vocabulary = db.query(cls).filter(cls.id == vocabulary_id).first()
        if db_vocabulary:
            for key, value in vocabulary_data.dict(exclude_unset=True).items():
                setattr(db_vocabulary, key, value)
            db.commit()
            db.refresh(db_vocabulary)
        return db_vocabulary

    @classmethod
    def delete_vocabulary(cls, db, vocabulary_id: int):
        db_vocabulary = db.query(cls).filter(cls.id == vocabulary_id).first()
        if db_vocabulary:
            db.delete(db_vocabulary)
            db.commit()
            return True
        return False

    @classmethod
    def record_review(cls, db, vocabulary_id: int, is_correct: bool):
        from datetime import timedelta
        db_vocabulary = db.query(cls).filter(cls.id == vocabulary_id).first()
        if db_vocabulary:
            db_vocabulary.last_reviewed = datetime.utcnow()
            db_vocabulary.review_count += 1
            
            # 间隔重复算法
            if is_correct:
                intervals = [1, 3, 7, 14, 30, 90]  # 天数
                interval_index = min(db_vocabulary.review_count - 1, len(intervals) - 1)
                days = intervals[interval_index]
                db_vocabulary.next_review = datetime.utcnow() + timedelta(days=days)
            else:
                db_vocabulary.next_review = datetime.utcnow() + timedelta(days=1)
            
            # 记录学习记录
            study_record = StudyRecord(
                vocabulary_id=vocabulary_id,
                is_correct=is_correct
            )
            db.add(study_record)
            db.commit()
            return True
        return False

    @classmethod
    def get_stats(cls, db):
        from sqlalchemy import func
        total = db.query(func.count(cls.id)).scalar()
        a1_words = db.query(func.count(cls.id)).filter(cls.difficulty == "A1").scalar()
        a2_words = db.query(func.count(cls.id)).filter(cls.difficulty == "A2").scalar()
        b1_words = db.query(func.count(cls.id)).filter(cls.difficulty == "B1").scalar()
        b2_words = db.query(func.count(cls.id)).filter(cls.difficulty == "B2").scalar()
        c1_words = db.query(func.count(cls.id)).filter(cls.difficulty == "C1").scalar()
        due_for_review = db.query(func.count(cls.id)).filter(
            cls.next_review <= datetime.utcnow()
        ).scalar()
        
        return {
            "total_vocabulary": total,
            "a1_words": a1_words,
            "a2_words": a2_words,
            "b1_words": b1_words,
            "b2_words": b2_words,
            "c1_words": c1_words,
            "due_for_review": due_for_review
        }

class StudyRecord(Base):
    __tablename__ = "study_records"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"))
    vocabulary_id = Column(Integer, ForeignKey("vocabulary.id"))
    is_correct = Column(Boolean)
    review_date = Column(DateTime, default=datetime.utcnow)

    # 关系
    question = relationship("Question", back_populates="study_records")
    vocabulary = relationship("Vocabulary", back_populates="study_records") 