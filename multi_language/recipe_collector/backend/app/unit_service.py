import re
from fractions import Fraction
from typing import Any


US_UNIT_PATTERN = re.compile(
    r"(?P<amount>\d+\s+\d+/\d+|\d+[.,]\d+|\d+/\d+|\d+)\s*"
    r"(?P<unit>cups?|tbsp|tablespoons?|tsp|teaspoons?|oz|ounces?|lb|lbs|pounds?)\b",
    re.IGNORECASE,
)

UNICODE_FRACTIONS = {
    "\u00bc": 0.25,
    "\u00bd": 0.5,
    "\u00be": 0.75,
    "\u2153": 1 / 3,
    "\u2154": 2 / 3,
    "\u215b": 0.125,
    "\u215c": 0.375,
    "\u215d": 0.625,
    "\u215e": 0.875,
}

LIQUID_CUP_KEYWORDS = {
    "water",
    "milk",
    "cream",
    "stock",
    "broth",
    "oil",
    "vinegar",
    "sauce",
    "soy sauce",
    "juice",
    "wine",
    "beer",
    "wasser",
    "milch",
    "sahne",
    "bruehe",
    "br\u00fche",
    "oel",
    "\u00f6l",
    "essig",
    "sauce",
    "saft",
    "wein",
}

CUP_GRAM_CONVERSIONS = [
    {
        "keywords": {"corn", "mais"},
        "grams_per_cup": 165,
    },
    {
        "keywords": {"onion", "zwiebel"},
        "grams_per_cup": 160,
    },
    {
        "keywords": {"mozzarella"},
        "grams_per_cup": 110,
    },
    {
        "keywords": {"cheddar", "gouda", "parmesan", "cheese", "kaese", "k\u00e4se"},
        "grams_per_cup": 115,
    },
    {
        "keywords": {"mayo", "mayonnaise"},
        "grams_per_cup": 230,
    },
    {
        "keywords": {"butter"},
        "grams_per_cup": 225,
    },
    {
        "keywords": {"flour", "mehl"},
        "grams_per_cup": 120,
    },
    {
        "keywords": {"sugar", "zucker"},
        "grams_per_cup": 200,
    },
    {
        "keywords": {"brown sugar", "brauner zucker"},
        "grams_per_cup": 220,
    },
    {
        "keywords": {"rice", "reis"},
        "grams_per_cup": 185,
    },
    {
        "keywords": {"oats", "haferflocken"},
        "grams_per_cup": 90,
    },
    {
        "keywords": {"breadcrumbs", "panko", "semmelbroesel", "semmelbr\u00f6sel"},
        "grams_per_cup": 110,
    },
    {
        "keywords": {"nuts", "almonds", "walnuts", "nuesse", "n\u00fcsse", "mandeln"},
        "grams_per_cup": 120,
    },
]


def add_unit_conversion_suggestions(recipe_data: dict[str, Any]) -> dict[str, Any]:
    ingredients = recipe_data.get("ingredients")

    if not isinstance(ingredients, list):
        return recipe_data

    analysis = analyze_ingredient_units([str(ingredient) for ingredient in ingredients])

    recipe_data["converted_ingredients"] = analysis["converted_ingredients"]
    recipe_data["unit_warnings"] = analysis["unit_warnings"]

    return recipe_data


def analyze_ingredient_units(ingredients: list[str]) -> dict[str, list[str]]:
    converted_ingredients = []
    unit_warnings = []

    for ingredient in ingredients:
        converted_ingredient, warnings = convert_ingredient_units(ingredient)
        converted_ingredients.append(converted_ingredient)
        unit_warnings.extend(warnings)

    return {
        "converted_ingredients": converted_ingredients,
        "unit_warnings": unit_warnings,
    }


def convert_ingredient_units(ingredient: str) -> tuple[str, list[str]]:
    warnings = []

    def replace_match(match: re.Match[str]) -> str:
        amount_text = match.group("amount")
        unit = match.group("unit").lower()
        amount = parse_amount(amount_text)

        if amount is None:
            warnings.append(f"Could not parse amount in: {ingredient}")
            return match.group(0)

        if unit in {"tbsp", "tablespoon", "tablespoons"}:
            return f"{format_amount(amount)} EL"

        if unit in {"tsp", "teaspoon", "teaspoons"}:
            return f"{format_amount(amount)} TL"

        if unit in {"oz", "ounce", "ounces"}:
            return f"{format_grams(amount * 28.35)} g"

        if unit in {"lb", "lbs", "pound", "pounds"}:
            return f"{format_grams(amount * 453.592)} g"

        if unit in {"cup", "cups"}:
            cup_conversion = find_cup_gram_conversion(ingredient)

            if cup_conversion is not None:
                return f"{format_grams(amount * cup_conversion)} g"

            if looks_like_liquid_ingredient(ingredient):
                return f"{format_amount(amount * 240)} ml"

            warnings.append(
                f"US cup found in '{ingredient}'. Cups depend on the ingredient, so please check this manually."
            )
            return f"{match.group(0)} (US cup - bitte pruefen)"

        return match.group(0)

    converted = US_UNIT_PATTERN.sub(replace_match, ingredient)
    converted = replace_unicode_fractions(converted)

    return converted, warnings


def parse_amount(value: str) -> float | None:
    value = value.strip().replace(",", ".")

    if " " in value and "/" in value:
        whole_number, fraction = value.split(" ", 1)
        return float(whole_number) + float(Fraction(fraction))

    if "/" in value:
        return float(Fraction(value))

    try:
        return float(value)
    except ValueError:
        return None


def replace_unicode_fractions(value: str) -> str:
    for unicode_fraction, decimal_value in UNICODE_FRACTIONS.items():
        if unicode_fraction in value:
            value = value.replace(unicode_fraction, format_amount(decimal_value))

    return value


def looks_like_liquid_ingredient(ingredient: str) -> bool:
    normalized = ingredient.lower()
    return any(keyword in normalized for keyword in LIQUID_CUP_KEYWORDS)


def find_cup_gram_conversion(ingredient: str) -> int | None:
    normalized = ingredient.lower()

    for conversion in CUP_GRAM_CONVERSIONS:
        keywords = conversion["keywords"]

        if any(keyword in normalized for keyword in keywords):
            return int(conversion["grams_per_cup"])

    return None


def format_amount(value: float) -> str:
    rounded = round(value, 2)

    if rounded.is_integer():
        return str(int(rounded))

    return str(rounded).replace(".", ",")


def format_grams(value: float) -> str:
    if value >= 100:
        return str(round(value / 5) * 5)

    return str(round(value))
