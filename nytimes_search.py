import os
import sys

import requests


API_BASE_URL = "https://api.nytimes.com/svc/search/v2/articlesearch.json"
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))


def load_dotenv():
    env_path = os.path.join(PROJECT_DIR, ".env")

    if not os.path.exists(env_path):
        return

    with open(env_path, "r", encoding="utf-8") as env_file:
        for line in env_file:
            line = line.strip()

            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def get_api_key():
    # Get your personal NYTimes API key from:
    # https://developer.nytimes.com/get-started
    # Follow the official steps: sign in, register an app, enable the API,
    # then copy the key from the app's API Keys section.
    load_dotenv()
    api_key = os.getenv("NYTIMES_API_KEY")
    if not api_key:
        print("Missing API key. Set it first with:")
        print('  $env:NYTIMES_API_KEY="your_api_key_here"')
        print("Or create a .env file with:")
        print("  NYTIMES_API_KEY=your_api_key_here")
        sys.exit(1)
    return api_key


def search_articles(search_term, api_key):
    params = {
        "q": search_term,
        "api-key": api_key,
        "sort": "newest",
    }

    response = requests.get(API_BASE_URL, params=params, timeout=15)
    response.raise_for_status()
    return response.json()


def display_results(search_results):
    docs = search_results.get("response", {}).get("docs", [])

    if not docs:
        print("No articles found.")
        return

    for index, doc in enumerate(docs, start=1):
        headline = doc.get("headline", {}).get("main", "Untitled")
        web_url = doc.get("web_url", "No URL")
        publication_date = doc.get("pub_date", "")[:10]

        date_text = f" - {publication_date}" if publication_date else ""
        print(f"{index}. {headline}{date_text}")
        print(f"   {web_url}")


def main():
    api_key = get_api_key()

    while True:
        search_term = input("Your search term (or 'exit'): ").strip()

        if search_term.lower() in {"exit", "quit", "q"}:
            print("Bye!")
            break

        if not search_term:
            print("Please type a search term.")
            continue

        try:
            search_results = search_articles(search_term, api_key)
            display_results(search_results)
        except requests.RequestException as error:
            print(f"Request failed: {error}")

        print()


if __name__ == "__main__":
    main()
