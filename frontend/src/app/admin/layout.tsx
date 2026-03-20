import { Sidebar } from "@/components/layout/Sidebar";

const NAV = [
  { label: "Dashboard",     href: "/admin/dashboard",  icon: "dashboard" },
  { label: "Users",         href: "/admin/users",       icon: "manage_accounts" },
  { label: "Doctor Approval", href: "/admin/doctors",  icon: "verified_user" },
  { label: "Analytics",     href: "/admin/analytics",   icon: "analytics" },
  { label: "Support",       href: "/admin/support",     icon: "support_agent" },
  { label: "Audit Log",     href: "/admin/audit",       icon: "history" },
  { label: "Settings",      href: "/admin/settings",    icon: "settings" },
];

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen bg-surface">
      <Sidebar navItems={NAV} portalLabel="Admin Portal" portalIcon="admin_panel_settings" />
      <div className="flex-1 lg:ml-64 min-h-screen">
        {children}
      </div>
    </div>
  );
}
