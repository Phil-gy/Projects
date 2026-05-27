import json
import re
from typing import Any

import requests
from bs4 import BeautifulSoup
from recipe_scrapers import scrape_html


def scrape_recipe_from_url(url: str) -> dict:
    if not url.startswith("http://") and not url.startswith("https://"):
        raise ValueError("URL must start with http:// or https://")

    html = fetch_html(url)

    try:
        return scrape_with_recipe_scrapers(html, url)
    except Exception as first_error:
        print("recipe-scrapers failed:", first_error)

    try:
        return scrape_with_json_ld(html, url)
    except Exception as second_error:
        print("JSON-LD fallback failed:", second_error)

    raise ValueError(
        "This recipe could not be imported automatically. "
        "The website is either not supported, blocks scraping, or does not provide structured recipe data. "
        "Please add this recipe manually."
    )


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
                "This website blocks automated scraping requests. "
                "Please try another recipe website or add the recipe manually."
            )

        raise ValueError(f"HTTP error while loading page: {error}")
    except requests.exceptions.RequestException as error:
        raise ValueError(f"Could not load page: {error}")


def scrape_with_recipe_scrapers(html: str, url: str) -> dict:
    scraper = scrape_html(html, org_url=url)

    title = safe_call(scraper.title, "Untitled Recipe")
    ingredients = safe_call(scraper.ingredients, [])
    instructions_text = safe_call(scraper.instructions, "")
    image_url = safe_call(scraper.image, None)
    total_time = safe_call(scraper.total_time, None)
    servings = safe_call(scraper.yields, None)

    instructions = split_instructions(instructions_text)

    if not ingredients and not instructions:
        raise ValueError("No ingredients or instructions found.")

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


def scrape_with_json_ld(html: str, url: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    script_tags = soup.find_all("script", type="application/ld+json")

    for script_tag in script_tags:
        if not script_tag.string:
            continue

        try:
            data = json.loads(script_tag.string)
        except json.JSONDecodeError:
            continue

        recipe_data = find_recipe_data(data)

        if recipe_data:
            return parse_json_ld_recipe(recipe_data, url)

    raise ValueError("No JSON-LD recipe data found.")


def find_recipe_data(data: Any) -> dict | None:
    if isinstance(data, list):
        for item in data:
            found = find_recipe_data(item)
            if found:
                return found

    if isinstance(data, dict):
        data_type = data.get("@type")

        if is_recipe_type(data_type):
            return data

        graph = data.get("@graph")
        if graph:
            return find_recipe_data(graph)

        for value in data.values():
            found = find_recipe_data(value)
            if found:
                return found

    return None


def is_recipe_type(data_type: Any) -> bool:
    if isinstance(data_type, str):
        return data_type.lower() == "recipe"

    if isinstance(data_type, list):
        return any(str(item).lower() == "recipe" for item in data_type)

    return False


def parse_json_ld_recipe(recipe_data: dict, url: str) -> dict:
    title = recipe_data.get("name") or "Untitled Recipe"

    image_url = extract_image_url(recipe_data.get("image"))

    ingredients = recipe_data.get("recipeIngredient") or []
    ingredients = clean_string_list(ingredients)

    instructions = extract_instructions(recipe_data.get("recipeInstructions"))

    servings = recipe_data.get("recipeYield")
    if isinstance(servings, list):
        servings = ", ".join(str(item) for item in servings)

    total_time = parse_time_to_minutes(
        recipe_data.get("totalTime")
        or recipe_data.get("cookTime")
        or recipe_data.get("prepTime")
    )

    category = recipe_data.get("recipeCategory")
    if isinstance(category, list):
        category = ", ".join(str(item) for item in category)

    if not ingredients and not instructions:
        raise ValueError("JSON-LD recipe has no ingredients or instructions.")

    return {
        "title": clean_text(title),
        "source_url": url,
        "image_url": image_url,
        "servings": clean_text(servings) if servings else None,
        "total_time": total_time,
        "ingredients": ingredients,
        "instructions": instructions,
        "category": clean_text(category) if category else "",
        "notes": "",
    }


def extract_image_url(image_data: Any) -> str | None:
    if isinstance(image_data, str):
        return image_data

    if isinstance(image_data, list) and image_data:
        first_image = image_data[0]

        if isinstance(first_image, str):
            return first_image

        if isinstance(first_image, dict):
            return first_image.get("url")

    if isinstance(image_data, dict):
        return image_data.get("url")

    return None


def extract_instructions(instruction_data: Any) -> list[str]:
    if instruction_data is None:
        return []

    instructions = []

    if isinstance(instruction_data, str):
        return split_instructions(instruction_data)

    if isinstance(instruction_data, list):
        for item in instruction_data:
            if isinstance(item, str):
                instructions.append(clean_text(item))

            elif isinstance(item, dict):
                item_type = item.get("@type")

                if item_type == "HowToStep":
                    text = item.get("text") or item.get("name")
                    if text:
                        instructions.append(clean_text(text))

                elif item_type == "HowToSection":
                    section_items = item.get("itemListElement") or []
                    instructions.extend(extract_instructions(section_items))

                else:
                    text = item.get("text") or item.get("name")
                    if text:
                        instructions.append(clean_text(text))

    return [step for step in instructions if step]


def parse_time_to_minutes(time_value: Any) -> int | None:
    if not time_value:
        return None

    text = str(time_value)

    hour_match = re.search(r"(\d+)H", text)
    minute_match = re.search(r"(\d+)M", text)

    hours = int(hour_match.group(1)) if hour_match else 0
    minutes = int(minute_match.group(1)) if minute_match else 0

    total = hours * 60 + minutes

    if total > 0:
        return total

    number_match = re.search(r"\d+", text)
    if number_match:
        return int(number_match.group(0))

    return None


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
        part = clean_text(part)

        if part:
            cleaned.append(part)

    if cleaned:
        return cleaned

    return [clean_text(instructions_text)]


def clean_string_list(items: list[Any]) -> list[str]:
    cleaned = []

    for item in items:
        text = clean_text(str(item))

        if text:
            cleaned.append(text)

    return cleaned


def clean_text(value: Any) -> str:
    if value is None:
        return ""

    text = str(value)
    text = re.sub(r"\s+", " ", text)
    return text.strip()