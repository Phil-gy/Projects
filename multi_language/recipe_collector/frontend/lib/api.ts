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

export async function scrapeRecipe(url: string): Promise<RecipeDraft> {
  const response = await fetch(`${API_BASE_URL}/recipes/scrape`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
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
    headers: {
      "Content-Type": "application/json",
    },
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