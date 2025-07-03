from fastapi import FastAPI, HTTPException, UploadFile, File, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import os
from datetime import datetime
import shutil

from database import engine, Base, Question, Vocabulary, StudyRecord
from schemas import QuestionCreate, QuestionUpdate, VocabularyCreate, VocabularyUpdate
from services.ocr_service import OCRService
from services.translation_service import TranslationService
from services.vocabulary_service import VocabularyService

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="德国入籍考试学习助手",
    description="一个帮助你学习德国入籍考试的应用",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务
if not os.path.exists("uploads"):
    os.makedirs("uploads")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# 初始化服务
ocr_service = OCRService()
translation_service = TranslationService()
vocabulary_service = VocabularyService()

@app.get("/")
async def root():
    return {"message": "德国入籍考试学习助手 API"}

@app.get("/health")
async def health_check():
    return {"status": "OK", "message": "服务运行正常"}

# 题目管理API
@app.get("/api/questions")
async def get_questions(skip: int = 0, limit: int = 50, category: str = None, difficulty: str = None):
    """获取题目列表"""
    from database import get_db
    db = next(get_db())
    return Question.get_questions(db, skip=skip, limit=limit, category=category, difficulty=difficulty)

@app.get("/api/questions/{question_id}")
async def get_question(question_id: int):
    """获取单个题目"""
    from database import get_db
    db = next(get_db())
    question = Question.get_question(db, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    return question

@app.post("/api/questions")
async def create_question(question: QuestionCreate = Body(...)):
    """创建新题目"""
    from database import get_db
    db = next(get_db())
    try:
        db_question = Question.create_question(db, question)
        return db_question
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建题目失败: {str(e)}")

@app.put("/api/questions/{question_id}")
async def update_question(question_id: int, question: QuestionUpdate):
    """更新题目"""
    from database import get_db
    db = next(get_db())
    updated_question = Question.update_question(db, question_id, question)
    if not updated_question:
        raise HTTPException(status_code=404, detail="题目不存在")
    return updated_question

@app.delete("/api/questions/{question_id}")
async def delete_question(question_id: int):
    """删除题目"""
    from database import get_db
    db = next(get_db())
    success = Question.delete_question(db, question_id)
    if not success:
        raise HTTPException(status_code=404, detail="题目不存在")
    return {"message": "删除成功"}

@app.get("/api/questions/stats/summary")
async def get_question_stats():
    """获取题目统计"""
    from database import get_db
    db = next(get_db())
    return Question.get_stats(db)

# 词汇管理API
@app.get("/api/vocabulary")
async def get_vocabulary(skip: int = 0, limit: int = 50, difficulty: str = None):
    """获取词汇列表"""
    from database import get_db
    db = next(get_db())
    return Vocabulary.get_vocabulary(db, skip=skip, limit=limit, difficulty=difficulty)

@app.get("/api/vocabulary/review")
async def get_review_vocabulary(limit: int = 20):
    """获取需要复习的词汇"""
    from database import get_db
    db = next(get_db())
    return Vocabulary.get_review_vocabulary(db, limit=limit)

@app.get("/api/vocabulary/{vocabulary_id}")
async def get_vocabulary_item(vocabulary_id: int):
    """获取单个词汇"""
    from database import get_db
    db = next(get_db())
    vocabulary = Vocabulary.get_vocabulary_item(db, vocabulary_id)
    if not vocabulary:
        raise HTTPException(status_code=404, detail="词汇不存在")
    return vocabulary

@app.post("/api/vocabulary")
async def create_vocabulary(vocabulary: VocabularyCreate = Body(...)):
    """创建新词汇"""
    from database import get_db
    db = next(get_db())
    try:
        db_vocabulary = Vocabulary.create_vocabulary(db, vocabulary)
        return db_vocabulary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建词汇失败: {str(e)}")

@app.put("/api/vocabulary/{vocabulary_id}")
async def update_vocabulary(vocabulary_id: int, vocabulary: VocabularyUpdate):
    """更新词汇"""
    from database import get_db
    db = next(get_db())
    updated_vocabulary = Vocabulary.update_vocabulary(db, vocabulary_id, vocabulary)
    if not updated_vocabulary:
        raise HTTPException(status_code=404, detail="词汇不存在")
    return updated_vocabulary

@app.delete("/api/vocabulary/{vocabulary_id}")
async def delete_vocabulary(vocabulary_id: int):
    """删除词汇"""
    from database import get_db
    db = next(get_db())
    success = Vocabulary.delete_vocabulary(db, vocabulary_id)
    if not success:
        raise HTTPException(status_code=404, detail="词汇不存在")
    return {"message": "删除成功"}

@app.post("/api/vocabulary/{vocabulary_id}/review")
async def record_vocabulary_review(vocabulary_id: int, is_correct: bool):
    """记录词汇复习结果"""
    from database import get_db
    db = next(get_db())
    success = Vocabulary.record_review(db, vocabulary_id, is_correct)
    if not success:
        raise HTTPException(status_code=404, detail="词汇不存在")
    return {"message": "复习记录成功"}

@app.get("/api/vocabulary/stats/summary")
async def get_vocabulary_stats():
    """获取词汇统计"""
    from database import get_db
    db = next(get_db())
    return Vocabulary.get_stats(db)

# OCR和翻译API
@app.post("/api/ocr/process-image")
async def process_image(image: UploadFile = File(...)):
    """处理图片识别和翻译"""
    # 保存上传的图片
    file_path = f"uploads/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{image.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    
    try:
        # OCR识别
        german_text = ocr_service.recognize_text(file_path)
        if not german_text:
            raise HTTPException(status_code=400, detail="无法识别图片中的文本")
        
        # 翻译
        chinese_translation = translation_service.translate(german_text)
        
        # 检测高级词汇
        vocabulary_words = vocabulary_service.detect_advanced_vocabulary(german_text)
        
        return {
            "german_text": german_text,
            "chinese_translation": chinese_translation,
            "vocabulary_words": vocabulary_words
        }
    finally:
        # 清理临时文件
        if os.path.exists(file_path):
            os.remove(file_path)

@app.post("/api/ocr/translate")
async def translate_text(text: str):
    """翻译文本"""
    translation = translation_service.translate(text)
    return {
        "original_text": text,
        "translated_text": translation
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 