import os


GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
model = None #genai.Client(api_key=GEMINI_API_KEY)


def translate(text):
    if text:
        text = text.strip()
    if not text:
        return ''
    return text
    try:
        system_instruction = "你是一位专业、严谨的学术翻译助手，翻译时严格保留专业术语和原文风格。"
        prompt = f"{system_instruction}\n请将以下学术内容准确翻译为中文：\n{text}"
        response = model.generate_content(prompt, genai.GenerationConfig(temperature=0.3))
        return response.text
    except Exception as e:
        print(f"翻译失败: {str(e)}")
        return text + " [翻译失败]"  # 返回原文前100字符+错误标记
