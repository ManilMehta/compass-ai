import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Compass AI — UC Davis Professor Guide",
  description: "Find the best professors at UC Davis",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}