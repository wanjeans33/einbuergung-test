#!/usr/bin/env python3
"""
测试脚本 - 验证应用功能
"""

import requests
import json
import time

# API基础URL
API_BASE_URL = "http://localhost:8000"

def test_health():
    """测试健康检查"""
    print("🔍 测试健康检查...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ 健康检查通过")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
        return False

def test_questions_api():
    """测试题目API"""
    print("\n📝 测试题目API...")
    
    # 创建测试题目
    test_question = {
        "german_text": "Was ist die Hauptstadt von Deutschland?",
        "chinese_translation": "德国的首都是什么？",
        "category": "地理",
        "difficulty": "简单",
        "options": "Berlin\nMünchen\nHamburg\nKöln",
        "correct_answer": "Berlin",
        "explanation": "柏林是德国的首都"
    }
    
    try:
        # 创建题目
        response = requests.post(f"{API_BASE_URL}/api/questions", json=test_question)
        if response.status_code == 200:
            question_id = response.json()['id']
            print(f"✅ 创建题目成功，ID: {question_id}")
            
            # 获取题目列表
            response = requests.get(f"{API_BASE_URL}/api/questions")
            if response.status_code == 200:
                questions = response.json()
                print(f"✅ 获取题目列表成功，共 {len(questions)} 个题目")
            
            # 获取题目统计
            response = requests.get(f"{API_BASE_URL}/api/questions/stats/summary")
            if response.status_code == 200:
                stats = response.json()
                print(f"✅ 获取题目统计成功: {stats}")
            
            return True
        else:
            print(f"❌ 创建题目失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 题目API测试异常: {e}")
        return False

def test_vocabulary_api():
    """测试词汇API"""
    print("\n📚 测试词汇API...")
    
    # 创建测试词汇
    test_vocabulary = {
        "german_word": "Einbürgerung",
        "chinese_translation": "入籍",
        "part_of_speech": "名词",
        "difficulty": "B2",
        "example_sentence": "Die Einbürgerung ist ein wichtiger Schritt."
    }
    
    try:
        # 创建词汇
        response = requests.post(f"{API_BASE_URL}/api/vocabulary", json=test_vocabulary)
        if response.status_code == 200:
            vocab_id = response.json()['id']
            print(f"✅ 创建词汇成功，ID: {vocab_id}")
            
            # 获取词汇列表
            response = requests.get(f"{API_BASE_URL}/api/vocabulary")
            if response.status_code == 200:
                vocabulary = response.json()
                print(f"✅ 获取词汇列表成功，共 {len(vocabulary)} 个词汇")
            
            # 获取词汇统计
            response = requests.get(f"{API_BASE_URL}/api/vocabulary/stats/summary")
            if response.status_code == 200:
                stats = response.json()
                print(f"✅ 获取词汇统计成功: {stats}")
            
            return True
        else:
            print(f"❌ 创建词汇失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 词汇API测试异常: {e}")
        return False

def test_translation():
    """测试翻译功能"""
    print("\n🌐 测试翻译功能...")
    
    test_text = "Guten Tag! Wie geht es Ihnen?"
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/ocr/translate",
            params={"text": test_text}
        )
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 翻译成功")
            print(f"原文: {result['original_text']}")
            print(f"译文: {result['translated_text']}")
            return True
        else:
            print(f"❌ 翻译失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 翻译测试异常: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 开始测试德国入籍考试学习助手")
    print("=" * 50)
    
    # 等待服务启动
    print("⏳ 等待服务启动...")
    time.sleep(3)
    
    # 运行测试
    tests = [
        test_health,
        test_questions_api,
        test_vocabulary_api,
        test_translation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        time.sleep(1)
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！应用运行正常。")
    else:
        print("⚠️ 部分测试失败，请检查服务状态。")
    
    print("\n🌐 前端界面: http://localhost:8501")
    print("🔧 API文档: http://localhost:8000/docs")

if __name__ == "__main__":
    main() 