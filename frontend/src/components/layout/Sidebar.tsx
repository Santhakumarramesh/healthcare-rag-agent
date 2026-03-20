"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import { clearTokens, clearUser } from "@/lib/auth";
import { useAuthStore, useUIStore } from "@/lib/store";
import toast from "react-hot-toast";
import { authApi } from "@/lib/api";

interface NavItem {
  label: string;
  href: string;
  icon: string;
}

interface SidebarProps {
  navItems: NavItem[];
  portalLabel: string;
  portalIcon?: string;
}

export function Sidebar({ navItems, portalLabel, portalIcon = "clinical_notes" }: SidebarProps) {
  const pathname = usePathname();
  const router = useRouter();
  const user = useAuthStore((s) => s.user);
  const clearAuth = useAuthStore((s) => s.clearAuth);
  const sidebarOpen = useUIStore((s) => s.sidebarOpen);

  const handleLogout = async () => {
    try { await authApi.logout(); } catch { /* ignore */ }
    clearTokens();
    clearUser();
    clearAuth();
    toast.success("Signed out");
    router.push("/auth/login");
  };

  return (
    <>
      {/* Overlay for mobile */}
      {sidebarOpen && (
        <div className="fixed inset-0 bg-black/30 z-40 lg:hidden" onClick={useUIStore.getState().toggleSidebar} />
      )}

      <aside className={cn(
        "fixed left-0 top-0 h-screen w-64 flex flex-col bg-surface-container-low z-50 transition-transform duration-300",
        "border-r border-outline-variant/30",
        sidebarOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
      )}>
        {/* Brand */}
        <div className="px-6 py-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-primary-container flex items-center justify-center">
              <span className="material-symbols-outlined text-on-primary ms-fill">{portalIcon}</span>
            </div>
            <div>
              <div className="font-extrabold text-primary tracking-tight text-lg font-headline leading-tight">
                CareCopilot AI
              </div>
              <div className="text-[10px] uppercase tracking-widest text-on-surface-variant font-bold">
                {portalLabel}
              </div>
            </div>
          </div>
        </div>

        {/* Nav items */}
        <nav className="flex-1 px-2 space-y-0.5 overflow-y-auto">
          {navItems.map((item) => {
            const active = pathname === item.href || pathname.startsWith(item.href + "/");
            return (
              <Link key={item.href} href={item.href}>
                <div className={cn(
                  "nav-item",
                  active
                    ? "bg-primary text-white font-semibold shadow-sm"
                    : "text-on-surface-variant hover:text-on-surface"
                )}>
                  <span className={cn("material-symbols-outlined text-xl", active && "ms-fill")}>
                    {item.icon}
                  </span>
                  <span className="text-sm">{item.label}</span>
                </div>
              </Link>
            );
          })}
        </nav>

        {/* User + logout */}
        <div className="p-4 border-t border-outline-variant/30 space-y-2">
          {user && (
            <div className="flex items-center gap-3 px-2 py-2">
              <div className="w-8 h-8 rounded-full bg-primary-fixed flex items-center justify-center text-primary font-bold text-xs shrink-0">
                {user.full_name.split(" ").map((n) => n[0]).join("").toUpperCase().slice(0, 2)}
              </div>
              <div className="overflow-hidden">
                <p className="text-sm font-semibold text-on-surface truncate">{user.full_name}</p>
                <p className="text-xs text-on-surface-variant truncate">{user.email}</p>
              </div>
            </div>
          )}
          <button
            onClick={handleLogout}
            className="nav-item w-full text-error hover:bg-error-container/30"
          >
            <span className="material-symbols-outlined text-xl">logout</span>
            <span className="text-sm">Sign Out</span>
          </button>
        </div>
      </aside>
    </>
  );
}
