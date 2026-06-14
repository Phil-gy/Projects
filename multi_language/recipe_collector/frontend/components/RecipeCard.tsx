import Link from "next/link";
import { Recipe } from "@/lib/api";

type RecipeCardProps = {
  recipe: Recipe;
};

function isInstagramRecipe(recipe: Recipe): boolean {
  return (
    recipe.category?.toLowerCase() === "instagram" ||
    recipe.source_url.toLowerCase().includes("instagram.com")
  );
}

export default function RecipeCard({ recipe }: RecipeCardProps) {
  return (
    <article className="recipeCard">
      <Link href={`/recipes/${recipe.id}`} className="recipeCardClickableArea">
        {recipe.image_url && (
          <img
            src={recipe.image_url}
            alt={recipe.title}
            className={
              isInstagramRecipe(recipe)
                ? "recipeImage instagramRecipeCardImage"
                : "recipeImage"
            }
          />
        )}

        <div className="recipeCardContent">
          <div className="recipeDetailMeta">
            {recipe.category && <span>{recipe.category}</span>}
            {recipe.total_time && <span>{recipe.total_time} min</span>}
            {recipe.servings && <span>{recipe.servings}</span>}

            {recipe.rating !== null && recipe.rating !== undefined && (
              <span>⭐ {recipe.rating}/10</span>
            )}
          </div>

          <h2>{recipe.title}</h2>

          <section>
            <h3>Ingredients</h3>
            <ul>
              {recipe.ingredients.slice(0, 3).map((ingredient, index) => (
                <li key={index}>{ingredient}</li>
              ))}
            </ul>
          </section>

          <section>
            <h3>Steps</h3>
            <ol>
              {recipe.instructions.slice(0, 2).map((step, index) => (
                <li key={index}>{step}</li>
              ))}
            </ol>
          </section>

          <p className="openRecipeHint">Open recipe details →</p>
        </div>
      </Link>
    </article>
  );
}
