from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# 题目相关模型
class QuestionBase(BaseModel):
    german_text: str
    chinese_translation: Optional[str] = None
    category: Optional[str] = None
    difficulty: Optional[str] = "medium"
    options: Optional[str] = None
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None

class QuestionCreate(QuestionBase):
    pass

class QuestionUpdate(BaseModel):
    german_text: Optional[str] = None
    chinese_translation: Optional[str] = None
    category: Optional[str] = None
    difficulty: Optional[str] = None
    options: Optional[str] = None
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None

class Question(QuestionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# 词汇相关模型
class VocabularyBase(BaseModel):
    german_word: str
    chinese_translation: Optional[str] = None
    part_of_speech: Optional[str] = None
    difficulty: Optional[str] = "B1"
    example_sentence: Optional[str] = None

class VocabularyCreate(VocabularyBase):
    pass

class VocabularyUpdate(BaseModel):
    german_word: Optional[str] = None
    chinese_translation: Optional[str] = None
    part_of_speech: Optional[str] = None
    difficulty: Optional[str] = None
    example_sentence: Optional[str] = None

class Vocabulary(VocabularyBase):
    id: int
    created_at: datetime
    last_reviewed: Optional[datetime] = None
    review_count: int
    next_review: Optional[datetime] = None

    class Config:
        from_attributes = True

# 学习记录模型
class StudyRecord(BaseModel):
    id: int
    question_id: Optional[int] = None
    vocabulary_id: Optional[int] = None
    is_correct: bool
    review_date: datetime

    class Config:
        from_attributes = True

# 统计模型
class QuestionStats(BaseModel):
    total_questions: int
    categorized_questions: int
    easy_questions: int
    medium_questions: int
    hard_questions: int

class VocabularyStats(BaseModel):
    total_vocabulary: int
    a1_words: int
    a2_words: int
    b1_words: int
    b2_words: int
    c1_words: int
    due_for_review: int

# OCR和翻译模型
class OCRResult(BaseModel):
    german_text: str
    chinese_translation: str
    vocabulary_words: list

class TranslationResult(BaseModel):
    original_text: str
    translated_text: str

class VocabularyWord(BaseModel):
    word: str
    difficulty: str
    suggested_translation: str 