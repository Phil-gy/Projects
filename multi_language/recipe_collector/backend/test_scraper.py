from recipe_scrapers import scrape_me

url = "https://www.allrecipes.com/recipe/158968/spinach-and-feta-turkey-burgers/"

scraper = scrape_me(url)

print("TITLE:")
print(scraper.title())

print("\nINGREDIENTS:")
print(scraper.ingredients())

print("\nINSTRUCTIONS:")
print(scraper.instructions())

print("\nTOTAL TIME:")
print(scraper.total_time())

print("\nIMAGE:")
print(scraper.image())

print("\nYIELDS:")
print(scraper.yields())