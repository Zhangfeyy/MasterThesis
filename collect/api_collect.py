import requests
import time
import csv
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
api_key = os.getenv("KEY")
if not api_key:
    raise ValueError("API key not found.")

BASE_URL = "https://content.guardianapis.com/search"
csv_file = "./data/world_articles_2025.csv"

# Create CSV with headers
with open(csv_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["publication_date", "headline", "body_html"])
    writer.writeheader()


# Check the doc: https://open-platform.theguardian.com/documentation/
params = {
    "section": "world",
    "from-date": "2025-01-01",
    "to-date": "2025-12-31",
    "page-size": 50,
    "show-fields": "headline,body",
    "order-by": "oldest",
    "api-key": api_key
}

page = 1
while True:
    params["page"] = page
    try:
        response = requests.get(BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()["response"]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        break

    results = data.get("results", [])
    if not results:
        break

    with open(csv_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["publication_date", "headline", "body_html"])
        for article in results:
            writer.writerow({
                "publication_date": article.get("webPublicationDate", ""),
                "headline": article.get("fields", {}).get("headline", ""),
                "body_html": article.get("fields", {}).get("body", "")
            })

    print(f"Saved page {page} ({len(results)} articles)")
    if page >= data.get("pages", 0):
        break
    page += 1
    time.sleep(0.3)

print("All pages saved with HTML content.")