"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

interface MobileNavItem {
  label: string;
  href: string;
  icon: string;
}

export function MobileNav({ items }: { items: MobileNavItem[] }) {
  const pathname = usePathname();

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-surface-container-lowest/90 backdrop-blur-md border-t border-outline-variant/20 pb-safe z-30 lg:hidden">
      <div className="flex items-center justify-around px-2 py-2">
        {items.map((item) => {
          const active = pathname === item.href || pathname.startsWith(item.href + "/");
          return (
            <Link key={item.href} href={item.href}>
              <div className="flex flex-col items-center gap-0.5 px-3 py-1.5 rounded-xl transition-all">
                <span className={cn(
                  "material-symbols-outlined text-2xl transition-all",
                  active ? "text-primary ms-fill scale-110" : "text-on-surface-variant"
                )}>
                  {item.icon}
                </span>
                <span className={cn(
                  "text-[10px] font-semibold",
                  active ? "text-primary" : "text-on-surface-variant"
                )}>
                  {item.label}
                </span>
              </div>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
