import type { ReactNode } from "react";
import "./globals.css";

export const metadata = {
  title: "Recipe Collector",
  description: "Phil.gy Recipe Collector for Rabea",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}