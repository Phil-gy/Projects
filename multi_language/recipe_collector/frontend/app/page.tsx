import Link from "next/link";

export default function HomePage() {
  return (
    <main className="page">
      <section className="hero">
        <div className="heroContent">
          <p className="eyebrow">Private Recipe Library from Philipp for Rabea</p>

          <h1>Recipe Collector</h1>

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

        <div className="previewCard">
          <div className="previewHeader">
            <div>
              <p className="smallLabel">Today&apos;s idea</p>
              <h2>Creamy Tomato Pasta</h2>
            </div>
            <span className="timeBadge">25 min</span>
          </div>

          <div className="ingredientBox">
            <p>Ingredients</p>
            <ul>
              <li>200g pasta</li>
              <li>1 can tomatoes</li>
              <li>Garlic, basil, olive oil</li>
            </ul>
          </div>

          <div className="stepsBox">
            <p>Instructions</p>
            <ol>
              <li>Cook the pasta.</li>
              <li>Prepare the sauce.</li>
              <li>Mix everything and serve.</li>
            </ol>
          </div>
        </div>
      </section>
    </main>
  );
}