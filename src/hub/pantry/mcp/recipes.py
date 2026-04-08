import json

from fastmcp import FastMCP
from fastmcp.exceptions import ResourceError

from hub.pantry import get_db
from hub.pantry.models import Recipe

mcp = FastMCP("recipes")


@mcp.resource("hub://recipes/{name}")
def get_recipe(name: str) -> str:
    db = get_db()
    recipe = db.get_or_none(Recipe, name)
    if not recipe:
        raise ResourceError(f"Recipe not found: {name}")
    return recipe.model_dump_json()


@mcp.resource("hub://recipes")
def get_recipes() -> str:
    db = get_db()
    recipes = db.query(Recipe)
    return json.dumps([r.model_dump() for r in recipes], indent=2)
