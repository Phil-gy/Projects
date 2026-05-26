"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import {
  Recipe,
  RecipeDraft,
  deleteRecipe,
  getRecipe,
  updateRecipe,
} from "@/lib/api";

export default function RecipeDetailPage() {
  const params = useParams();
  const id = params.id as string;

  const [recipe, setRecipe] = useState<Recipe | null>(null);
  const [draft, setDraft] = useState<RecipeDraft | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    async function loadRecipe() {
      try {
        const loadedRecipe = await getRecipe(id);

        setRecipe(loadedRecipe);
        setDraft({
          title: loadedRecipe.title,
          source_url: loadedRecipe.source_url,
          image_url: loadedRecipe.image_url,
          servings: loadedRecipe.servings,
          total_time: loadedRecipe.total_time,
          ingredients: loadedRecipe.ingredients,
          instructions: loadedRecipe.instructions,
          category: loadedRecipe.category,
          notes: loadedRecipe.notes,
        });
      } catch (error) {
        console.error(error);
        alert("Recipe could not be loaded.");
      } finally {
        setLoading(false);
      }
    }

    if (id) {
      loadRecipe();
    }
  }, [id]);

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

  async function handleSave() {
    if (!recipe || !draft) return;

    try {
      setSaving(true);
      const updatedRecipe = await updateRecipe(recipe.id, draft);
      setRecipe(updatedRecipe);
      setIsEditing(false);
      alert("Recipe updated!");
    } catch (error) {
      console.error(error);
      alert("Recipe could not be updated.");
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete() {
    if (!recipe) return;

    const confirmed = confirm("Do you really want to delete this recipe?");
    if (!confirmed) return;

    try {
      await deleteRecipe(recipe.id);
      window.location.href = "/recipes";
    } catch (error) {
      console.error(error);
      alert("Recipe could not be deleted.");
    }
  }

  if (loading) {
    return (
      <main className="appPage">
        <p>Loading recipe...</p>
      </main>
    );
  }

  if (!recipe || !draft) {
    return (
      <main className="appPage">
        <h1>Recipe not found</h1>
        <Link href="/recipes" className="primaryButton">
          Back to recipes
        </Link>
      </main>
    );
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

      <section className="recipeDetailLayout">
        <article className="recipeDetailCard">
          {recipe.image_url && (
            <img
              src={recipe.image_url}
              alt={recipe.title}
              className="recipeDetailImage"
            />
          )}

          {!isEditing ? (
            <>
              <p className="eyebrow">Recipe Details</p>
              <h1>{recipe.title}</h1>

              <div className="recipeDetailMeta">
                {recipe.total_time && <span>{recipe.total_time} min</span>}
                {recipe.servings && <span>{recipe.servings}</span>}
                {recipe.category && <span>{recipe.category}</span>}
              </div>

              <section className="recipeDetailSection">
                <h2>Ingredients</h2>
                <ul>
                  {recipe.ingredients.map((ingredient, index) => (
                    <li key={index}>{ingredient}</li>
                  ))}
                </ul>
              </section>

              <section className="recipeDetailSection">
                <h2>Instructions</h2>
                <ol>
                  {recipe.instructions.map((step, index) => (
                    <li key={index}>{step}</li>
                  ))}
                </ol>
              </section>

              {recipe.notes && (
                <section className="recipeDetailSection">
                  <h2>Notes</h2>
                  <p>{recipe.notes}</p>
                </section>
              )}

              <div className="recipeActionRow">
                <button
                  onClick={() => setIsEditing(true)}
                  className="primaryButton"
                >
                  Edit Recipe
                </button>

                <a
                  href={recipe.source_url}
                  target="_blank"
                  rel="noreferrer"
                  className="secondaryButton"
                >
                  Open Original
                </a>

                <button onClick={handleDelete} className="dangerButton">
                  Delete
                </button>
              </div>
            </>
          ) : (
            <>
              <p className="eyebrow">Edit Recipe</p>
              <h1>Edit recipe</h1>

              <label className="formLabel">Title</label>
              <input
                value={draft.title}
                onChange={(event) =>
                  updateDraftField("title", event.target.value)
                }
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
                    className="textInput"
                  />
                </div>
              </div>

              <label className="formLabel">Ingredients</label>
              <textarea
                value={draft.ingredients.join("\n")}
                onChange={(event) => updateIngredients(event.target.value)}
                rows={10}
                className="textArea"
              />

              <label className="formLabel">Instructions</label>
              <textarea
                value={draft.instructions.join("\n")}
                onChange={(event) => updateInstructions(event.target.value)}
                rows={14}
                className="textArea"
              />

              <label className="formLabel">Notes</label>
              <textarea
                value={draft.notes ?? ""}
                onChange={(event) =>
                  updateDraftField("notes", event.target.value)
                }
                rows={5}
                className="textArea"
              />

              <div className="recipeActionRow">
                <button
                  onClick={handleSave}
                  disabled={saving}
                  className="saveButtonInline"
                >
                  {saving ? "Saving..." : "Save Changes"}
                </button>

                <button
                  onClick={() => setIsEditing(false)}
                  className="secondaryButton"
                >
                  Cancel
                </button>
              </div>
            </>
          )}
        </article>
      </section>
    </main>
  );
}