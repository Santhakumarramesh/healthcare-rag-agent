"use client";
import { useAuthStore } from "@/lib/store";
import { clearTokens, clearUser } from "@/lib/auth";
import { useRouter } from "next/navigation";
import toast from "react-hot-toast";
import { authApi } from "@/lib/api";

const SECTIONS = [
  {
    title: "Account",
    items: [
      { icon: "person", label: "Edit Profile", href: "/patient/profile" },
      { icon: "lock", label: "Change Password", href: "/patient/settings/password" },
      { icon: "notifications", label: "Notification Preferences", href: "/patient/settings/notifications" },
    ],
  },
  {
    title: "Health",
    items: [
      { icon: "health_and_safety", label: "Insurance", href: "/patient/insurance" },
      { icon: "medical_information", label: "Medical Profile", href: "/patient/profile/health" },
      { icon: "family_restroom", label: "Caregivers & Access", href: "/patient/settings/caregivers" },
    ],
  },
  {
    title: "Privacy & Security",
    items: [
      { icon: "privacy_tip", label: "Privacy Center", href: "/patient/settings/privacy" },
      { icon: "shield", label: "Data & Permissions", href: "/patient/settings/data" },
      { icon: "download", label: "Download My Data", href: "/patient/settings/export" },
    ],
  },
];

export default function SettingsPage() {
  const router = useRouter();
  const user = useAuthStore((s) => s.user);
  const clearAuth = useAuthStore((s) => s.clearAuth);

  const handleLogout = async () => {
    try { await authApi.logout(); } catch {}
    clearTokens();
    clearUser();
    clearAuth();
    toast.success("Signed out");
    router.push("/auth/login");
  };

  return (
    <div className="max-w-2xl mx-auto px-5 py-8 space-y-6">
      <h1 className="text-2xl font-extrabold text-primary font-headline">Settings</h1>

      {/* Profile card */}
      {user && (
        <div className="card flex items-center gap-4">
          <div className="w-14 h-14 rounded-full bg-primary-fixed flex items-center justify-center text-primary font-extrabold text-lg">
            {user.full_name.split(" ").map((n) => n[0]).join("").toUpperCase().slice(0, 2)}
          </div>
          <div>
            <p className="font-bold text-on-surface">{user.full_name}</p>
            <p className="text-sm text-on-surface-variant">{user.email}</p>
            <div className="flex items-center gap-1.5 mt-1">
              <span className="material-symbols-outlined text-xs text-on-tertiary-container ms-fill">verified</span>
              <span className="text-xs text-on-tertiary-container font-medium capitalize">{user.role}</span>
            </div>
          </div>
        </div>
      )}

      {/* Settings sections */}
      {SECTIONS.map((section) => (
        <section key={section.title} className="space-y-1">
          <p className="text-xs font-semibold text-on-surface-variant uppercase tracking-wider px-1">
            {section.title}
          </p>
          <div className="card p-0 overflow-hidden">
            {section.items.map((item, idx) => (
              <a key={item.href} href={item.href}>
                <div className={`flex items-center gap-3 px-4 py-4 hover:bg-surface-container transition-colors cursor-pointer ${
                  idx < section.items.length - 1 ? "border-b border-outline-variant/10" : ""
                }`}>
                  <span className="material-symbols-outlined text-on-surface-variant text-xl">{item.icon}</span>
                  <span className="flex-1 text-sm font-medium text-on-surface">{item.label}</span>
                  <span className="material-symbols-outlined text-on-surface-variant text-sm">chevron_right</span>
                </div>
              </a>
            ))}
          </div>
        </section>
      ))}

      {/* Logout */}
      <div className="card p-0 overflow-hidden">
        <button onClick={handleLogout}
          className="w-full flex items-center gap-3 px-4 py-4 text-error hover:bg-error-container/20 transition-colors">
          <span className="material-symbols-outlined text-xl">logout</span>
          <span className="text-sm font-medium">Sign Out</span>
        </button>
      </div>

      <div className="text-center text-xs text-on-surface-variant">
        CareCopilot AI v2.0.0 · HIPAA-aligned
      </div>
    </div>
  );
}
