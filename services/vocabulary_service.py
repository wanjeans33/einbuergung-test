import re
import json
import os
from typing import List, Dict

class VocabularyService:
    def __init__(self):
        # B1词汇表（简化版本，实际应用中应该有完整的词汇表）
        self.b1_vocabulary = self._load_b1_vocabulary()
        
        # 高级词汇特征
        self.advanced_patterns = [
            r'\b[A-Z][a-zäöüß]{8,}\b',  # 长度超过8个字符的单词
            r'\b[A-Z][a-zäöüß]*[tät|ung|heit|keit|schaft|nis]\b',  # 常见后缀
            r'\b[A-Z][a-zäöüß]*[lich|bar|sam|voll|los]\b',  # 形容词后缀
        ]
    
    def _load_b1_vocabulary(self) -> set:
        """
        加载B1词汇表
        这里使用一个简化的词汇表，实际应用中应该从文件或数据库加载
        """
        basic_words = {
            'das', 'der', 'die', 'und', 'in', 'den', 'von', 'mit', 'sich', 'auf',
            'für', 'ist', 'im', 'dem', 'nicht', 'ein', 'eine', 'als', 'auch', 'es',
            'an', 'werden', 'aus', 'er', 'hat', 'dass', 'sie', 'nach', 'wird', 'bei',
            'einer', 'um', 'am', 'noch', 'wie', 'einem', 'über', 'einen', 'so', 'zum',
            'zur', 'zurück', 'nur', 'vor', 'bis', 'mehr', 'durch', 'man', 'sein', 'wird',
            'hier', 'doch', 'einer', 'unter', 'weil', 'soll', 'ich', 'eines', 'es', 'an',
            'auch', 'als', 'da', 'beim', 'seit', 'haben', 'mir', 'gegen', 'vom', 'kann',
            'schon', 'wenn', 'habe', 'ihr', 'dann', 'unter', 'wir', 'sollte', 'etwas',
            'nichts', 'ohne', 'so', 'selbst', 'jetzt', 'da', 'wird', 'schon', 'hier',
            'alle', 'beide', 'dabei', 'seit', 'ihm', 'ihn', 'ihnen', 'ihr', 'ihre',
            'ihrer', 'ihres', 'mein', 'meine', 'meiner', 'meines', 'dein', 'deine',
            'deiner', 'deines', 'sein', 'seine', 'seiner', 'seines', 'unser', 'unsere',
            'unserer', 'unseres', 'euer', 'eure', 'eurer', 'eures', 'ihr', 'ihre',
            'ihrer', 'ihres', 'ihr', 'ihre', 'ihrer', 'ihres'
        }
        return basic_words
    
    def detect_advanced_vocabulary(self, text: str) -> List[Dict]:
        """
        检测文本中的高级词汇
        
        Args:
            text: 德语文本
            
        Returns:
            高级词汇列表
        """
        if not text:
            return []
        
        # 分词
        words = re.findall(r'\b[A-Za-zäöüß]+\b', text)
        advanced_words = []
        
        for word in words:
            word_lower = word.lower()
            
            # 跳过B1基础词汇
            if word_lower in self.b1_vocabulary:
                continue
            
            # 检查是否符合高级词汇特征
            if self._is_advanced_word(word):
                advanced_words.append({
                    'word': word,
                    'difficulty': self._estimate_difficulty(word),
                    'suggested_translation': ''
                })
        
        return advanced_words
    
    def _is_advanced_word(self, word: str) -> bool:
        """
        判断是否为高级词汇
        """
        # 检查长度
        if len(word) < 8:
            return False
        
        # 检查模式匹配
        for pattern in self.advanced_patterns:
            if re.match(pattern, word):
                return True
        
        # 检查是否包含特殊字符（德语特有）
        if any(char in word.lower() for char in ['ä', 'ö', 'ü', 'ß']):
            return True
        
        return False
    
    def _estimate_difficulty(self, word: str) -> str:
        """
        估算词汇难度
        """
        length = len(word)
        
        if length >= 12:
            return 'C1'
        elif length >= 10:
            return 'B2'
        elif length >= 8:
            return 'B1'
        else:
            return 'A2'
    
    def get_vocabulary_stats(self, words: List[str]) -> Dict:
        """
        获取词汇统计信息
        
        Args:
            words: 词汇列表
            
        Returns:
            统计信息字典
        """
        stats = {
            'total': len(words),
            'a1': 0,
            'a2': 0,
            'b1': 0,
            'b2': 0,
            'c1': 0,
            'advanced': 0
        }
        
        for word in words:
            if word.lower() in self.b1_vocabulary:
                stats['b1'] += 1
            elif self._is_advanced_word(word):
                stats['advanced'] += 1
                difficulty = self._estimate_difficulty(word)
                stats[difficulty.lower()] += 1
            else:
                stats['a2'] += 1
        
        return stats
    
    def suggest_translations(self, words: List[str]) -> List[Dict]:
        """
        为词汇提供翻译建议
        这里可以集成翻译API来获取建议翻译
        """
        suggestions = []
        for word in words:
            suggestions.append({
                'word': word,
                'suggested_translation': f'[需要翻译] {word}',
                'difficulty': self._estimate_difficulty(word)
            })
        return suggestions 