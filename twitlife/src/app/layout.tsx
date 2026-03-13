import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "TwitLife",
  description: "AI Social Simulation",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased min-h-screen bg-navy text-text-main">
        {children}
      </body>
    </html>
  );
}
