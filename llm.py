import os

from google import genai
from google.genai import types


GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
model = genai.Client(api_key=GEMINI_API_KEY)

GEMINI_MODEL = os.getenv('GEMINI_API_KEY')


def translate(text):
    if text:
        text = text.strip()
    if not text:
        return ''
    try:
        system_instruction = "你是一位专业、严谨的学术翻译助手，翻译时严格保留专业术语和原文风格，请将用户输入的文本翻译成中文"
        response = model.models.generate_content(
            model=GEMINI_MODEL,
            contents=types.Part.from_text(text=text),
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                max_output_tokens=1024,
                temperature=0.3,
            ),
        )
        return response.text
    except Exception as e:
        print(f"翻译失败: {str(e)}")
        return text + " [翻译失败]" + text[: min(len(text), 100)]  # 返回原文前100字符+错误标记


def analize(text):
    if text:
        text = text.strip()
    if not text:
        return ''
    try:
        system_instruction = "你是一位洞察翻译助手，翻译时严格保留专业术语和原文风格，请将用户输入的文本翻译成中文"
        response = model.models.generate_content(
            model=GEMINI_MODEL,
            contents=types.Part.from_text(text=text),
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                max_output_tokens=1024,
                temperature=0.3,
            ),
        )
        return response.text
    except Exception as e:
        print(f"翻译失败: {str(e)}")
        return text + " [翻译失败]"  # 返回原文前100字符+错误标记
