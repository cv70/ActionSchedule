from datetime import datetime
from datetime import datetime, timedelta
from random import random
import os

import yaml

from config import AppConfig
from fetcher import Fetcher
from sender import Sender
from llmanger import LLManager
import argparse


def parse_args():
    parser = argparse.ArgumentParser(
        description="从 YAML 配置文件加载应用设置并运行",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "-c", "--config",
        type=str,
        default=None,
        help="YAML 配置文件路径"
    )
    return parser.parse_args()


def load_config() -> AppConfig:
    config_raw = os.getenv('CONFIG')
    if not config_raw:
        args = parse_args()
        with open(args.config, 'r') as file:
            config_raw = file.read()

    config = AppConfig.model_validate(yaml.safe_load(config_raw))
    return config


def main():
    config = load_config()

    if config.source.fetch_limit <= 0:
        return
    if not config.source.subscription_sources:
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
