import { getToken, removeToken } from "./auth";

export type Recipe = {
  id: number;
  title: string;
  source_url: string;
  image_url?: string | null;
  servings?: string | null;
  total_time?: number | null;
  ingredients: string[];
  instructions: string[];
  rating?: number | null;
  category?: string | null;
  notes?: string | null;
};

export type RecipeDraft = {
  title: string;
  source_url: string;
  image_url?: string | null;
  image_options?: string[] | null;
  converted_ingredients?: string[] | null;
  unit_warnings?: string[] | null;
  servings?: string | null;
  total_time?: number | null;
  ingredients: string[];
  instructions: string[];
  rating?: number | null;
  category?: string | null;
  notes?: string | null;
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export class AuthSessionExpiredError extends Error {
  constructor() {
    super("Your admin login has expired. Please log in again.");
    this.name = "AuthSessionExpiredError";
  }
}

async function getErrorMessage(
  response: Response,
  fallbackMessage: string,
): Promise<string> {
  const errorData = await response.json().catch(() => null);

  return errorData?.detail ?? fallbackMessage;
}

function throwIfAuthFailed(response: Response, message: string): void {
  if (response.status !== 401) {
    return;
  }

  if (
    message === "Token expired" ||
    message === "Invalid token" ||
    message === "Missing authorization header"
  ) {
    removeToken();
    throw new AuthSessionExpiredError();
  }
}

function getAuthHeaders(): HeadersInit {
  const token = getToken();

  if (!token) {
    return {
      "Content-Type": "application/json",
    };
  }

  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
}

export async function loginAdmin(password: string): Promise<string> {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ password }),
  });

  if (!response.ok) {
    throw new Error("Wrong password");
  }

  const data = await response.json();
  return data.token;
}

export async function scrapeRecipe(url: string): Promise<RecipeDraft> {
  const response = await fetch(`${API_BASE_URL}/recipes/scrape`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({ url }),
  });

  if (!response.ok) {
    const message = await getErrorMessage(
      response,
      `Could not scrape recipe. Status: ${response.status}`,
    );

    throwIfAuthFailed(response, message);
    throw new Error(message);
  }

  return response.json();
}

export async function saveRecipe(recipe: RecipeDraft): Promise<Recipe> {
  const response = await fetch(`${API_BASE_URL}/recipes`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify(recipe),
  });

  if (!response.ok) {
    const message = await getErrorMessage(response, "Could not save recipe");

    throwIfAuthFailed(response, message);
    throw new Error(message);
  }

  return response.json();
}

export async function getRecipes(): Promise<Recipe[]> {
  const response = await fetch(`${API_BASE_URL}/recipes`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Could not load recipes");
  }

  return response.json();
}

export async function getRecipe(id: string): Promise<Recipe> {
  const url = `${API_BASE_URL}/recipes/${id}`;

  const response = await fetch(url, {
    cache: "no-store",
  });

  if (!response.ok) {
    const errorText = await response.text().catch(() => "");
    throw new Error(
      `Could not load recipe. Status: ${response.status}. URL: ${url}. ${errorText}`,
    );
  }

  return response.json();
}

export async function updateRecipe(
  id: number,
  recipe: RecipeDraft,
): Promise<Recipe> {
  const response = await fetch(`${API_BASE_URL}/recipes/${id}`, {
    method: "PUT",
    headers: getAuthHeaders(),
    body: JSON.stringify(recipe),
  });

  if (!response.ok) {
    const message = await getErrorMessage(response, "Could not update recipe");

    throwIfAuthFailed(response, message);
    throw new Error(message);
  }

  return response.json();
}

export async function deleteRecipe(id: number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/recipes/${id}`, {
    method: "DELETE",
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const message = await getErrorMessage(response, "Could not delete recipe");

    throwIfAuthFailed(response, message);
    throw new Error(message);
  }
}

export type RecipeImage = {
  id: number;
  recipe_id: number;
  image_url: string;
  public_id?: string | null;
  is_cover: boolean;
  created_at: string;
};

function getAuthOnlyHeaders(): HeadersInit {
  const token = getToken();

  if (!token) {
    return {};
  }

  return {
    Authorization: `Bearer ${token}`,
  };
}

export async function getRecipeImages(recipeId: number): Promise<RecipeImage[]> {
  const response = await fetch(`${API_BASE_URL}/recipes/${recipeId}/images`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Could not load recipe images");
  }

  return response.json();
}

export async function uploadRecipeImage(
  recipeId: number,
  file: File
): Promise<RecipeImage> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/recipes/${recipeId}/images`, {
    method: "POST",
    headers: getAuthOnlyHeaders(),
    body: formData,
  });

  if (!response.ok) {
    const message = await getErrorMessage(
      response,
      `Could not upload image. Status: ${response.status}`,
    );

    throwIfAuthFailed(response, message);
    throw new Error(message);
  }

  return response.json();
}

export async function setRecipeCoverImage(
  recipeId: number,
  imageId: number
): Promise<RecipeImage> {
  const response = await fetch(
    `${API_BASE_URL}/recipes/${recipeId}/images/${imageId}/cover`,
    {
      method: "PUT",
      headers: getAuthHeaders(),
    }
  );

  if (!response.ok) {
    const message = await getErrorMessage(
      response,
      "Could not set cover image",
    );

    throwIfAuthFailed(response, message);
    throw new Error(message);
  }

  return response.json();
}

export async function deleteRecipeImage(
  recipeId: number,
  imageId: number
): Promise<void> {
  const response = await fetch(
    `${API_BASE_URL}/recipes/${recipeId}/images/${imageId}`,
    {
      method: "DELETE",
      headers: getAuthHeaders(),
    }
  );

  if (!response.ok) {
    const message = await getErrorMessage(response, "Could not delete image");

    throwIfAuthFailed(response, message);
    throw new Error(message);
  }
}
