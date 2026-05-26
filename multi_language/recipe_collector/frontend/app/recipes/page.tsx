import Link from "next/link";
import { getRecipes } from "@/lib/api";
import RecipeCard from "@/components/RecipeCard";

export default async function RecipesPage() {
  const recipes = await getRecipes();

  return (
    <main className="appPage">
      <nav className="topNav">
        <Link href="/" className="brandLink">
          Recipe Collector
        </Link>

        <div className="navLinks">
          <Link href="/add">Add</Link>
          <Link href="/recipes">Recipes</Link>
        </div>
      </nav>

      <section className="pageHeader recipesHeader">
        <div>
          <p className="eyebrow">Your Collection</p>
          <h1>Saved recipes</h1>
          <p className="subtitle">
            Browse your private recipe library. Every saved recipe keeps the
            original source, extracted ingredients, instructions and personal notes.
          </p>
        </div>

        <Link href="/add" className="primaryButton">
          Add Recipe
        </Link>
      </section>

      {recipes.length === 0 ? (
        <section className="emptyState">
          <div className="emptyIcon">🥘</div>
          <h2>No recipes saved yet</h2>
          <p>
            Start by importing your first recipe from a URL. Once saved, it will
            appear here as a recipe card.
          </p>

          <Link href="/add" className="primaryButton">
            Add your first recipe
          </Link>
        </section>
      ) : (
        <section className="recipesGrid">
          {recipes.map((recipe) => (
            <RecipeCard key={recipe.id} recipe={recipe} />
          ))}
        </section>
      )}
    </main>
  );
}