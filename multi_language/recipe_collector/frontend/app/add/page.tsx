"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { RecipeDraft, scrapeRecipe, saveRecipe } from "@/lib/api";
import { isLoggedIn } from "@/lib/auth";

const emptyRecipe: RecipeDraft = {
  title: "",
  source_url: "",
  image_url: "",
  servings: "",
  total_time: null,
  ingredients: [],
  instructions: [],
  category: "",
  notes: "",
};

export default function AddRecipePage() {
  const [allowed, setAllowed] = useState(false);
  const [url, setUrl] = useState("");
  const [draft, setDraft] = useState<RecipeDraft | null>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!isLoggedIn()) {
      window.location.href = "/login";
      return;
    }

    setAllowed(true);
  }, []);

  if (!allowed) {
    return (
      <main className="appPage">
        <p>Redirecting to login...</p>
      </main>
    );
  }

  async function handleScrape() {
    if (!url.trim()) {
      alert("Please enter a recipe URL.");
      return;
    }

    try {
      setLoading(true);
      const scrapedRecipe = await scrapeRecipe(url.trim());
      setDraft(scrapedRecipe);
    } catch (error) {
      console.error(error);
      alert(
        error instanceof Error
          ? error.message
          : "Recipe could not be scraped."
      );
    } finally {
      setLoading(false);
    }
  }

  function handleManualRecipe() {
    setDraft({
      ...emptyRecipe,
      source_url: url.trim() || "Manual recipe",
    });
  }

  function updateDraftField(field: keyof RecipeDraft, value: string) {
    if (!draft) return;

    setDraft({
      ...draft,
      [field]: value,
    });
  }

  function updateTotalTime(value: string) {
    if (!draft) return;

    setDraft({
      ...draft,
      total_time: value === "" ? null : Number(value),
    });
  }

  function updateIngredients(value: string) {
    if (!draft) return;

    setDraft({
      ...draft,
      ingredients: value
        .split("\n")
        .map((item) => item.trim())
        .filter((item) => item !== ""),
    });
  }

  function updateInstructions(value: string) {
    if (!draft) return;

    setDraft({
      ...draft,
      instructions: value
        .split("\n")
        .map((item) => item.trim())
        .filter((item) => item !== ""),
    });
  }

  async function handleSave() {
    if (!draft) return;

    if (!draft.title.trim()) {
      alert("Please enter a recipe title.");
      return;
    }

    if (draft.ingredients.length === 0) {
      alert("Please enter at least one ingredient.");
      return;
    }

    if (draft.instructions.length === 0) {
      alert("Please enter at least one instruction.");
      return;
    }

    try {
      setSaving(true);
      const savedRecipe = await saveRecipe(draft);
      alert("Recipe saved!");
      window.location.href = `/recipes/${savedRecipe.id}`;
    } catch (error) {
      console.error(error);
      alert("Recipe could not be saved.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <main className="appPage">
      <nav className="topNav">
        <Link href="/" className="brandLink">
          Rabeas Recipes
        </Link>

        <div className="navLinks">
          <Link href="/recipes">Recipes</Link>
          <Link href="/add">Add</Link>
        </div>
      </nav>

      <section className="addRecipeLayout">
        <div className="addRecipeCard">
          <p className="eyebrow">Add Recipe</p>
          <h1>Add a new recipe</h1>

          <p className="subtitle">
            Paste a recipe link to import it automatically, or write your own
            recipe manually.
          </p>

          <label className="formLabel">Recipe URL</label>
          <input
            value={url}
            onChange={(event) => setUrl(event.target.value)}
            placeholder="https://example.com/my-recipe"
            className="textInput"
          />

          <div className="recipeActionRow">
            <button
              onClick={handleScrape}
              disabled={loading || !url.trim()}
              className="primaryButton"
            >
              {loading ? "Scraping..." : "Scrape Recipe"}
            </button>

            <button
              onClick={handleManualRecipe}
              className="secondaryButton"
              type="button"
            >
              Write recipe manually
            </button>
          </div>
        </div>

        {draft && (
          <div className="addRecipeCard">
            <p className="eyebrow">
              {draft.source_url === "Manual recipe"
                ? "Manual Recipe"
                : "Review Recipe"}
            </p>

            <h2>Recipe details</h2>

            <label className="formLabel">Title</label>
            <input
              value={draft.title}
              onChange={(event) =>
                updateDraftField("title", event.target.value)
              }
              placeholder="Recipe title"
              className="textInput"
            />

            <label className="formLabel">Image URL</label>
            <input
              value={draft.image_url ?? ""}
              onChange={(event) =>
                updateDraftField("image_url", event.target.value)
              }
              placeholder="https://example.com/image.jpg"
              className="textInput"
            />

            {draft.image_url && (
              <img
                src={draft.image_url}
                alt={draft.title || "Recipe preview"}
                className="manualRecipePreviewImage"
              />
            )}

            <div className="twoColumnForm">
              <div>
                <label className="formLabel">Category</label>
                <input
                  value={draft.category ?? ""}
                  onChange={(event) =>
                    updateDraftField("category", event.target.value)
                  }
                  placeholder="Dinner, Pasta, Dessert..."
                  className="textInput"
                />
              </div>

              <div>
                <label className="formLabel">Servings</label>
                <input
                  value={draft.servings ?? ""}
                  onChange={(event) =>
                    updateDraftField("servings", event.target.value)
                  }
                  placeholder="2 servings"
                  className="textInput"
                />
              </div>
            </div>

            <label className="formLabel">Total time in minutes</label>
            <input
              type="number"
              value={draft.total_time ?? ""}
              onChange={(event) => updateTotalTime(event.target.value)}
              placeholder="45"
              className="textInput"
            />

            <label className="formLabel">Ingredients</label>
            <textarea
              value={draft.ingredients.join("\n")}
              onChange={(event) => updateIngredients(event.target.value)}
              placeholder={"1 onion\n2 cloves garlic\n200g pasta"}
              rows={10}
              className="textArea"
            />

            <label className="formLabel">Instructions</label>
            <textarea
              value={draft.instructions.join("\n")}
              onChange={(event) => updateInstructions(event.target.value)}
              placeholder={
                "Cut the vegetables.\nHeat oil in a pan.\nCook everything together."
              }
              rows={12}
              className="textArea"
            />

            <label className="formLabel">Notes</label>
            <textarea
              value={draft.notes ?? ""}
              onChange={(event) =>
                updateDraftField("notes", event.target.value)
              }
              placeholder="Optional notes..."
              rows={5}
              className="textArea"
            />

            <div className="recipeActionRow">
              <button
                onClick={handleSave}
                disabled={saving}
                className="saveButtonInline"
              >
                {saving ? "Saving..." : "Save Recipe"}
              </button>

              <button
                onClick={() => setDraft(null)}
                className="secondaryButton"
                type="button"
              >
                Cancel
              </button>
            </div>
          </div>
        )}
      </section>
    </main>
  );
}