import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/sonner";

const inter = Inter({ subsets: ['latin']})


export const metadata: Metadata = {
  title: 'IA Data Processor - Processamento Inteligente de Dados',
  description: 'Limpe e processe seus dados CSV automaticamente usando Inteligência Artificial',
  keywords: 'CSV, IA, processamento de dados, limpeza de dados, inteligência artificial',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${inter.className} antialiased`}
      >
        {children}
        <Toaster richColors />
      </body>
    </html>
  );
}
