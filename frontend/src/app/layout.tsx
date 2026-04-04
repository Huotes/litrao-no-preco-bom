import type { Metadata } from "next";
import type { ReactNode } from "react";

import { BottomNav } from "@/components/BottomNav";
import "./globals.css";

export const metadata: Metadata = {
  title: "Litrão no Preço Bom",
  description: "Encontre as melhores promoções de bebidas alcoólicas na sua região",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="pt-BR">
      <body className="min-h-screen bg-[var(--bg-primary)] text-[var(--text-primary)] antialiased pb-20">
        <main className="mx-auto max-w-lg px-4">{children}</main>
        <BottomNav />
      </body>
    </html>
  );
}
