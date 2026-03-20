import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "@/components/Providers";

export const metadata: Metadata = {
  title: "CareCopilot AI — Your Health Command Center",
  description: "AI-powered healthcare copilot for reports, insights, consultations, and care management.",
  keywords: ["healthcare", "AI", "medical records", "telemedicine", "CareCopilot"],
  openGraph: {
    title: "CareCopilot AI",
    description: "AI-powered healthcare platform",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
