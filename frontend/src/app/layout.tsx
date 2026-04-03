import type { Metadata } from "next";
import Link from "next/link";
import type { ReactNode } from "react";

import "./globals.css";

export const metadata: Metadata = {
  title: "Litrão no Preço Bom",
  description: "Encontre as melhores promoções de bebidas alcoólicas",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="pt-BR">
      <body className="min-h-screen bg-gray-50 text-gray-900 antialiased dark:bg-gray-950 dark:text-gray-100">
        <header className="border-b border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-900">
          <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
            <Link href="/" className="text-xl font-bold text-amber-600">
              Litrão no Preço Bom
            </Link>
          </div>
        </header>

        <main className="mx-auto max-w-5xl px-4 py-6">{children}</main>

        <footer className="border-t border-gray-200 py-4 text-center text-xs text-gray-400 dark:border-gray-800">
          Preços coletados automaticamente — podem não refletir valores em tempo real.
        </footer>
      </body>
    </html>
  );
}
