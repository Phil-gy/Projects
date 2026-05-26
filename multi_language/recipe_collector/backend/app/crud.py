import json
from sqlmodel import Session, select
from app.models import Recipe
from app.schemas import RecipeCreate, RecipeRead


def create_recipe(session: Session, recipe_data: RecipeCreate) -> Recipe:
    recipe = Recipe(
        title=recipe_data.title,
        source_url=recipe_data.source_url,
        image_url=recipe_data.image_url,
        servings=recipe_data.servings,
        total_time=recipe_data.total_time,
        ingredients=json.dumps(recipe_data.ingredients, ensure_ascii=False),
        instructions=json.dumps(recipe_data.instructions, ensure_ascii=False),
        category=recipe_data.category,
        notes=recipe_data.notes,
    )

    session.add(recipe)
    session.commit()
    session.refresh(recipe)

    return recipe


def get_all_recipes(session: Session) -> list[Recipe]:
    statement = select(Recipe).order_by(Recipe.id.desc())
    return list(session.exec(statement).all())


def get_recipe_by_id(session: Session, recipe_id: int) -> Recipe | None:
    return session.get(Recipe, recipe_id)


def delete_recipe(session: Session, recipe_id: int) -> bool:
    recipe = session.get(Recipe, recipe_id)

    if recipe is None:
        return False

    session.delete(recipe)
    session.commit()
    return True


def recipe_to_read(recipe: Recipe) -> RecipeRead:
    return RecipeRead(
        id=recipe.id,
        title=recipe.title,
        source_url=recipe.source_url,
        image_url=recipe.image_url,
        servings=recipe.servings,
        total_time=recipe.total_time,
        ingredients=json.loads(recipe.ingredients),
        instructions=json.loads(recipe.instructions),
        category=recipe.category,
        notes=recipe.notes,
    )