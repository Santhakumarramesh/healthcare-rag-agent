"use client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "react-hot-toast";
import { useState } from "react";

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: { retry: 1, staleTime: 30_000 },
    },
  }));

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            fontFamily: "Inter, sans-serif",
            fontSize: "14px",
            borderRadius: "12px",
          },
          success: {
            iconTheme: { primary: "#00504a", secondary: "#8ef4e9" },
          },
          error: {
            iconTheme: { primary: "#ba1a1a", secondary: "#ffdad6" },
          },
        }}
      />
    </QueryClientProvider>
  );
}
