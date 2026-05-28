"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import RecipeCard from "@/components/RecipeCard";
import { getRecipes, Recipe } from "@/lib/api";

type SortOption = "default" | "best-rated" | "lowest-rated";

export default function RecipesPage() {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchText, setSearchText] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [sortOption, setSortOption] = useState<SortOption>("default");

  useEffect(() => {
    async function loadRecipes() {
      try {
        const loadedRecipes = await getRecipes();
        setRecipes(loadedRecipes);
      } catch (error) {
        console.error("Could not load recipes:", error);
        alert("Recipes could not be loaded.");
      } finally {
        setLoading(false);
      }
    }

    loadRecipes();
  }, []);

  const categories = useMemo(() => {
    const categorySet = new Set<string>();

    recipes.forEach((recipe) => {
      if (recipe.category && recipe.category.trim() !== "") {
        categorySet.add(recipe.category.trim());
      }
    });

    return ["All", ...Array.from(categorySet).sort()];
  }, [recipes]);

  const filteredRecipes = useMemo(() => {
    const normalizedSearch = searchText.trim().toLowerCase();

    const filtered = recipes.filter((recipe) => {
      const matchesCategory =
        selectedCategory === "All" ||
        recipe.category?.trim() === selectedCategory;

      const searchableText = [
        recipe.title,
        recipe.category,
        recipe.notes,
        recipe.servings,
        recipe.ingredients.join(" "),
        recipe.instructions.join(" "),
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();

      const matchesSearch =
        normalizedSearch === "" || searchableText.includes(normalizedSearch);

      return matchesCategory && matchesSearch;
    });

    const sorted = [...filtered];

    if (sortOption === "best-rated") {
      sorted.sort((a, b) => {
        const ratingA = a.rating ?? -1;
        const ratingB = b.rating ?? -1;

        return ratingB - ratingA;
      });
    }

    if (sortOption === "lowest-rated") {
      sorted.sort((a, b) => {
        const ratingA = a.rating ?? Number.POSITIVE_INFINITY;
        const ratingB = b.rating ?? Number.POSITIVE_INFINITY;

        return ratingA - ratingB;
      });
    }

    return sorted;
  }, [recipes, searchText, selectedCategory, sortOption]);

  function clearFilters() {
    setSearchText("");
    setSelectedCategory("All");
    setSortOption("default");
  }

  if (loading) {
    return (
      <main className="appPage">
        <nav className="topNav">
          <Link href="/" className="brandLink">
            Rabeas Recipes
          </Link>

          <div className="navLinks">
            <Link href="/add">Add</Link>
            <Link href="/recipes">Recipes</Link>
          </div>
        </nav>

        <p>Loading recipes...</p>
      </main>
    );
  }

  return (
    <main className="appPage">
      <nav className="topNav">
        <Link href="/" className="brandLink">
          Rabeas Recipes
        </Link>

        <div className="navLinks">
          <Link href="/add">Add</Link>
          <Link href="/recipes">Recipes</Link>
        </div>
      </nav>

      <section className="recipesHeader">
        <div>
          <p className="eyebrow">Recipe Collection</p>
          <h1>Saved recipes</h1>
          <p className="subtitle">
            Search your saved recipes, filter them by category, or sort them by
            rating.
          </p>
        </div>

        <Link href="/add" className="primaryButton">
          Add Recipe
        </Link>
      </section>

      <section className="recipeFilters">
        <div className="searchBox">
          <label className="formLabel">Search recipes</label>
          <input
            value={searchText}
            onChange={(event) => setSearchText(event.target.value)}
            placeholder="Search by title, ingredient, category..."
            className="textInput"
          />
        </div>

        <div className="categoryFilterBox">
          <label className="formLabel">Category</label>
          <select
            value={selectedCategory}
            onChange={(event) => setSelectedCategory(event.target.value)}
            className="selectInput"
          >
            {categories.map((category) => (
              <option key={category} value={category}>
                {category}
              </option>
            ))}
          </select>
        </div>

        <div className="sortFilterBox">
          <label className="formLabel">Sort by</label>
          <select
            value={sortOption}
            onChange={(event) =>
              setSortOption(event.target.value as SortOption)
            }
            className="selectInput"
          >
            <option value="default">Default</option>
            <option value="best-rated">Best rated</option>
            <option value="lowest-rated">Lowest rated</option>
          </select>
        </div>

        <button type="button" onClick={clearFilters} className="secondaryButton">
          Clear filters
        </button>
      </section>

      <section className="filterResultInfo">
        <p>
          Showing <strong>{filteredRecipes.length}</strong> of{" "}
          <strong>{recipes.length}</strong> recipes
        </p>
      </section>

      {filteredRecipes.length > 0 ? (
        <section className="recipeGrid">
          {filteredRecipes.map((recipe) => (
            <RecipeCard key={recipe.id} recipe={recipe} />
          ))}
        </section>
      ) : (
        <section className="emptyRecipesBox">
          <h2>No recipes found</h2>
          <p>
            Try another search term, choose another category, change the sorting,
            or clear the filters.
          </p>

          <button
            type="button"
            onClick={clearFilters}
            className="primaryButton"
          >
            Clear filters
          </button>
        </section>
      )}
    </main>
  );
}