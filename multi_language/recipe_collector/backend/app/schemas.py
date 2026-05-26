from typing import Optional
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


class ScrapeRequest(BaseModel):
    url: str