import Link from "next/link";
import { getRecipes, Recipe } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  let recipes: Recipe[] = [];

  try {
    recipes = await getRecipes();
  } catch (error) {
    console.error("Could not load recipes for homepage:", error);
    recipes = [];
  }

  const randomRecipe =
    recipes.length > 0
      ? recipes[Math.floor(Math.random() * recipes.length)]
      : null;

  return (
    <main className="page">
      <section className="hero">
        <div className="heroContent">
          <p className="eyebrow">Private Recipe Library</p>

          <h1>Recipe Collector</h1>

          <p className="subtitle">
            Save recipes from different websites, extract ingredients and
            instructions automatically, and organize everything in one clean
            private collection.
          </p>

          <div className="buttonGroup">
            <Link href="/add" className="primaryButton">
              Add Recipe
            </Link>

            <Link href="/recipes" className="secondaryButton">
              View Recipes
            </Link>
          </div>

          <div className="featureGrid">
            <div className="featureCard">
              <span>🔗</span>
              <h3>Import by URL</h3>
              <p>Paste a recipe link and let the app extract the useful data.</p>
            </div>

            <div className="featureCard">
              <span>🥘</span>
              <h3>Organize Recipes</h3>
              <p>Save recipes with categories, notes, ingredients and steps.</p>
            </div>

            <div className="featureCard">
              <span>🔍</span>
              <h3>Search Later</h3>
              <p>Build your own searchable recipe collection over time.</p>
            </div>
          </div>
        </div>

        {randomRecipe ? (
          <Link href={`/recipes/${randomRecipe.id}`} className="previewCard homeRecipePreview">
            {randomRecipe.image_url ? (
              <img
                src={randomRecipe.image_url}
                alt={randomRecipe.title}
                className="homeRecipeImage"
              />
            ) : (
              <div className="homeRecipePlaceholder">
                <span>🥘</span>
              </div>
            )}

            <div className="homeRecipeContent">
              <p className="smallLabel">Random saved recipe</p>
              <h2>{randomRecipe.title}</h2>

              <div className="recipeDetailMeta">
                {randomRecipe.total_time && (
                  <span>{randomRecipe.total_time} min</span>
                )}
                {randomRecipe.servings && <span>{randomRecipe.servings}</span>}
                {randomRecipe.category && <span>{randomRecipe.category}</span>}
              </div>

              <p className="openRecipeHint">Open full recipe →</p>
            </div>
          </Link>
        ) : (
          <div className="previewCard">
            <div className="previewHeader">
              <div>
                <p className="smallLabel">No recipe loaded</p>
                <h2>Your saved recipes will appear here</h2>
              </div>
            </div>

            <div className="ingredientBox">
              <p>How to start</p>
              <ul>
                <li>Add your first recipe from a URL.</li>
                <li>Save it to your private collection.</li>
                <li>Reload the homepage to see a random saved recipe.</li>
              </ul>
            </div>

            <Link href="/add" className="primaryButton">
              Add Recipe
            </Link>
          </div>
        )}
      </section>
    </main>
  );
}