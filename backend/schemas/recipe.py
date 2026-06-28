from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class RecipeOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    title: str
    description: Optional[str]
    ingredients: str  # JSON string
    instructions: str
    cooking_time_minutes: Optional[int]
    servings: int
    cuisine: Optional[str]
    category: Optional[str]
    is_vegetarian: bool
    is_vegan: bool
    is_high_protein: bool
    is_gluten_free: bool
    calories: Optional[float]
    image_url: Optional[str]


class RecipeRecommendRequest(BaseModel):
    available_ingredients: List[str]
    filter_vegetarian: bool = False
    filter_vegan: bool = False
    filter_high_protein: bool = False
    max_cooking_time: Optional[int] = None
    use_expiring_first: bool = True
    top_k: int = 5


class RecipeRecommendResponse(BaseModel):
    recipes: List[RecipeOut]
    generated_recipe: Optional[str] = None  # Ollama-generated recipe text
    source: str = "faiss"  # "faiss" or "ollama"
