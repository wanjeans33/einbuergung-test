import easyocr
import cv2
import numpy as np
from PIL import Image
import os

class OCRService:
    def __init__(self):
        # 初始化EasyOCR，支持德语
        self.reader = easyocr.Reader(['de'], gpu=False)
    
    def recognize_text(self, image_path: str) -> str:
        """
        识别图片中的德语文本
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            识别出的文本
        """
        try:
            # 读取图片
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("无法读取图片文件")
            
            # 图像预处理
            image = self._preprocess_image(image)
            
            # OCR识别
            results = self.reader.readtext(image)
            
            # 提取文本
            text = ' '.join([result[1] for result in results])
            
            return text.strip()
            
        except Exception as e:
            print(f"OCR识别错误: {e}")
            return ""
    
    def _preprocess_image(self, image):
        """
        图像预处理，提高OCR识别准确率
        """
        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 去噪
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # 自适应阈值处理
        thresh = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # 形态学操作
        kernel = np.ones((1, 1), np.uint8)
        processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        return processed
    
    def get_confidence(self, image_path: str) -> float:
        """
        获取OCR识别的置信度
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            平均置信度
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                return 0.0
            
            image = self._preprocess_image(image)
            results = self.reader.readtext(image)
            
            if not results:
                return 0.0
            
            # 计算平均置信度
            confidences = [result[2] for result in results]
            return sum(confidences) / len(confidences)
            
        except Exception as e:
            print(f"获取置信度错误: {e}")
            return 0.0 