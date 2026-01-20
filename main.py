from datetime import datetime
from datetime import datetime, timedelta
from random import random

from config import Config
from fetcher import Fetcher
from output import send_email, build_html_content
from llmanger import LLManager

def main():
    config = Config()
    if config.FETCH_LIMIT <= 0:
        return
    if not config.SUBSCRIPTION_SOURCES:
        return

    llmanager = LLManager(config)
    fetcher = Fetcher(llmanager, config)

    # 数据抓取
    all_articles = fetcher.fetch()

    # 洞察信息生成
    report = llmanager.analyze_datas(all_articles)

    body = build_html_content(all_articles, report)

    # Send email notification
    send_email('Tech Insight', body)

if __name__ == "__main__":
    main()
