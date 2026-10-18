import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Ragaa — Music Player",
  description: "Ragaa — Stream, Discover and Enjoy Full-Length Kannada Music with Lossless Audio",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-black antialiased">{children}</body>
    </html>
  );
}
