from datetime import datetime
from datetime import datetime, timedelta
from random import random

from config import Config
from fetcher import Fetcher
from sender import Sender
from llmanger import LLManager

def main():
    config = Config()
    if config.FETCH_LIMIT <= 0:
        return
    if not config.SUBSCRIPTION_SOURCES:
        return

    llmanager = LLManager(config)
    fetcher = Fetcher(llmanager, config)
    sender = Sender(config)

    # 数据抓取
    all_articles = fetcher.fetch()

    # 洞察信息生成
    report = llmanager.analyze_datas(all_articles)

    # 洞察信息发送
    sender.send(all_articles, report)


if __name__ == "__main__":
    main()
