from googletrans import Translator
import requests
import json
import time

class TranslationService:
    def __init__(self):
        self.translator = Translator()
        self.fallback_api = "https://api.mymemory.translated.net/get"
        self.last_request_time = 0
        self.request_interval = 1  # 请求间隔，秒
    
    def translate(self, text: str, src_lang: str = 'de', dest_lang: str = 'zh-cn') -> str:
        """
        翻译文本
        
        Args:
            text: 要翻译的文本
            src_lang: 源语言代码
            dest_lang: 目标语言代码
            
        Returns:
            翻译后的文本
        """
        if not text:
            return ""
        
        try:
            # 限制请求频率
            current_time = time.time()
            if current_time - self.last_request_time < self.request_interval:
                time.sleep(self.request_interval - (current_time - self.last_request_time))
            
            # 使用googletrans
            translation = self.translator.translate(text, src=src_lang, dest=dest_lang)
            self.last_request_time = time.time()
            
            if translation and hasattr(translation, 'text'):
                return translation.text
            
            # 如果googletrans失败，尝试使用备用翻译方法
            return self._fallback_translate(text, src_lang, dest_lang)
            
        except Exception as e:
            print(f"翻译错误: {e}")
            # 尝试备用翻译方法
            return self._fallback_translate(text, src_lang, dest_lang)
    
    def _fallback_translate(self, text: str, src_lang: str = 'de', dest_lang: str = 'zh-cn') -> str:
        """
        备用翻译方法
        
        当主要翻译方法失败时使用
        """
        try:
            # 简单的模拟翻译，实际应用中可以使用其他翻译API
            # 这里只是为了演示，返回一个带标记的原文
            return f"[翻译] {text}"
        except Exception as e:
            print(f"备用翻译错误: {e}")
            return f"[无法翻译] {text}"
    
    def batch_translate(self, texts: list, src_lang: str = 'de', dest_lang: str = 'zh-cn') -> list:
        """
        批量翻译文本
        
        Args:
            texts: 要翻译的文本列表
            src_lang: 源语言代码
            dest_lang: 目标语言代码
            
        Returns:
            翻译后的文本列表
        """
        results = []
        for text in texts:
            results.append(self.translate(text, src_lang, dest_lang))
            # 避免请求过于频繁
            time.sleep(self.request_interval)
        return results
    
    def detect_language(self, text: str) -> str:
        """
        检测文本语言
        
        Args:
            text: 要检测的文本
            
        Returns:
            语言代码
        """
        try:
            result = self.translator.detect(text)
            return result.lang
        except Exception as e:
            print(f"语言检测失败: {e}")
            return "unknown" 