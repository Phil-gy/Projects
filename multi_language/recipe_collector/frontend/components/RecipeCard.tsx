import Link from "next/link";
import { Recipe } from "@/lib/api";

type RecipeCardProps = {
  recipe: Recipe;
};

export default function RecipeCard({ recipe }: RecipeCardProps) {
  return (
    <article className="recipeCard">
      <Link href={`/recipes/${recipe.id}`} className="recipeCardClickableArea">
        {recipe.image_url ? (
          <img
            src={recipe.image_url}
            alt={recipe.title}
            className="recipeCardImage"
          />
        ) : (
          <div className="recipeImagePlaceholder">
            <span>🥘</span>
          </div>
        )}

        <div className="recipeCardBody">
          <div className="recipeCardMeta">
            {recipe.category && <span>{recipe.category}</span>}
            {recipe.total_time && <span>{recipe.total_time} min</span>}
            {recipe.servings && <span>{recipe.servings}</span>}
          </div>

          <h2>{recipe.title}</h2>

          <div className="recipePreviewLists">
            <div>
              <p>Ingredients</p>
              <ul>
                {recipe.ingredients.slice(0, 3).map((ingredient, index) => (
                  <li key={index}>{ingredient}</li>
                ))}
              </ul>
            </div>

            <div>
              <p>Steps</p>
              <ol>
                {recipe.instructions.slice(0, 2).map((step, index) => (
                  <li key={index}>{step}</li>
                ))}
              </ol>
            </div>
          </div>

          <p className="openRecipeHint">Open recipe details →</p>
        </div>
      </Link>
    </article>
  );
}