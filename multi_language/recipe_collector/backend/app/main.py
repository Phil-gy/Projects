import os

import cloudinary
import cloudinary.uploader

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

from app.database import create_db_and_tables, get_session
from app.schemas import (
    RecipeCreate,
    RecipeRead,
    ScrapeRequest,
    LoginRequest,
    LoginResponse,
    RecipeImageRead,
)
from app.scraper_service import scrape_recipe_from_url
from app.auth import create_admin_token, check_password, verify_admin_token
from app.crud import (
    create_recipe,
    get_all_recipes,
    get_recipe_by_id,
    update_recipe,
    delete_recipe,
    recipe_to_read,
    add_recipe_image,
    get_recipe_images,
    set_cover_image,
    delete_recipe_image,
)

app = FastAPI(title="Recipe Collector API")

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://www.rabeasrezepte.de",
        "https://rabeasrezepte.de",
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


@app.post("/auth/login", response_model=LoginResponse)
def login(request: LoginRequest):
    if not check_password(request.password):
        raise HTTPException(status_code=401, detail="Wrong password")

    token = create_admin_token()
    return LoginResponse(token=token)


@app.get("/auth/me")
def me(_: bool = Depends(verify_admin_token)):
    return {"role": "admin"}


@app.post("/recipes/scrape", response_model=RecipeCreate)
def scrape_recipe(
    request: ScrapeRequest,
    _: bool = Depends(verify_admin_token),
):
    try:
        return scrape_recipe_from_url(request.url)
    except Exception as error:
        print("SCRAPER ERROR:", error)
        raise HTTPException(
            status_code=400,
            detail=f"Could not scrape recipe: {str(error)}",
        )


@app.post("/recipes", response_model=RecipeRead)
def add_recipe(
    recipe_data: RecipeCreate,
    session: Session = Depends(get_session),
    _: bool = Depends(verify_admin_token),
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
    session: Session = Depends(get_session),
):
    recipe = get_recipe_by_id(session, recipe_id)

    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return recipe_to_read(recipe)


@app.put("/recipes/{recipe_id}", response_model=RecipeRead)
def edit_recipe(
    recipe_id: int,
    recipe_data: RecipeCreate,
    session: Session = Depends(get_session),
    _: bool = Depends(verify_admin_token),
):
    recipe = update_recipe(session, recipe_id, recipe_data)

    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return recipe_to_read(recipe)


@app.delete("/recipes/{recipe_id}")
def remove_recipe(
    recipe_id: int,
    session: Session = Depends(get_session),
    _: bool = Depends(verify_admin_token),
):
    was_deleted = delete_recipe(session, recipe_id)

    if not was_deleted:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return {"message": "Recipe deleted"}


@app.post("/recipes/{recipe_id}/images", response_model=RecipeImageRead)
def upload_recipe_image(
    recipe_id: int,
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    _: bool = Depends(verify_admin_token),
):
    recipe = get_recipe_by_id(session, recipe_id)

    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")

    try:
        upload_result = cloudinary.uploader.upload(
            file.file,
            folder=f"rabeas-recipes/{recipe_id}",
            resource_type="image",
        )

        image_url = upload_result["secure_url"]
        public_id = upload_result.get("public_id")

        image = add_recipe_image(
            session=session,
            recipe_id=recipe_id,
            image_url=image_url,
            public_id=public_id,
        )

        if image is None:
            raise HTTPException(status_code=404, detail="Recipe not found")

        return image

    except Exception as error:
        print("IMAGE UPLOAD ERROR:", error)
        raise HTTPException(
            status_code=400,
            detail=f"Could not upload image: {str(error)}",
        )


@app.get("/recipes/{recipe_id}/images", response_model=list[RecipeImageRead])
def list_recipe_images(
    recipe_id: int,
    session: Session = Depends(get_session),
):
    recipe = get_recipe_by_id(session, recipe_id)

    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return get_recipe_images(session, recipe_id)


@app.put("/recipes/{recipe_id}/images/{image_id}/cover", response_model=RecipeImageRead)
def choose_cover_image(
    recipe_id: int,
    image_id: int,
    session: Session = Depends(get_session),
    _: bool = Depends(verify_admin_token),
):
    image = set_cover_image(session, recipe_id, image_id)

    if image is None:
        raise HTTPException(status_code=404, detail="Image not found")

    return image


@app.delete("/recipes/{recipe_id}/images/{image_id}")
def remove_recipe_image(
    recipe_id: int,
    image_id: int,
    session: Session = Depends(get_session),
    _: bool = Depends(verify_admin_token),
):
    image = delete_recipe_image(session, recipe_id, image_id)

    if image is None:
        raise HTTPException(status_code=404, detail="Image not found")

    if image.public_id:
        try:
            cloudinary.uploader.destroy(image.public_id)
        except Exception as error:
            print("CLOUDINARY DELETE ERROR:", error)

    return {"message": "Image deleted"}