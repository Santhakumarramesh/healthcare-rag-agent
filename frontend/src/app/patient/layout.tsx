import { Sidebar } from "@/components/layout/Sidebar";
import { MobileNav } from "@/components/layout/MobileNav";

const NAV = [
  { label: "Dashboard",     href: "/patient/dashboard",      icon: "home" },
  { label: "AI Chat",       href: "/patient/ai-chat",         icon: "chat_bubble" },
  { label: "Records",       href: "/patient/records",         icon: "folder_shared" },
  { label: "Tracking",      href: "/patient/tracking",        icon: "monitoring" },
  { label: "Prescriptions", href: "/patient/prescriptions",   icon: "medication" },
  { label: "Consultations", href: "/patient/consultations",   icon: "video_call" },
  { label: "Insurance",     href: "/patient/insurance",       icon: "health_and_safety" },
  { label: "Marketplace",   href: "/patient/marketplace",     icon: "store" },
  { label: "Settings",      href: "/patient/settings",        icon: "settings" },
];

const MOBILE_NAV = [
  { label: "Home",    href: "/patient/dashboard",    icon: "home" },
  { label: "AI",      href: "/patient/ai-chat",      icon: "chat_bubble" },
  { label: "Records", href: "/patient/records",       icon: "folder_shared" },
  { label: "Track",   href: "/patient/tracking",      icon: "monitoring" },
  { label: "Rx",      href: "/patient/prescriptions", icon: "medication" },
];

export default function PatientLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen bg-surface">
      <Sidebar navItems={NAV} portalLabel="Patient Portal" portalIcon="person" />
      <div className="flex-1 lg:ml-64 flex flex-col min-h-screen">
        <main className="flex-1 pb-24 lg:pb-8">
          {children}
        </main>
      </div>
      <MobileNav items={MOBILE_NAV} />
    </div>
  );
}
