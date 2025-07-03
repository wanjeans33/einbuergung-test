import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os

# 配置页面
st.set_page_config(
    page_title="德国入籍考试学习助手",
    page_icon="🇩🇪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API基础URL
API_BASE_URL = "http://localhost:8000"

# 初始化会话状态
if 'show_add_question' not in st.session_state:
    st.session_state.show_add_question = False
if 'show_add_vocabulary' not in st.session_state:
    st.session_state.show_add_vocabulary = False
if 'show_save_question' not in st.session_state:
    st.session_state.show_save_question = False
if 'ocr_result' not in st.session_state:
    st.session_state.ocr_result = None

def main():
    # 侧边栏导航
    st.sidebar.title("🇩🇪 入籍考试助手")
    
    page = st.sidebar.selectbox(
        "选择功能",
        ["📊 仪表板", "📝 题目管理", "📚 词汇本", "🖼️ 图片识别"]
    )
    
    if page == "📊 仪表板":
        show_dashboard()
    elif page == "📝 题目管理":
        show_questions()
    elif page == "📚 词汇本":
        show_vocabulary()
    elif page == "🖼️ 图片识别":
        show_ocr()

def show_dashboard():
    """显示仪表板"""
    st.title("📊 学习仪表板")
    st.markdown("---")
    
    try:
        # 获取统计数据
        question_stats = requests.get(f"{API_BASE_URL}/api/questions/stats/summary").json()
        vocabulary_stats = requests.get(f"{API_BASE_URL}/api/vocabulary/stats/summary").json()
        
        # 统计卡片
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("总题目数", question_stats.get('total_questions', 0))
        
        with col2:
            st.metric("词汇总数", vocabulary_stats.get('total_vocabulary', 0))
        
        with col3:
            st.metric("待复习词汇", vocabulary_stats.get('due_for_review', 0))
        
        with col4:
            st.metric("已分类题目", question_stats.get('categorized_questions', 0))
        
        # 图表
        col1, col2 = st.columns(2)
        
        with col1:
            # 题目难度分布
            difficulty_data = {
                '难度': ['简单', '中等', '困难'],
                '数量': [
                    question_stats.get('easy_questions', 0),
                    question_stats.get('medium_questions', 0),
                    question_stats.get('hard_questions', 0)
                ]
            }
            df_difficulty = pd.DataFrame(difficulty_data)
            fig = px.pie(df_difficulty, values='数量', names='难度', title='题目难度分布')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 词汇水平分布
            level_data = {
                '水平': ['A1', 'A2', 'B1', 'B2', 'C1'],
                '数量': [
                    vocabulary_stats.get('a1_words', 0),
                    vocabulary_stats.get('a2_words', 0),
                    vocabulary_stats.get('b1_words', 0),
                    vocabulary_stats.get('b2_words', 0),
                    vocabulary_stats.get('c1_words', 0)
                ]
            }
            df_level = pd.DataFrame(level_data)
            fig = px.bar(df_level, x='水平', y='数量', title='词汇水平分布')
            st.plotly_chart(fig, use_container_width=True)
        
        # 最近数据
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("最近添加的题目")
            recent_questions = requests.get(f"{API_BASE_URL}/api/questions?limit=5").json()
            if recent_questions:
                for q in recent_questions:
                    st.write(f"• {q['german_text'][:50]}...")
            else:
                st.write("暂无题目")
        
        with col2:
            st.subheader("待复习词汇")
            review_vocab = requests.get(f"{API_BASE_URL}/api/vocabulary/review?limit=5").json()
            if review_vocab:
                for v in review_vocab:
                    st.write(f"• {v['german_word']} ({v['difficulty']})")
            else:
                st.write("暂无待复习词汇")
                
    except Exception as e:
        st.error(f"获取数据失败: {e}")

def show_questions():
    """显示题目管理"""
    st.title("📝 题目管理")
    st.markdown("---")
    
    # 添加题目按钮
    if st.button("➕ 添加新题目"):
        st.session_state.show_add_question = True
    
    if st.session_state.get('show_add_question', False):
        show_add_question_form()
    
    # 题目列表
    st.subheader("题目列表")
    
    try:
        questions = requests.get(f"{API_BASE_URL}/api/questions").json()
        
        if questions:
            # 创建DataFrame
            df = pd.DataFrame(questions)
            df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d')
            
            # 显示表格
            st.dataframe(
                df[['id', 'german_text', 'category', 'difficulty', 'created_at']],
                use_container_width=True
            )
            
            # 题目详情
            selected_id = st.selectbox("选择题目查看详情", df['id'].tolist())
            if selected_id:
                show_question_detail(selected_id)
        else:
            st.info("暂无题目数据")
            
    except Exception as e:
        st.error(f"获取题目失败: {e}")

def show_add_question_form():
    """显示添加题目表单"""
    st.subheader("添加新题目")
    
    with st.form("add_question"):
        german_text = st.text_area("德语文本", height=100)
        chinese_translation = st.text_area("中文翻译", height=100)
        
        col1, col2 = st.columns(2)
        with col1:
            category = st.selectbox("分类", ["一般知识", "历史", "政治", "文化", "地理", "经济", "法律"])
        with col2:
            difficulty = st.selectbox("难度", ["简单", "中等", "困难"])
        
        options = st.text_area("选项（每行一个）")
        correct_answer = st.text_input("正确答案")
        explanation = st.text_area("解释")
        
        submitted = st.form_submit_button("保存题目")
        
        if submitted and german_text:
            try:
                data = {
                    "german_text": german_text,
                    "chinese_translation": chinese_translation,
                    "category": category,
                    "difficulty": difficulty.lower(),
                    "options": options,
                    "correct_answer": correct_answer,
                    "explanation": explanation
                }
                
                response = requests.post(f"{API_BASE_URL}/api/questions", json=data)
                if response.status_code == 200:
                    st.success("题目添加成功！")
                    st.session_state.show_add_question = False
                    st.rerun()
                else:
                    st.error("添加失败")
            except Exception as e:
                st.error(f"添加失败: {e}")

def show_question_detail(question_id):
    """显示题目详情"""
    try:
        question = requests.get(f"{API_BASE_URL}/api/questions/{question_id}").json()
        
        st.subheader("题目详情")
        st.write(f"**德语文本:** {question['german_text']}")
        st.write(f"**中文翻译:** {question['chinese_translation']}")
        st.write(f"**分类:** {question['category']}")
        st.write(f"**难度:** {question['difficulty']}")
        
        if question.get('options'):
            st.write(f"**选项:** {question['options']}")
        if question.get('correct_answer'):
            st.write(f"**正确答案:** {question['correct_answer']}")
        if question.get('explanation'):
            st.write(f"**解释:** {question['explanation']}")
            
    except Exception as e:
        st.error(f"获取题目详情失败: {e}")

def show_vocabulary():
    """显示词汇本"""
    st.title("📚 词汇本")
    st.markdown("---")
    
    # 添加词汇按钮
    if st.button("➕ 添加新词汇"):
        st.session_state.show_add_vocabulary = True
    
    if st.session_state.get('show_add_vocabulary', False):
        show_add_vocabulary_form()
    
    # 复习按钮
    if st.button("📖 开始复习"):
        start_vocabulary_review()
    
    # 词汇列表
    st.subheader("词汇列表")
    
    try:
        vocabulary = requests.get(f"{API_BASE_URL}/api/vocabulary").json()
        
        if vocabulary:
            df = pd.DataFrame(vocabulary)
            df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d')
            
            st.dataframe(
                df[['id', 'german_word', 'chinese_translation', 'difficulty', 'review_count']],
                use_container_width=True
            )
        else:
            st.info("暂无词汇数据")
            
    except Exception as e:
        st.error(f"获取词汇失败: {e}")

def show_add_vocabulary_form():
    """显示添加词汇表单"""
    st.subheader("添加新词汇")
    
    with st.form("add_vocabulary"):
        german_word = st.text_input("德语单词")
        chinese_translation = st.text_input("中文翻译")
        
        col1, col2 = st.columns(2)
        with col1:
            part_of_speech = st.selectbox("词性", ["名词", "动词", "形容词", "副词", "代词", "介词", "连词"])
        with col2:
            difficulty = st.selectbox("难度", ["A1", "A2", "B1", "B2", "C1"])
        
        example_sentence = st.text_area("例句")
        
        submitted = st.form_submit_button("保存词汇")
        
        if submitted and german_word:
            try:
                data = {
                    "german_word": german_word,
                    "chinese_translation": chinese_translation,
                    "part_of_speech": part_of_speech,
                    "difficulty": difficulty,
                    "example_sentence": example_sentence
                }
                
                response = requests.post(f"{API_BASE_URL}/api/vocabulary", json=data)
                if response.status_code == 200:
                    st.success("词汇添加成功！")
                    st.session_state.show_add_vocabulary = False
                    st.rerun()
                else:
                    st.error("添加失败")
            except Exception as e:
                st.error(f"添加失败: {e}")

def start_vocabulary_review():
    """开始词汇复习"""
    try:
        review_words = requests.get(f"{API_BASE_URL}/api/vocabulary/review").json()
        
        if not review_words:
            st.info("没有需要复习的词汇")
            return
        
        st.subheader("词汇复习")
        
        for i, word in enumerate(review_words):
            st.write(f"**{i+1}. {word['german_word']}** ({word['difficulty']})")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"✅ 记得", key=f"correct_{word['id']}"):
                    record_review(word['id'], True)
                    st.success("复习记录成功！")
                    st.rerun()
            
            with col2:
                if st.button(f"❌ 不记得", key=f"incorrect_{word['id']}"):
                    record_review(word['id'], False)
                    st.success("复习记录成功！")
                    st.rerun()
            
            st.write("---")
            
    except Exception as e:
        st.error(f"开始复习失败: {e}")

def record_review(vocabulary_id, is_correct):
    """记录复习结果"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/vocabulary/{vocabulary_id}/review",
            params={"is_correct": is_correct}
        )
        return response.status_code == 200
    except Exception as e:
        st.error(f"记录复习失败: {e}")
        return False

def show_ocr():
    """显示图片识别"""
    st.title("🖼️ 图片识别")
    st.markdown("---")
    
    st.write("上传题目截图，自动识别德语文本并翻译")
    
    uploaded_file = st.file_uploader(
        "选择图片文件",
        type=['png', 'jpg', 'jpeg', 'gif'],
        help="支持PNG、JPG、JPEG、GIF格式"
    )
    
    if uploaded_file is not None:
        # 如果用户上传了新的文件，则重置之前的识别结果和保存表单状态
        file_id = f"{uploaded_file.name}_{uploaded_file.size}"
        if st.session_state.get('uploaded_file_id') != file_id:
            st.session_state.uploaded_file_id = file_id
            st.session_state.ocr_result = None
            st.session_state.show_save_question = False

        # 显示上传的图片
        st.image(uploaded_file, caption="上传的图片", use_column_width=True)
        
        # 如果已经有识别结果，直接展示
        result = st.session_state.get('ocr_result')

        if result:
            st.success("识别成功！")

            # 显示结果
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("德语文本")
                st.write(result['german_text'])

            with col2:
                st.subheader("中文翻译")
                st.write(result['chinese_translation'])

            # 显示检测到的高级词汇
            if result.get('vocabulary_words'):
                st.subheader("检测到的高级词汇")
                for word in result['vocabulary_words']:
                    st.write(f"• {word['word']} ({word['difficulty']})")

            # 始终提供重新识别按钮，便于用户在同一图片上重新识别
            if st.button("🔍 重新识别", key="re_ocr_btn"):
                with st.spinner("正在重新识别图片中的文本..."):
                    try:
                        files = {"image": uploaded_file}
                        response = requests.post(f"{API_BASE_URL}/api/ocr/process-image", files=files)
                        if response.status_code == 200:
                            new_result = response.json()
                            st.session_state.ocr_result = new_result
                            st.session_state.show_save_question = False
                            st.experimental_rerun()
                    except Exception as e:
                        st.error(f"识别失败: {e}")

            # 如果尚未打开保存表单，则显示保存按钮
            if not st.session_state.get('show_save_question'):
                if st.button("💾 保存为题目", key="save_ocr_btn"):
                    st.session_state.show_save_question = True
                    st.experimental_rerun()
        else:
            # 还没有识别结果，显示识别按钮
            if st.button("🔍 开始识别"):
                with st.spinner("正在识别图片中的文本..."):
                    try:
                        # 发送图片到API
                        files = {"image": uploaded_file}
                        response = requests.post(f"{API_BASE_URL}/api/ocr/process-image", files=files)

                        if response.status_code == 200:
                            result = response.json()

                            # 保存结果到会话状态并重新运行，以便显示结果
                            st.session_state.ocr_result = result
                            st.experimental_rerun()
                    except Exception as e:
                        st.error(f"识别失败: {e}")
    
    # 保存题目表单
    if st.session_state.get('show_save_question', False):
        show_save_ocr_question()

def show_save_ocr_question():
    """显示保存OCR结果的表单"""
    st.subheader("保存为题目")
    
    result = st.session_state.get('ocr_result', {})
    st.write(f"调试信息 - OCR结果: {result}")
    
    with st.form("save_ocr_question"):
        german_text = st.text_area("德语文本", value=result.get('german_text', ''))
        chinese_translation = st.text_area("中文翻译", value=result.get('chinese_translation', ''))
        
        col1, col2 = st.columns(2)
        with col1:
            category = st.selectbox("分类", ["一般知识", "历史", "政治", "文化", "地理", "经济", "法律"])
        with col2:
            difficulty = st.selectbox("难度", ["简单", "中等", "困难"])
        
        options = st.text_area("选项（每行一个）")
        correct_answer = st.text_input("正确答案")
        explanation = st.text_area("解释")
        
        # 添加选项：是否保存检测到的词汇
        save_vocabulary = st.checkbox("同时将检测到的词汇保存到词汇库", value=True)
        
        submitted = st.form_submit_button("保存题目")
        
        if submitted:
            try:
                # 1. 保存题目
                data = {
                    "german_text": german_text,
                    "chinese_translation": chinese_translation,
                    "category": category,
                    "difficulty": difficulty.lower(),
                    "options": options,
                    "correct_answer": correct_answer,
                    "explanation": explanation
                }
                
                st.write(f"调试信息 - 发送数据: {data}")
                
                response = requests.post(f"{API_BASE_URL}/api/questions", json=data)
                st.write(f"调试信息 - 响应状态码: {response.status_code}")
                st.write(f"调试信息 - 响应内容: {response.text}")
                
                if response.status_code == 200:
                    st.success("题目保存成功！")
                    
                    # 2. 如果选择了保存词汇，则保存检测到的词汇
                    if save_vocabulary and result.get('vocabulary_words'):
                        saved_vocab_count = 0
                        for word_info in result.get('vocabulary_words', []):
                            try:
                                # 检查词汇是否已存在
                                vocab_data = {
                                    "german_word": word_info['word'],
                                    "chinese_translation": word_info.get('suggested_translation', ''),
                                    "difficulty": word_info['difficulty'],
                                    "part_of_speech": "未知"
                                }
                                
                                st.write(f"调试信息 - 保存词汇: {vocab_data}")
                                
                                # 发送请求保存词汇
                                vocab_response = requests.post(f"{API_BASE_URL}/api/vocabulary", json=vocab_data)
                                st.write(f"调试信息 - 词汇响应: {vocab_response.status_code}")
                                
                                if vocab_response.status_code == 200:
                                    saved_vocab_count += 1
                            except Exception as e:
                                st.error(f"保存词汇失败: {e}")
                                print(f"保存词汇失败: {e}")
                        
                        if saved_vocab_count > 0:
                            st.success(f"成功保存 {saved_vocab_count} 个词汇到词汇库！")
                    
                    # 表单内不能有带回调的普通按钮；保存成功后在表单之外提供"返回"按钮
                else:
                    st.error(f"保存失败: {response.status_code}")
                    st.error(response.text)
            except Exception as e:
                st.error(f"保存失败: {e}")
                import traceback
                st.error(traceback.format_exc())

    # 表单区域结束后，统一放置"返回"按钮（不在表单上下文内，避免 Streamlit 回调限制）
    if st.button("返回"):
        clear_session_and_return()

def clear_session_and_return():
    """清理会话状态并返回"""
    st.session_state.show_save_question = False
    st.session_state.ocr_result = None
    st.experimental_rerun()

if __name__ == "__main__":
    main() 