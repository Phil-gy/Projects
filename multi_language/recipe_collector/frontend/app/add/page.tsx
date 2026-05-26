"use client";

import Link from "next/link";
import { useState } from "react";
import { RecipeDraft, scrapeRecipe, saveRecipe } from "@/lib/api";

export default function AddRecipePage() {
  const [url, setUrl] = useState("");
  const [draft, setDraft] = useState<RecipeDraft | null>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  async function handleScrape() {
    try {
      setLoading(true);
      const scrapedRecipe = await scrapeRecipe(url);
      setDraft(scrapedRecipe);
    } catch (error) {
    if (error instanceof Error) {
        alert(error.message);
    } else {
        alert("Recipe could not be analyzed.");
    }
    }
}

  async function handleSave() {
    if (!draft) return;

    try {
      setSaving(true);
      await saveRecipe(draft);
      alert("Recipe saved!");
      setUrl("");
      setDraft(null);
    } catch (error) {
      alert("Recipe could not be saved.");
    } finally {
      setSaving(false);
    }
  }

  function updateDraftField(field: keyof RecipeDraft, value: string) {
    if (!draft) return;

    setDraft({
      ...draft,
      [field]: value,
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

      <section className="pageHeader">
        <p className="eyebrow">Import Recipe</p>
        <h1>Add a new recipe</h1>
        <p className="subtitle">
          Paste a recipe URL, let the app extract the ingredients and instructions,
          then review everything before saving it to your private collection.
        </p>
      </section>

      <section className="contentGrid">
        <div className="mainPanel">
          <div className="glassPanel">
            <h2>Recipe URL</h2>
            <p className="panelText">
              Use a recipe page with structured data. If extraction fails, you can
              still add manual editing later.
            </p>

            <div className="urlForm">
              <input
                value={url}
                onChange={(event) => setUrl(event.target.value)}
                placeholder="https://example.com/recipe"
                className="textInput"
              />

              <button
                onClick={handleScrape}
                disabled={loading || !url}
                className="primaryButton"
              >
                {loading ? "Analyzing..." : "Analyze Recipe"}
              </button>
            </div>
          </div>

          {draft && (
            <div className="glassPanel reviewPanel">
              <div className="sectionTitleRow">
                <div>
                  <p className="smallLabel">Review before saving</p>
                  <h2>{draft.title || "Untitled Recipe"}</h2>
                </div>

                {draft.total_time && (
                  <span className="timeBadge">{draft.total_time} min</span>
                )}
              </div>

              {draft.image_url && (
                <img
                  src={draft.image_url}
                  alt={draft.title}
                  className="recipeHeroImage"
                />
              )}

              <label className="formLabel">Title</label>
              <input
                value={draft.title}
                onChange={(event) => updateDraftField("title", event.target.value)}
                className="textInput"
              />

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

              <label className="formLabel">Ingredients</label>
              <textarea
                value={draft.ingredients.join("\n")}
                onChange={(event) => updateIngredients(event.target.value)}
                rows={8}
                className="textArea"
              />

              <label className="formLabel">Instructions</label>
              <textarea
                value={draft.instructions.join("\n")}
                onChange={(event) => updateInstructions(event.target.value)}
                rows={10}
                className="textArea"
              />

              <label className="formLabel">Notes</label>
              <textarea
                value={draft.notes ?? ""}
                onChange={(event) => updateDraftField("notes", event.target.value)}
                rows={4}
                placeholder="Personal notes, changes, ideas..."
                className="textArea"
              />

              <button
                onClick={handleSave}
                disabled={saving}
                className="saveButton"
              >
                {saving ? "Saving..." : "Save Recipe"}
              </button>
            </div>
          )}
        </div>

        <aside className="sidePanel">
          <div className="tipCard">
            <span>💡</span>
            <h3>How it works</h3>
            <p>
              The backend loads the recipe page, extracts structured recipe data,
              and sends it back to the frontend for review.
            </p>
          </div>

          <div className="tipCard">
            <span>✅</span>
            <h3>Good portfolio feature</h3>
            <p>
              This page shows API communication, form handling, error handling,
              and real data processing.
            </p>
          </div>

          <div className="tipCard">
            <span>⚠️</span>
            <h3>Important</h3>
            <p>
              Keep copied recipe data out of GitHub. Use demo data in your public
              repository.
            </p>
          </div>
        </aside>
      </section>
    </main>
  );
}