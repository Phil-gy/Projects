"use client";

import { isLoggedIn } from "@/lib/auth";
import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import {
  Recipe,
  RecipeDraft,
  RecipeImage,
  deleteRecipe,
  deleteRecipeImage,
  getRecipe,
  getRecipeImages,
  setRecipeCoverImage,
  updateRecipe,
  uploadRecipeImage,
} from "@/lib/api";

export default function RecipeDetailPage() {
  const params = useParams();
  const id = params.id as string;

  const [recipe, setRecipe] = useState<Recipe | null>(null);
  const [draft, setDraft] = useState<RecipeDraft | null>(null);
  const [images, setImages] = useState<RecipeImage[]>([]);
  const [selectedImageIndex, setSelectedImageIndex] = useState(0);

  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [admin, setAdmin] = useState(false);

  useEffect(() => {
    setAdmin(isLoggedIn());

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

        const loadedImages = await getRecipeImages(loadedRecipe.id);
        setImages(loadedImages);

        const coverIndex = loadedImages.findIndex((image) => image.is_cover);
        setSelectedImageIndex(coverIndex >= 0 ? coverIndex : 0);
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

  const selectedImage = images[selectedImageIndex];

  function showPreviousImage() {
    if (images.length === 0) return;

    setSelectedImageIndex((currentIndex) =>
      currentIndex === 0 ? images.length - 1 : currentIndex - 1
    );
  }

  function showNextImage() {
    if (images.length === 0) return;

    setSelectedImageIndex((currentIndex) =>
      currentIndex === images.length - 1 ? 0 : currentIndex + 1
    );
  }

  async function handleImageUpload(event: React.ChangeEvent<HTMLInputElement>) {
    if (!recipe) return;

    const file = event.target.files?.[0];

    if (!file) return;

    try {
      setUploading(true);

      const uploadedImage = await uploadRecipeImage(recipe.id, file);
      const updatedImages = await getRecipeImages(recipe.id);

      setImages(updatedImages);

      const newImageIndex = updatedImages.findIndex(
        (image) => image.id === uploadedImage.id
      );

      if (newImageIndex >= 0) {
        setSelectedImageIndex(newImageIndex);
      }

      if (uploadedImage.is_cover) {
        setRecipe({
          ...recipe,
          image_url: uploadedImage.image_url,
        });
      }

      alert("Image uploaded!");
    } catch (error) {
      console.error(error);
      alert(
  error instanceof Error
    ? error.message
    : "Image could not be uploaded."
    );
    } finally {
      setUploading(false);
      event.target.value = "";
    }
  }

  async function handleSetCoverImage() {
    if (!recipe || !selectedImage) return;

    try {
      const coverImage = await setRecipeCoverImage(recipe.id, selectedImage.id);
      const updatedImages = await getRecipeImages(recipe.id);

      setImages(updatedImages);
      setRecipe({
        ...recipe,
        image_url: coverImage.image_url,
      });

      const coverIndex = updatedImages.findIndex(
        (image) => image.id === coverImage.id
      );

      setSelectedImageIndex(coverIndex >= 0 ? coverIndex : 0);

      alert("Cover image updated!");
    } catch (error) {
      console.error(error);
      alert("Cover image could not be updated.");
    }
  }

  async function handleDeleteImage() {
    if (!recipe || !selectedImage) return;

    const confirmed = confirm("Do you really want to delete this image?");
    if (!confirmed) return;

    try {
      await deleteRecipeImage(recipe.id, selectedImage.id);

      const updatedImages = await getRecipeImages(recipe.id);
      setImages(updatedImages);
      setSelectedImageIndex(0);

      const coverImage = updatedImages.find((image) => image.is_cover);

      if (coverImage) {
        setRecipe({
          ...recipe,
          image_url: coverImage.image_url,
        });
      }

      alert("Image deleted!");
    } catch (error) {
      console.error(error);
      alert("Image could not be deleted.");
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
          Rabeas Recipes
        </Link>

        <div className="navLinks">
          <Link href="/add">Add</Link>
          <Link href="/recipes">Recipes</Link>
        </div>
      </nav>

      <section className="recipeDetailLayout">
        <article className="recipeDetailCard">
          {!isEditing && (
            <section className="recipeImageGallery">
              {selectedImage ? (
                <>
                  <div className="recipeMainImageWrapper">
                    <img
                      src={selectedImage.image_url}
                      alt={recipe.title}
                      className="recipeGalleryMainImage"
                    />

                    {images.length > 1 && (
                      <>
                        <button
                          type="button"
                          onClick={showPreviousImage}
                          className="galleryArrow galleryArrowLeft"
                        >
                          ‹
                        </button>

                        <button
                          type="button"
                          onClick={showNextImage}
                          className="galleryArrow galleryArrowRight"
                        >
                          ›
                        </button>
                      </>
                    )}
                  </div>

                  {images.length > 1 && (
                    <div className="recipeThumbnailRow">
                      {images.map((image, index) => (
                        <button
                          key={image.id}
                          type="button"
                          onClick={() => setSelectedImageIndex(index)}
                          className="recipeThumbnailButton"
                        >
                          <img
                            src={image.image_url}
                            alt={`${recipe.title} image ${index + 1}`}
                            className={
                              index === selectedImageIndex
                                ? "recipeThumbnail recipeThumbnailActive"
                                : "recipeThumbnail"
                            }
                          />
                        </button>
                      ))}
                    </div>
                  )}
                </>
              ) : recipe.image_url ? (
                <img
                  src={recipe.image_url}
                  alt={recipe.title}
                  className="recipeGalleryMainImage"
                />
              ) : (
                <div className="recipeImagePlaceholder">
                  <span>🥘</span>
                  <p>No pictures yet</p>
                </div>
              )}

              {admin && (
                <div className="galleryAdminControls">
                  <label className="imageUploadLabel">
                    {uploading ? "Uploading..." : "Upload picture"}
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleImageUpload}
                      disabled={uploading}
                      className="imageUploadInput"
                    />
                  </label>

                  {selectedImage && (
                    <>
                      <button
                        type="button"
                        onClick={handleSetCoverImage}
                        className="secondaryButton"
                      >
                        Set as cover
                      </button>

                      <button
                        type="button"
                        onClick={handleDeleteImage}
                        className="dangerButton"
                      >
                        Delete picture
                      </button>
                    </>
                  )}
                </div>
              )}
            </section>
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
                {admin && (
                  <button
                    onClick={() => setIsEditing(true)}
                    className="primaryButton"
                  >
                    Edit Recipe
                  </button>
                )}

                <a
                  href={recipe.source_url}
                  target="_blank"
                  rel="noreferrer"
                  className="secondaryButton"
                >
                  Open Original
                </a>

                {admin && (
                  <button onClick={handleDelete} className="dangerButton">
                    Delete Recipe
                  </button>
                )}
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