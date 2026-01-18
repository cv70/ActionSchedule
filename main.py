from datetime import datetime
from datetime import datetime, timedelta

from fetcher import fetch_huggingface_papers, fetch_techcrunch_rss, fetch_github_trending

yesterday = datetime.now() - timedelta(days=1)
today = yesterday.strftime("%Y-%m-%d")


# List of famous quotes
FAMOUS_QUOTES = [
    "The only way to do great work is to love what you do. - Steve Jobs",
    "Believe you can and you're halfway there. - Theodore Roosevelt",
    "Success is not final, failure is not fatal: It is the courage to continue that counts. - Winston S. Churchill",
    "The best way to predict the future is to invent it. - Alan Kay",
    "Do not wait to strike till the iron is hot; but make it hot by striking. - William Butler Yeats"
]


def main():
    # query = "cs.NE OR cs.MA OR cs.LG OR cs.CV OR cs.CL OR cs.AI"

    # arxiv_papers = get_arxiv_papers(query)

    # hacknews_storys = fetch_hacknews_storys()
    # print(hacknews_storys)

    huggingface_papers = fetch_huggingface_papers()

    # total = len(arxiv_papers) + len(hacknews_storys) + len(huggingface_papers)
    # random_quote = random.choice(FAMOUS_QUOTES)
    print(huggingface_papers)

    github_trending = fetch_github_trending()
    print(github_trending)
    

    # subject = "Tech Trending"
    # body = f"Today, we have collected {total} articles.\n\n" 
    #        f"New papers have been updated. Check the website for details.\n\n" 
    #        f"{random_quote}"

    # Send email notification
    # send_email(subject, body)

if __name__ == "__main__":
    main()
