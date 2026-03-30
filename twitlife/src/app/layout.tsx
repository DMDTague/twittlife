import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/context/AuthContext";

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
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
