import os
import time

from google import genai
from google.genai import types
from openai import OpenAI


# GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
# GEMINI_MODEL = os.getenv('GEMINI_MODEL')
# gemini_model = genai.Client(api_key=GEMINI_API_KEY)

class LLManager():
    def __init__(self):
        self.GPT_API_KEY = os.getenv('GPT_API_KEY')
        self.GPT_API_URL = os.getenv('GPT_API_URL')
        self.GPT_MODEL = os.getenv('GPT_MODEL')
        self.gpt_model = OpenAI(
            api_key=self.GPT_API_KEY,
            base_url=self.GPT_API_URL
        )

    def translate(self, text):
        if text:
            text = text.strip()
        if not text:
            return ''
        try:
            system_instruction = "你是一位专业、严谨的翻译专家，翻译时严格保留专业术语和原文风格，请将用户输入的文本翻译成中文"
            response = self.gpt_model.chat.completions.create(
                model=self.GPT_MODEL,
                temperature=0.3,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": f"将以下学术内容准确翻译为中文：{text}"}
                ],
                timeout=30  # 添加超时设置
            )
            time.sleep(1) # 礼貌延迟
            if not response.choices:
                return text # 不知道这是什么情况，先用原始内容吧
            return response.choices[0].message.content
        except Exception as e:
            print(f"翻译失败: {str(e)}")
            return "[翻译失败]" + text[: min(len(text), 100)]  # 返回原文前100字符+错误标记


    def analize(self, text):
        if text:
            text = text.strip()
        if not text:
            return ''
        try:
            time.sleep(1)
            system_instruction = "你是一位洞察分析专家，擅长发现信息之间的深层联系，能够提供深刻的见解，请你基于用户提供的信息生成一段行业洞察、趋势分析、商业价值等内容的分析报告，确保内容的深度与广度"
            response = self.gpt_model.chat.completions.create(
                model=self.GPT_MODEL,
                temperature=0.7,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": text}
                ],
                timeout=30  # 添加超时设置
            )
            if not response.choices:
                return text # 不知道这是什么情况，先用原始内容吧
            return response.choices[0].message.content
            response = gemini_model.models.generate_content(
                model=GEMINI_MODEL,
                contents=types.Part.from_text(text=text),
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    max_output_tokens=8192,
                    temperature=0.7,
                ),
            )
            return response.text
        except Exception as e:
            print(f"分析失败: {str(e)}")
            return "[分析失败]"


    def analize_datas(self, datas):
        data_prompt = ''
        for data in datas:
            if 'title_cn' in data:
                data_prompt += data['title_cn']
            
            if 'meta' in data:
                data_prompt += data['meta']

            if 'summary' in data:
                data_prompt += data['summary']
            
            data_prompt += '\n\n'

        return self.analize(data_prompt)
