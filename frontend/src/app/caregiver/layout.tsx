import { Sidebar } from "@/components/layout/Sidebar";
import { MobileNav } from "@/components/layout/MobileNav";

const NAV = [
  { label: "Dashboard",  href: "/caregiver/dashboard", icon: "home" },
  { label: "My Patients", href: "/caregiver/patients", icon: "supervisor_account" },
  { label: "Messages",   href: "/caregiver/messages",  icon: "chat" },
  { label: "Settings",   href: "/caregiver/settings",  icon: "settings" },
];

const MOBILE_NAV = [
  { label: "Home",     href: "/caregiver/dashboard", icon: "home" },
  { label: "Patients", href: "/caregiver/patients",  icon: "supervisor_account" },
  { label: "Messages", href: "/caregiver/messages",  icon: "chat" },
];

export default function CaregiverLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen bg-surface">
      <Sidebar navItems={NAV} portalLabel="Caregiver Portal" portalIcon="supervisor_account" />
      <div className="flex-1 lg:ml-64 min-h-screen pb-24 lg:pb-0">
        {children}
      </div>
      <MobileNav items={MOBILE_NAV} />
    </div>
  );
}
