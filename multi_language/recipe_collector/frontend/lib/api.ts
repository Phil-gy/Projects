import { getToken } from "./auth";

export type Recipe = {
  id: number;
  title: string;
  source_url: string;
  image_url?: string | null;
  servings?: string | null;
  total_time?: number | null;
  ingredients: string[];
  instructions: string[];
  category?: string | null;
  notes?: string | null;
};

export type RecipeDraft = {
  title: string;
  source_url: string;
  image_url?: string | null;
  servings?: string | null;
  total_time?: number | null;
  ingredients: string[];
  instructions: string[];
  category?: string | null;
  notes?: string | null;
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

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
    const errorData = await response.json().catch(() => null);

    const message =
      errorData?.detail ??
      `Could not scrape recipe. Status: ${response.status}`;

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
    throw new Error("Could not save recipe");
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
    throw new Error("Could not update recipe");
  }

  return response.json();
}

export async function deleteRecipe(id: number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/recipes/${id}`, {
    method: "DELETE",
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error("Could not delete recipe");
  }
}