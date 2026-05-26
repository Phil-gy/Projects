import requests
from recipe_scrapers import scrape_html


def scrape_recipe_from_url(url: str) -> dict:
    """
    Scrapes a recipe from a URL.
    Uses browser-like headers to reduce simple 403 blocks.
    """

    if not url.startswith("http://") and not url.startswith("https://"):
        raise ValueError("URL must start with http:// or https://")

    html = fetch_html(url)

    try:
        scraper = scrape_html(html, org_url=url)
    except Exception as error:
        raise ValueError(f"Could not parse this recipe page: {error}")

    title = safe_call(scraper.title, "Untitled Recipe")
    ingredients = safe_call(scraper.ingredients, [])
    instructions_text = safe_call(scraper.instructions, "")
    image_url = safe_call(scraper.image, None)
    total_time = safe_call(scraper.total_time, None)
    servings = safe_call(scraper.yields, None)

    instructions = split_instructions(instructions_text)

    if not ingredients and not instructions:
        raise ValueError(
            "No ingredients or instructions found. This website may block scraping or may not expose recipe data."
        )

    return {
        "title": title,
        "source_url": url,
        "image_url": image_url,
        "servings": servings,
        "total_time": total_time,
        "ingredients": ingredients,
        "instructions": instructions,
        "category": "",
        "notes": "",
    }


def fetch_html(url: str) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,de;q=0.8",
        "Connection": "keep-alive",
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.text
    except requests.exceptions.HTTPError as error:
        if response.status_code == 403:
            raise ValueError(
                "This website blocks automated scraping requests. Try another recipe website or add the recipe manually."
            )
        raise ValueError(f"HTTP error while loading page: {error}")
    except requests.exceptions.RequestException as error:
        raise ValueError(f"Could not load page: {error}")


def safe_call(func, default):
    try:
        value = func()
        if value is None:
            return default
        return value
    except Exception:
        return default


def split_instructions(instructions_text: str) -> list[str]:
    if not instructions_text:
        return []

    text = instructions_text.replace("\r", "\n")
    parts = text.split("\n")

    cleaned = []

    for part in parts:
        part = part.strip()
        if part:
            cleaned.append(part)

    if cleaned:
        return cleaned

    return [instructions_text.strip()]