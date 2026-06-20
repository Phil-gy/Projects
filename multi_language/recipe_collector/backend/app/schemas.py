from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class RecipeCreate(BaseModel):
    title: str
    source_url: str
    image_url: Optional[str] = None
    servings: Optional[str] = None
    total_time: Optional[int] = None
    ingredients: list[str]
    instructions: list[str]
    category: Optional[str] = None
    notes: Optional[str] = None
    rating: Optional[float] = None
    image_options: Optional[list[str]] = None
    converted_ingredients: Optional[list[str]] = None
    unit_warnings: Optional[list[str]] = None


class RecipeRead(BaseModel):
    id: int
    title: str
    source_url: str
    image_url: Optional[str] = None
    servings: Optional[str] = None
    total_time: Optional[int] = None
    ingredients: list[str]
    instructions: list[str]
    category: Optional[str] = None
    notes: Optional[str] = None
    rating: Optional[float] = None


class ScrapeRequest(BaseModel):
    url: str


class LoginRequest(BaseModel):
    password: str


class LoginResponse(BaseModel):
    token: str


class RecipeImageRead(BaseModel):
    id: int
    recipe_id: int
    image_url: str
    public_id: Optional[str] = None
    is_cover: bool
    created_at: datetime
