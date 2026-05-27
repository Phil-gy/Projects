"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { getRecipes, Recipe } from "@/lib/api";

export default function HomePage() {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [randomRecipe, setRandomRecipe] = useState<Recipe | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadRecipes() {
      try {
        const loadedRecipes = await getRecipes();
        setRecipes(loadedRecipes);

        if (loadedRecipes.length > 0) {
          const firstRandomRecipe =
            loadedRecipes[Math.floor(Math.random() * loadedRecipes.length)];

          setRandomRecipe(firstRandomRecipe);
        }
      } catch (error) {
        console.error("Could not load recipes for homepage:", error);
      } finally {
        setLoading(false);
      }
    }

    loadRecipes();
  }, []);

  function chooseRandomRecipe() {
    if (recipes.length === 0) return;

    if (recipes.length === 1) {
      setRandomRecipe(recipes[0]);
      return;
    }

    let newRandomRecipe = recipes[Math.floor(Math.random() * recipes.length)];

    while (randomRecipe && newRandomRecipe.id === randomRecipe.id) {
      newRandomRecipe = recipes[Math.floor(Math.random() * recipes.length)];
    }

    setRandomRecipe(newRandomRecipe);
  }

  return (
    <main className="page">
      <section className="hero">
        <div className="heroContent">
          <p className="eyebrow">Private Recipe Library</p>

          <h1>Rabeas Recipes</h1>

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

            <button
              type="button"
              onClick={chooseRandomRecipe}
              disabled={recipes.length === 0}
              className="randomButton"
            >
              Random Recipe
            </button>
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

        {loading ? (
          <div className="previewCard">
            <div className="previewHeader">
              <div>
                <p className="smallLabel">Loading</p>
                <h2>Loading random recipe...</h2>
              </div>
            </div>
          </div>
        ) : randomRecipe ? (
          <Link
            href={`/recipes/${randomRecipe.id}`}
            className="previewCard homeRecipePreview"
          >
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
                <li>Then use the random button to discover one.</li>
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