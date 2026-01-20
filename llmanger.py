import os
import time

from config import AppConfig

from google import genai
from google.genai import types
from openai import OpenAI
from utils import log_cost


class LLManager():
    def __init__(self, config: AppConfig):
        self.model_name = config.model.name
        self.model = OpenAI(
            api_key=config.model.api_key,
            base_url=config.model.api_url
        )
        self.call_interval = config.model.call_interval

    def translate(self, text: str) -> str:
        """
        将文本翻译为中文
        
        Args:
            text: 需要翻译的文本
            
        Returns:
            翻译后的文本，如果失败则返回带有错误标记的原文
        """
        if not text:
            return ''
        text = text.strip()
        if not text:
            return ''
            
        try:
            system_instruction = "你是一位专业、严谨的翻译专家，翻译时严格保留专业术语和原文风格，请将用户输入的文本翻译成中文"
            response = self.model.chat.completions.create(
                model=self.model_name,
                temperature=0.3,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": f"将以下学术内容准确翻译为中文：{text}"}
                ],
                timeout=30
            )
            time.sleep(self.call_interval)  # 礼貌延迟
            if not response.choices:
                return text
            return response.choices[0].message.content
        except Exception as e:
            print(f"翻译失败: {str(e)}")
            return "[翻译失败]" + text[:min(len(text), 100)]  # 返回原文前100字符+错误标记


    def analyze(self, text: str) -> str:
        """
        分析文本并生成行业洞察报告
        
        Args:
            text: 需要分析的文本
            
        Returns:
            分析报告，如果失败则返回带有错误标记的文本
        """
        if not text:
            return ''
        text = text.strip()
        if not text:
            return ''
            
        try:
            system_instruction = """你是一位洞察分析专家，擅长发现信息之间的深层联系，提供深刻的见解
请你基于用户提供的信息生成一段行业洞察、趋势分析、商业价值等内容的分析报告，确保内容的深度与广度，**纯文本输出不要含有任何格式，例如Markdown**，字数控制在1000字以内"""
            response = self.model.chat.completions.create(
                model=self.model_name,
                temperature=0.7,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": text}
                ],
                timeout=30
            )
            time.sleep(self.call_interval)  # 礼貌延迟
            if not response.choices:
                return text
            return response.choices[0].message.content
        except Exception as e:
            print(f"分析失败: {str(e)}")
            return "[分析失败]"


    @log_cost
    def analyze_datas(self, datas: list) -> str:
        """
        分析多个数据项并生成综合报告
        
        Args:
            datas: 包含文章信息的字典列表
            
        Returns:
            综合分析报告
        """
        data_prompt = ''
        for data in datas:
            if 'title_cn' in data:
                data_prompt += data['title_cn']
            
            if 'meta' in data:
                data_prompt += data['meta']

            if 'summary' in data:
                data_prompt += data['summary']
            
            data_prompt += '\n\n'

        return self.analyze(data_prompt)
