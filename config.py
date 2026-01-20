import os

class Config():
    # 常量定义
    SOURCE_ARXIV = 'arxiv'
    SOURCE_HACKER_NEWS = 'hacker_news'
    SOURCE_HUGGINGFACE_PAPERS = 'huggingface_papers'
    SOURCE_TECHCRUNCH = 'tech_crunch'
    SOURCE_GITHUB_TRENDING = 'github_trending'
    SOURCES = [SOURCE_ARXIV, SOURCE_HACKER_NEWS, SOURCE_HUGGINGFACE_PAPERS, SOURCE_TECHCRUNCH, SOURCE_GITHUB_TRENDING]


    def __init__(self):
        self.SMTP_USERNAME = os.getenv('SMTP_USERNAME')
        self.SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
        self.EMAIL_RECIPIENT = os.getenv('EMAIL_RECIPIENT')
        self.GPT_API_KEY = os.getenv('GPT_API_KEY')
        self.GPT_API_URL = os.getenv('GPT_API_URL')
        self.GPT_MODEL = os.getenv('GPT_MODEL')
        self.FETCH_LIMIT = int(os.getenv('FETCH_LIMIT').strip()) if os.getenv('FETCH_LIMIT') else 5
        self.SUBSCRIPTION_SOURCES = os.getenv('SUBSCRIPTION_SOURCES').split(',')
        self.SUBSCRIPTION_SOURCES = [s.strip() for s in self.SUBSCRIPTION_SOURCES if s.strip() in self.SOURCES]
