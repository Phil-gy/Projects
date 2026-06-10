"use client";

import Link from "next/link";
import { useState } from "react";
import { loginAdmin } from "@/lib/api";
import { saveToken } from "@/lib/auth";

export default function LoginPage() {
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleLogin() {
    try {
      setLoading(true);
      const token = await loginAdmin(password);
      saveToken(token);

      const searchParams = new URLSearchParams(window.location.search);
      const nextPath = searchParams.get("next");

      window.location.href =
        nextPath && nextPath.startsWith("/") && !nextPath.startsWith("//")
          ? nextPath
          : "/recipes";
    } catch (error) {
      alert("Wrong password.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="appPage">
      <nav className="topNav">
        <Link href="/" className="brandLink">
          Recipe Collector
        </Link>

        <div className="navLinks">
          <Link href="/recipes">Recipes</Link>
          <Link href="/add">Add</Link>
        </div>
      </nav>

      <section className="loginPanel">
        <p className="eyebrow">Admin Login</p>
        <h1>Login</h1>

        <p className="subtitle">
          Login is only needed to add, edit or delete recipes. Everyone can
          still view the recipe collection.
        </p>

        <label className="formLabel">Admin password</label>
        <input
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          placeholder="Enter admin password"
          className="textInput"
        />

        <button
          onClick={handleLogin}
          disabled={loading || !password}
          className="saveButton"
        >
          {loading ? "Logging in..." : "Login"}
        </button>
      </section>
    </main>
  );
}
