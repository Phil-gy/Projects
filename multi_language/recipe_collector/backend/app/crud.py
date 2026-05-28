import json
from sqlmodel import Session, select

from app.models import Recipe, RecipeImage
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
        rating=recipe_data.rating,
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


def update_recipe(
    session: Session,
    recipe_id: int,
    recipe_data: RecipeCreate,
) -> Recipe | None:
    recipe = session.get(Recipe, recipe_id)

    if recipe is None:
        return None

    recipe.title = recipe_data.title
    recipe.source_url = recipe_data.source_url
    recipe.image_url = recipe_data.image_url
    recipe.servings = recipe_data.servings
    recipe.total_time = recipe_data.total_time
    recipe.ingredients = json.dumps(recipe_data.ingredients, ensure_ascii=False)
    recipe.instructions = json.dumps(recipe_data.instructions, ensure_ascii=False)
    recipe.category = recipe_data.category
    recipe.notes = recipe_data.notes
    recipe.rating = recipe_data.rating

    session.add(recipe)
    session.commit()
    session.refresh(recipe)

    return recipe


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
        rating=recipe.rating,
    )


def add_recipe_image(
    session: Session,
    recipe_id: int,
    image_url: str,
    public_id: str | None,
) -> RecipeImage | None:
    recipe = session.get(Recipe, recipe_id)

    if recipe is None:
        return None

    existing_images = session.exec(
        select(RecipeImage).where(RecipeImage.recipe_id == recipe_id)
    ).all()

    is_first_image = len(existing_images) == 0

    image = RecipeImage(
        recipe_id=recipe_id,
        image_url=image_url,
        public_id=public_id,
        is_cover=is_first_image,
    )

    session.add(image)

    if is_first_image:
        recipe.image_url = image_url
        session.add(recipe)

    session.commit()
    session.refresh(image)

    return image


def get_recipe_images(session: Session, recipe_id: int) -> list[RecipeImage]:
    statement = (
        select(RecipeImage)
        .where(RecipeImage.recipe_id == recipe_id)
        .order_by(RecipeImage.created_at.desc())
    )

    return list(session.exec(statement).all())


def set_cover_image(
    session: Session,
    recipe_id: int,
    image_id: int,
) -> RecipeImage | None:
    recipe = session.get(Recipe, recipe_id)
    selected_image = session.get(RecipeImage, image_id)

    if recipe is None or selected_image is None:
        return None

    if selected_image.recipe_id != recipe_id:
        return None

    images = session.exec(
        select(RecipeImage).where(RecipeImage.recipe_id == recipe_id)
    ).all()

    for image in images:
        image.is_cover = image.id == image_id
        session.add(image)

    recipe.image_url = selected_image.image_url
    session.add(recipe)

    session.commit()
    session.refresh(selected_image)

    return selected_image


def delete_recipe_image(
    session: Session,
    recipe_id: int,
    image_id: int,
) -> RecipeImage | None:
    image = session.get(RecipeImage, image_id)

    if image is None or image.recipe_id != recipe_id:
        return None

    session.delete(image)
    session.commit()

    return image