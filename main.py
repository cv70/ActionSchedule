from datetime import datetime
from datetime import datetime, timedelta
from random import random

from fetcher import fetch_hacknews_storys, fetch_huggingface_papers, fetch_techcrunch_rss, fetch_github_trending
from output import send_email, build_html_content

def main():
    # query = "cs.NE OR cs.MA OR cs.LG OR cs.CV OR cs.CL OR cs.AI"

    # arxiv_papers = get_arxiv_papers(query)

    hacknews_storys = fetch_hacknews_storys()

    huggingface_papers = fetch_huggingface_papers()

    techcrunch_rss = fetch_techcrunch_rss()

    github_trending = fetch_github_trending()

    all_articles = []
    all_articles.extend(hacknews_storys)
    all_articles.extend(huggingface_papers)
    all_articles.extend(techcrunch_rss)
    all_articles.extend(github_trending)

    body = build_html_content(all_articles)

    # Send email notification
    send_email('Tech Insight', body)

if __name__ == "__main__":
    main()
