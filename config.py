import os

class Config():
    # 常量定义
    SOURCE_ARXIV = 'arxiv'
    SOURCE_HACKER_NEWS = 'hacker_news'
    SOURCE_HUGGINGFACE_PAPERS = 'huggingface_papers'
    SOURCE_TECHCRUNCH = 'tech_crunch'
    SOURCE_GITHUB_TRENDING = 'github_trending'
    SOURCES = [SOURCE_ARXIV, SOURCE_HACKER_NEWS, SOURCE_HUGGINGFACE_PAPERS, SOURCE_TECHCRUNCH, SOURCE_GITHUB_TRENDING]

    # 推送目标
    PUSH_ENDPOINT_EMAIL = 'email'
    PUSH_ENDPOINT_WECHAT = 'wechat'
    PUSH_ENDPOINTS = [PUSH_ENDPOINT_EMAIL, PUSH_ENDPOINT_WECHAT]


    def __init__(self):
        # SMTP 配置
        self.SMTP_SERVER = os.getenv('SMTP_SERVER')
        self.SMTP_SENDER = os.getenv('SMTP_SENDER')
        self.SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
        self.SMTP_RECEIVER = os.getenv('SMTP_RECEIVER')

        # 企业微信配置
        self.WECHAT_WEBHOOK_URL = os.getenv('WECHAT_WEBHOOK_URL')

        # 推送配置
        self.PUSH_ENDPOINT = os.getenv('PUSH_ENDPOINT').split(',')
        self.PUSH_ENDPOINT = [s.strip() for s in self.PUSH_ENDPOINT if s.strip() in self.PUSH_ENDPOINTS]

        # 模型配置
        self.GPT_API_KEY = os.getenv('GPT_API_KEY')
        self.GPT_API_URL = os.getenv('GPT_API_URL')
        self.GPT_MODEL = os.getenv('GPT_MODEL')

        # 抓取配置
        self.FETCH_LIMIT = int(os.getenv('FETCH_LIMIT').strip()) if os.getenv('FETCH_LIMIT') else 5
        self.SUBSCRIPTION_SOURCES = os.getenv('SUBSCRIPTION_SOURCES').split(',')
        self.SUBSCRIPTION_SOURCES = [s.strip() for s in self.SUBSCRIPTION_SOURCES if s.strip() in self.SOURCES]
