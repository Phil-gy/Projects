from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

from app.database import create_db_and_tables, get_session
from app.schemas import RecipeCreate, RecipeRead, ScrapeRequest
from app.scraper_service import scrape_recipe_from_url
from app.crud import (
    create_recipe,
    get_all_recipes,
    get_recipe_by_id,
    delete_recipe,
    recipe_to_read,
)

app = FastAPI(title="Recipe Collector API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://deine-recipe-app.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
def root():
    return {"message": "Recipe Collector API is running"}

@app.post("/recipes/scrape", response_model=RecipeCreate)
def scrape_recipe(request: ScrapeRequest):
    try:
        return scrape_recipe_from_url(request.url)
    except Exception as error:
        print("SCRAPER ERROR:", error)
        raise HTTPException(
            status_code=400,
            detail=f"Could not scrape recipe: {str(error)}"
        )

@app.post("/recipes", response_model=RecipeRead)
def add_recipe(
    recipe_data: RecipeCreate,
    session: Session = Depends(get_session)
):
    recipe = create_recipe(session, recipe_data)
    return recipe_to_read(recipe)


@app.get("/recipes", response_model=list[RecipeRead])
def list_recipes(session: Session = Depends(get_session)):
    recipes = get_all_recipes(session)
    return [recipe_to_read(recipe) for recipe in recipes]


@app.get("/recipes/{recipe_id}", response_model=RecipeRead)
def read_recipe(
    recipe_id: int,
    session: Session = Depends(get_session)
):
    recipe = get_recipe_by_id(session, recipe_id)

    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return recipe_to_read(recipe)


@app.delete("/recipes/{recipe_id}")
def remove_recipe(
    recipe_id: int,
    session: Session = Depends(get_session)
):
    was_deleted = delete_recipe(session, recipe_id)

    if not was_deleted:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return {"message": "Recipe deleted"}