import json
import re
from html import unescape
from typing import Any
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from recipe_scrapers import scrape_html


def scrape_recipe_from_url(url: str) -> dict:
    if not url.startswith("http://") and not url.startswith("https://"):
        raise ValueError("URL must start with http:// or https://")

    if is_instagram_url(url):
        return scrape_instagram_recipe_from_url(url)

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


def is_instagram_url(url: str) -> bool:
    hostname = urlparse(url).netloc.lower()
    return hostname == "instagram.com" or hostname.endswith(".instagram.com")


def scrape_instagram_recipe_from_url(url: str) -> dict:
    errors = []

    try:
        html = fetch_html(url)
        return scrape_instagram_recipe(html, url)
    except Exception as error:
        errors.append(str(error))
        print("Instagram page scrape failed:", error)

    embed_url = build_instagram_embed_url(url)

    if embed_url:
        try:
            html = fetch_html(embed_url)
            return scrape_instagram_recipe(html, url)
        except Exception as error:
            errors.append(str(error))
            print("Instagram embed scrape failed:", error)

    error_details = " ".join(errors)

    if "did not expose a public caption" in error_details:
        raise ValueError(
            "Instagram did not expose the caption to the scraper. "
            "This can happen when Instagram serves a login page, blocks automated requests, "
            "or the post is not fully public. Please paste the recipe text manually for this post."
        )

    raise ValueError(
        "This Instagram post could not be imported automatically. "
        "Instagram may be blocking the request or the caption may not contain clear recipe text. "
        "Please paste the recipe text manually for this post."
    )


def build_instagram_embed_url(url: str) -> str | None:
    parsed_url = urlparse(url)
    path_parts = [part for part in parsed_url.path.split("/") if part]

    if len(path_parts) < 2:
        return None

    post_type = path_parts[0]
    shortcode = path_parts[1]

    if post_type not in {"p", "reel", "tv"}:
        return None

    return f"https://www.instagram.com/{post_type}/{shortcode}/embed/captioned/"


def fetch_html(url: str) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,de;q=0.8",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "DNT": "1",
        "Pragma": "no-cache",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Upgrade-Insecure-Requests": "1",
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


def scrape_instagram_recipe(html: str, url: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")

    caption = extract_instagram_caption(soup, html)

    if not caption:
        raise ValueError(
            "Instagram did not expose a public caption for this post. "
            "Please make sure the post is public, or add the recipe manually."
        )

    title = extract_instagram_title(soup, caption)
    image_url = extract_instagram_image_url(soup, html)
    ingredients, instructions, notes = parse_instagram_recipe_caption(caption, title)

    if not ingredients and not instructions:
        raise ValueError(
            "The Instagram caption was found, but it did not look like a recipe. "
            "Please add the ingredients and instructions manually."
        )

    return {
        "title": title,
        "source_url": url,
        "image_url": image_url,
        "servings": None,
        "total_time": None,
        "ingredients": ingredients,
        "instructions": instructions,
        "category": "Instagram",
        "notes": notes,
    }


def extract_instagram_caption(soup: BeautifulSoup, html: str) -> str:
    caption_candidates = []

    for blockquote in soup.find_all("blockquote"):
        text = blockquote.get_text("\n", strip=True)

        if text:
            caption_candidates.append(text)

    for article in soup.find_all("article"):
        text = article.get_text("\n", strip=True)

        if text:
            caption_candidates.append(text)

    for selector in [
        {"property": "og:description"},
        {"name": "description"},
        {"property": "twitter:description"},
        {"name": "twitter:description"},
    ]:
        tag = soup.find("meta", attrs=selector)
        content = tag.get("content") if tag else None

        if content:
            caption_candidates.append(content)

    caption_candidates.extend(extract_instagram_caption_from_scripts(html))

    for candidate in caption_candidates:
        caption = clean_instagram_caption(candidate)

        if caption and looks_like_recipe_caption(caption):
            return caption

    for candidate in caption_candidates:
        caption = clean_instagram_caption(candidate)

        if caption:
            return caption

    return ""


def extract_instagram_caption_from_scripts(html: str) -> list[str]:
    captions = []

    patterns = [
        r'"edge_media_to_caption"\s*:\s*\{\s*"edges"\s*:\s*\[\s*\{\s*"node"\s*:\s*\{\s*"text"\s*:\s*"((?:\\.|[^"\\])*)"',
        r'"caption"\s*:\s*\{\s*"text"\s*:\s*"((?:\\.|[^"\\])*)"',
        r'"text"\s*:\s*"((?:\\.|[^"\\])*)"',
    ]

    for pattern in patterns:
        for match in re.finditer(pattern, html):
            text = decode_json_string(match.group(1))

            if text and looks_like_recipe_caption(text):
                captions.append(text)

    return captions


def extract_instagram_title(soup: BeautifulSoup, caption: str) -> str:
    first_caption_line = first_meaningful_caption_line(caption)

    if first_caption_line:
        return clean_instagram_title(first_caption_line)

    og_title = get_meta_content(soup, "property", "og:title")
    title_tag = soup.find("title")
    browser_title = title_tag.get_text(" ", strip=True) if title_tag else ""

    for candidate in [og_title, browser_title]:
        title = clean_instagram_title(candidate)

        if title:
            return title

    return "Instagram Recipe"


def extract_instagram_image_url(soup: BeautifulSoup, html: str) -> str | None:
    for image_url in extract_instagram_image_urls_from_scripts(html):
        if is_usable_instagram_recipe_image_url(image_url):
            return image_url

    for image_url in extract_instagram_image_urls_from_page(soup):
        if is_usable_instagram_recipe_image_url(image_url):
            return image_url

    for selector in [
        ("property", "og:image"),
        ("name", "twitter:image"),
        ("property", "og:image:secure_url"),
    ]:
        image_url = get_meta_content(soup, selector[0], selector[1])

        if image_url:
            return image_url

    return None


def extract_instagram_image_urls_from_scripts(html: str) -> list[str]:
    image_urls = []
    patterns = [
        r'"display_url"\s*:\s*"((?:\\.|[^"\\])*)"',
        r'"thumbnail_src"\s*:\s*"((?:\\.|[^"\\])*)"',
        r'"thumbnail_url"\s*:\s*"((?:\\.|[^"\\])*)"',
        r'"url"\s*:\s*"((?:\\.|[^"\\])*)"',
    ]

    for pattern in patterns:
        for match in re.finditer(pattern, html):
            image_url = clean_instagram_image_url(match.group(1))

            if image_url:
                image_urls.append(image_url)

    return deduplicate_strings(image_urls)


def extract_instagram_image_urls_from_page(soup: BeautifulSoup) -> list[str]:
    image_urls = []

    for image in soup.find_all("img"):
        src = image.get("src")

        if src:
            image_urls.append(clean_instagram_image_url(src))

        srcset = image.get("srcset")

        if not srcset:
            continue

        for srcset_part in srcset.split(","):
            srcset_url = srcset_part.strip().split(" ")[0]

            if srcset_url:
                image_urls.append(clean_instagram_image_url(srcset_url))

    return deduplicate_strings(image_urls)


def clean_instagram_image_url(image_url: str) -> str:
    image_url = decode_json_string(image_url)
    image_url = unescape(image_url)
    image_url = image_url.replace("\\/", "/")
    image_url = clean_text(image_url)

    return image_url


def is_usable_instagram_recipe_image_url(image_url: str) -> bool:
    if not image_url.startswith("http"):
        return False

    lowered = image_url.lower()

    if not any(extension in lowered for extension in [".jpg", ".jpeg", ".png", ".webp"]):
        return False

    blocked_fragments = [
        "profile_pic",
        "profilepic",
        "s150x150",
        "s320x320",
        "emoji",
        "static",
        "sprite",
    ]

    return not any(fragment in lowered for fragment in blocked_fragments)


def deduplicate_strings(items: list[str]) -> list[str]:
    seen = set()
    deduplicated = []

    for item in items:
        if not item or item in seen:
            continue

        seen.add(item)
        deduplicated.append(item)

    return deduplicated


def get_meta_content(soup: BeautifulSoup, key: str, value: str) -> str:
    tag = soup.find("meta", attrs={key: value})

    if not tag:
        return ""

    return clean_text(tag.get("content"))


def clean_instagram_caption(text: str) -> str:
    text = decode_json_string(text)
    text = unescape(text)
    text = text.replace("\\n", "\n")
    text = text.replace("\\u003Cbr\\u003E", "\n")
    text = text.replace("<br>", "\n")
    text = text.replace("<br/>", "\n")
    text = re.sub(r"^\s*[\d.,]+\s*[KMB]?\s+likes,\s*[\d.,]+\s*[KMB]?\s+comments\s*-\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^.+?\s+on Instagram:\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^[\w.]+(?:\s+on\s+[^:\n]+)?:\s*", "", text)
    text = text.strip()

    if len(text) >= 2 and text[0] in {"'", '"'} and text[-1] == text[0]:
        text = text[1:-1]

    return normalize_multiline_text(text)


def clean_instagram_title(text: str) -> str:
    text = clean_text(text)
    text = re.sub(r"^.+?\s+on Instagram:\s*", "", text, flags=re.IGNORECASE)
    text = text.strip(" \"'")
    text = re.sub(r"\s*[-|]\s*Instagram\s*$", "", text, flags=re.IGNORECASE)
    text = remove_trailing_social_text(text)

    return text or "Instagram Recipe"


def first_meaningful_caption_line(caption: str) -> str:
    for line in split_caption_lines(caption):
        normalized = line.strip(" \"'")

        if not normalized:
            continue

        if is_caption_noise(normalized):
            continue

        return normalized

    return ""


def parse_instagram_recipe_caption(
    caption: str,
    title: str,
) -> tuple[list[str], list[str], str]:
    lines = split_caption_lines(caption)

    if lines and clean_instagram_title(lines[0]).lower() == title.lower():
        lines = lines[1:]

    sections = collect_caption_sections(lines)
    ingredients = sections.get("ingredients", [])
    instructions = sections.get("instructions", [])
    notes = sections.get("notes", [])

    if not ingredients:
        ingredients = infer_ingredients_from_lines(lines)

    if not instructions:
        instructions = infer_instructions_from_lines(lines, ingredients)

    notes = [
        line
        for line in notes
        if line not in ingredients and line not in instructions and not is_caption_noise(line)
    ]

    return ingredients, instructions, "\n".join(notes)


def collect_caption_sections(lines: list[str]) -> dict[str, list[str]]:
    sections = {
        "ingredients": [],
        "instructions": [],
        "notes": [],
    }
    current_section = "notes"

    for line in lines:
        normalized = normalize_caption_heading(line)

        if is_caption_noise(line):
            continue

        if normalized in {
            "ingredient",
            "ingredients",
            "zutaten",
            "zutat",
            "you need",
            "you will need",
            "what you need",
        }:
            current_section = "ingredients"
            continue

        if normalized in {
            "instruction",
            "instructions",
            "method",
            "directions",
            "preparation",
            "prep",
            "steps",
            "zubereitung",
            "anleitung",
            "rezept",
        }:
            current_section = "instructions"
            continue

        if normalized in {
            "notes",
            "note",
            "tips",
            "tipp",
            "tip",
        }:
            current_section = "notes"
            continue

        cleaned_line = remove_list_marker(line)

        if not cleaned_line:
            continue

        if current_section == "ingredients" and looks_like_subheading(cleaned_line):
            sections["ingredients"].append(cleaned_line)
            continue

        sections[current_section].append(cleaned_line)

    return sections


def infer_ingredients_from_lines(lines: list[str]) -> list[str]:
    ingredients = []

    for line in lines:
        cleaned_line = remove_list_marker(line)

        if is_caption_noise(cleaned_line):
            continue

        if looks_like_instruction(cleaned_line):
            continue

        if looks_like_ingredient(cleaned_line):
            ingredients.append(cleaned_line)

    return ingredients


def infer_instructions_from_lines(
    lines: list[str],
    ingredients: list[str],
) -> list[str]:
    ingredient_set = set(ingredients)
    instructions = []

    for line in lines:
        cleaned_line = remove_list_marker(line)

        if not cleaned_line or cleaned_line in ingredient_set:
            continue

        if is_caption_noise(cleaned_line) or looks_like_ingredient(cleaned_line):
            continue

        if looks_like_instruction(cleaned_line):
            instructions.append(cleaned_line)

    return instructions


def split_caption_lines(text: str) -> list[str]:
    text = normalize_multiline_text(text)
    lines = []

    for line in text.split("\n"):
        cleaned_line = clean_text(line)

        if cleaned_line:
            lines.append(cleaned_line)

    return lines


def normalize_multiline_text(text: str) -> str:
    text = text.replace("\r", "\n")
    text = re.sub(r"\n\s*\n+", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def normalize_caption_heading(line: str) -> str:
    line = clean_text(line)
    line = line.strip(":-\u2013\u2014\u2022* ")
    return line.lower()


def remove_list_marker(line: str) -> str:
    line = clean_text(line)
    line = re.sub(r"^\s*(?:[-*\u2022]|\d+[.)])\s*", "", line)
    return line.strip()


def remove_trailing_social_text(text: str) -> str:
    text = re.sub(r"\s+#\S+.*$", "", text)
    text = re.sub(r"\s+Follow\s+.+$", "", text, flags=re.IGNORECASE)
    return text.strip()


def looks_like_recipe_caption(text: str) -> bool:
    lowered = text.lower()
    recipe_words = [
        "ingredient",
        "ingredients",
        "zutaten",
        "instructions",
        "method",
        "directions",
        "zubereitung",
        "recipe",
        "rezept",
    ]

    return any(word in lowered for word in recipe_words)


def looks_like_subheading(line: str) -> bool:
    if len(line) > 40:
        return False

    return line.endswith(":") or line.lower() in {
        "sauce",
        "layers",
        "filling",
        "dumpling filling",
        "topping",
        "dressing",
        "marinade",
        "for serving",
    }


def looks_like_ingredient(line: str) -> bool:
    lowered = line.lower()
    quantity_pattern = (
        r"(^|\s)(\d+|[\u00bc\u00bd\u00be\u2153\u2154\u215b\u215c\u215d\u215e]|\d+[\/.,]\d+|\d+\s*[\/]\s*\d+)"
    )
    unit_words = [
        "cup",
        "cups",
        "tbsp",
        "tablespoon",
        "tablespoons",
        "tsp",
        "teaspoon",
        "teaspoons",
        "g",
        "gram",
        "grams",
        "kg",
        "ml",
        "l",
        "lb",
        "lbs",
        "oz",
        "ounce",
        "ounces",
        "clove",
        "cloves",
        "can",
        "cans",
        "pack",
        "packs",
        "slice",
        "slices",
        "pinch",
        "handful",
        "bund",
        "el",
        "tl",
    ]

    if re.search(quantity_pattern, lowered):
        return True

    return any(re.search(rf"\b{re.escape(unit)}\b", lowered) for unit in unit_words)


def looks_like_instruction(line: str) -> bool:
    lowered = line.lower()

    if re.match(r"^\d+[.)]\s+", line):
        return True

    instruction_words = [
        "add",
        "bake",
        "boil",
        "chop",
        "combine",
        "cook",
        "cut",
        "drain",
        "fry",
        "heat",
        "mix",
        "pour",
        "preheat",
        "remove",
        "serve",
        "simmer",
        "stir",
        "top",
        "transfer",
        "whisk",
        "wrap",
        "backen",
        "braten",
        "erhitzen",
        "geben",
        "kochen",
        "mischen",
        "schneiden",
        "servieren",
        "verr\u00fchren",
    ]

    return any(re.search(rf"\b{word}\b", lowered) for word in instruction_words)


def is_caption_noise(line: str) -> bool:
    lowered = line.lower()

    if not lowered:
        return True

    if lowered.startswith("#"):
        return True

    if lowered.startswith("@"):
        return True

    noise_phrases = [
        "link in bio",
        "follow for more",
        "save this",
        "share this",
        "comment",
        "like and follow",
    ]

    return any(phrase in lowered for phrase in noise_phrases)


def decode_json_string(value: str) -> str:
    try:
        return json.loads(f'"{value}"')
    except json.JSONDecodeError:
        return value


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
