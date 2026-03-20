"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { isAuthenticated, getUser, getRedirectPath } from "@/lib/auth";

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    if (isAuthenticated()) {
      const user = getUser();
      if (user) {
        router.push(getRedirectPath(user.role));
        return;
      }
    }
    router.push("/auth/login");
  }, [router]);

  return (
    <div className="min-h-screen bg-mesh flex items-center justify-center">
      <div className="flex flex-col items-center gap-4">
        <div className="w-14 h-14 rounded-2xl bg-primary-container flex items-center justify-center">
          <span className="material-symbols-outlined text-3xl text-on-primary ms-fill">
            clinical_notes
          </span>
        </div>
        <h1 className="text-2xl font-extrabold text-primary font-headline tracking-tight">
          CareCopilot AI
        </h1>
        <div className="flex gap-1.5">
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              className="w-2 h-2 rounded-full bg-primary animate-bounce"
              style={{ animationDelay: `${i * 0.15}s` }}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
