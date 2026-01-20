from pydantic import BaseModel
from typing import List, Optional


class LLMConfig(BaseModel):
    """OpenAI API 配置"""
    name: str
    api_key: str
    api_url: str
    call_interval: int = 1  # 默认值为 1 秒，避免对 API 速率限制


class SMTPConfig(BaseModel):
    """SMTP 邮件服务器配置"""
    server: str
    sender: str
    password: str
    receiver: str


class WechatConfig(BaseModel):
    """企业微信机器人配置"""
    webhook_url: str


class PushConfig(BaseModel):
    """推送配置：支持多种推送方式"""
    endpoint: List[str]  # 如 ["email", "wechat"]


class SourceConfig(BaseModel):
    """数据源抓取配置"""
    fetch_limit: int = 5  # 默认值为 5
    subscription_sources: List[str]


class AppConfig(BaseModel):
    """应用全局配置"""
    model: LLMConfig
    smtp: SMTPConfig
    wechat: WechatConfig
    push: PushConfig
    source: SourceConfig
