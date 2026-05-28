"use client";

import { useMemo, useState } from "react";

type PortionCalculatorProps = {
  ingredients: string[];
  servings?: string | null;
};

function extractServingsNumber(servings?: string | null): number {
  if (!servings) return 2;

  const match = servings.match(/\d+(?:[.,]\d+)?/);

  if (!match) return 2;

  return Number(match[0].replace(",", "."));
}

function formatNumber(value: number): string {
  if (Number.isInteger(value)) {
    return String(value);
  }

  const rounded = Math.round(value * 100) / 100;

  if (rounded === 0.25) return "1/4";
  if (rounded === 0.5) return "1/2";
  if (rounded === 0.75) return "3/4";
  if (rounded === 1.5) return "1 1/2";
  if (rounded === 2.5) return "2 1/2";

  return String(rounded).replace(".", ",");
}

function parseAmount(value: string): number | null {
  const normalized = value.replace(",", ".");

  if (normalized.includes("/")) {
    const [top, bottom] = normalized.split("/").map(Number);

    if (!top || !bottom) return null;

    return top / bottom;
  }

  const number = Number(normalized);

  if (Number.isNaN(number)) return null;

  return number;
}

function scaleIngredient(ingredient: string, factor: number): string {
  return ingredient.replace(
    /(\d+(?:[.,]\d+)?|\d+\/\d+)/,
    (match: string) => {
      const amount = parseAmount(match);

      if (amount === null) {
        return match;
      }

      return formatNumber(amount * factor);
    }
  );
}

function parsePositiveNumber(value: string): number | null {
  if (value.trim() === "") return null;

  const parsed = Number(value.replace(",", "."));

  if (Number.isNaN(parsed)) return null;
  if (parsed <= 0) return null;

  return parsed;
}

export default function PortionCalculator({
  ingredients,
  servings,
}: PortionCalculatorProps) {
  const detectedServings = extractServingsNumber(servings);

  const [originalServingsInput, setOriginalServingsInput] = useState(
    String(detectedServings)
  );

  const [targetServingsInput, setTargetServingsInput] = useState(
    String(detectedServings)
  );

  const originalServings = parsePositiveNumber(originalServingsInput);
  const targetServings = parsePositiveNumber(targetServingsInput);

  const factor =
    originalServings && targetServings ? targetServings / originalServings : 1;

  const scaledIngredients = useMemo(() => {
    return ingredients.map((ingredient) => scaleIngredient(ingredient, factor));
  }, [ingredients, factor]);

  return (
    <section className="recipeDetailSection portionCalculator">
      <h2>Portion calculator</h2>

      <p className="portionCalculatorText">
        Adjust the number of portions and the ingredient amounts will be scaled
        automatically.
      </p>

      <div className="portionControls">
        <div>
          <label className="formLabel">Original portions</label>
          <input
            type="text"
            inputMode="decimal"
            value={originalServingsInput}
            onChange={(event) => setOriginalServingsInput(event.target.value)}
            className="textInput"
          />
        </div>

        <div>
          <label className="formLabel">Wanted portions</label>
          <input
            type="text"
            inputMode="decimal"
            value={targetServingsInput}
            onChange={(event) => setTargetServingsInput(event.target.value)}
            className="textInput"
          />
        </div>
      </div>

      {originalServings && targetServings ? (
        <div className="scaledIngredientBox">
          <p>Scaled ingredients</p>

          <ul>
            {scaledIngredients.map((ingredient, index) => (
              <li key={index}>{ingredient}</li>
            ))}
          </ul>
        </div>
      ) : (
        <div className="scaledIngredientBox">
          <p>Please enter valid portion numbers.</p>
        </div>
      )}
    </section>
  );
}