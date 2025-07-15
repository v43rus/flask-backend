import requests
from bs4 import BeautifulSoup
from datetime import datetime

def scrape_hackernews():
    url = "https://news.ycombinator.com/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    items = soup.select(".athing")
    posts = []

    for item in items:
        title_tag = item.select_one(".titleline > a")
        if not title_tag:
            continue

        post_id = item['id']
        title = title_tag.get_text(strip=True)
        url = title_tag['href']
        author = item.find_next_sibling("tr").select_one(".hnuser")
        points = item.find_next_sibling("tr").select_one(".score")

        posts.append({
            "id": post_id,
            "title": title,
            "url": url,
            "author": author.text if author else None,
            "points": int(points.text.replace(" points", "")) if points else 0,
            "created_at": datetime.now().isoformat()
        })

    return posts
