import type { ReactNode } from "react";
import "./globals.css";

export const metadata = {
  title: "Recipe Collector",
  description: "Private recipe organizer",
  icons: {
    icon: "/icon.png",
  },
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}