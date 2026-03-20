"use client";
import { useUIStore } from "@/lib/store";
import { useAuthStore } from "@/lib/store";
import Link from "next/link";

interface TopBarProps {
  title?: string;
}

export function TopBar({ title }: TopBarProps) {
  const toggleSidebar = useUIStore((s) => s.toggleSidebar);
  const user = useAuthStore((s) => s.user);

  return (
    <header className="h-16 bg-surface-container-lowest/80 backdrop-blur-md border-b border-outline-variant/20 flex items-center justify-between px-6 sticky top-0 z-30">
      <div className="flex items-center gap-4">
        <button
          onClick={toggleSidebar}
          className="w-9 h-9 flex items-center justify-center rounded-lg hover:bg-surface-container transition-colors"
        >
          <span className="material-symbols-outlined text-on-surface-variant">menu</span>
        </button>
        {title && (
          <h2 className="text-base font-semibold text-on-surface font-headline hidden sm:block">{title}</h2>
        )}
      </div>

      <div className="flex items-center gap-2">
        <Link href="#notifications">
          <button className="w-9 h-9 flex items-center justify-center rounded-lg hover:bg-surface-container transition-colors relative">
            <span className="material-symbols-outlined text-on-surface-variant">notifications</span>
            <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-error rounded-full" />
          </button>
        </Link>
        <div className="w-8 h-8 rounded-full bg-primary-fixed flex items-center justify-center text-primary font-bold text-xs">
          {user?.full_name.split(" ").map((n) => n[0]).join("").toUpperCase().slice(0, 2) ?? "??"}
        </div>
      </div>
    </header>
  );
}
