import os
import json
import time
import requests
import urllib.parse
from bs4 import BeautifulSoup

DATA_DIR = "data"
COMPANIES = ["Grip Security", "Wiz", "AppOmni", "Valence Security"]

def clean_summary(text):
    return BeautifulSoup(text, "html.parser").get_text().replace('\n', ' ').strip()

def scrape_reddit_for_company(company, max_posts=30):
    headers = {"User-Agent": "Mozilla/5.0"}
    query = urllib.parse.quote(company)
    url = f"https://www.reddit.com/search.json?q={query}&limit={max_posts}"
    posts = []
    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        data = res.json()
        for child in data.get("data", {}).get("children", []):
            d = child.get("data", {})
            posts.append({
                "company": company,
                "source": "Reddit",
                "title": d.get("title", ""),
                "url": "https://reddit.com" + d.get("permalink", ""),
                "subreddit": d.get("subreddit", ""),
                "created_utc": d.get("created_utc")
            })
    except Exception as e:
        print(f"❌ Reddit fetch error for {company}: {e}")
    return posts

def scrape_news_for_company(company, max_articles=5):
    query = urllib.parse.quote(f"{company} cybersecurity")
    rss_url = f"https://news.google.com/rss/search?q={query}"
    articles = []

    try:
        resp = requests.get(rss_url, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "xml")
        items = soup.find_all("item")[:max_articles]

        for item in items:
            title = item.title.text if item.title else ""
            link = item.link.text if item.link else ""
            pub = item.pubDate.text if item.pubDate else ""
            summary = clean_summary(item.description.text) if item.description else ""

            if company.lower() not in (title.lower() + summary.lower()):
                continue

            articles.append({
                "company": company,
                "source": "News",
                "title": title,
                "url": link,
                "published": pub,
                "summary": summary
            })

    except Exception as e:
        print(f"❌ News fetch error for {company}: {e}")

    return articles

def save_json(items, filename):
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w") as f:
        json.dump(items, f, indent=2)
    print(f"✅ Saved {len(items)} items → {path}")

def main():
    for company in COMPANIES:
        print(f"\n🔍 Fetching signals for: {company}")
        all_signals = []

        reddit_posts = scrape_reddit_for_company(company)
        news_articles = scrape_news_for_company(company)

        if reddit_posts:
            save_json(reddit_posts, f"{company.lower().replace(' ', '_')}_reddit.json")
            all_signals.extend(reddit_posts)

        if news_articles:
            save_json(news_articles, f"{company.lower().replace(' ', '_')}_news.json")
            all_signals.extend(news_articles)

        if all_signals:
            save_json(all_signals, f"{company.lower().replace(' ', '_')}_signals.json")

        time.sleep(2)

if __name__ == "__main__":
    main()
