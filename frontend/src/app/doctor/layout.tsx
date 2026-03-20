import { Sidebar } from "@/components/layout/Sidebar";
import { MobileNav } from "@/components/layout/MobileNav";

const NAV = [
  { label: "Dashboard",     href: "/doctor/dashboard",     icon: "dashboard" },
  { label: "Patients",      href: "/doctor/patients",       icon: "group" },
  { label: "Consultations", href: "/doctor/consultations",  icon: "video_call" },
  { label: "Prescriptions", href: "/doctor/prescriptions",  icon: "medication" },
  { label: "Availability",  href: "/doctor/availability",   icon: "calendar_month" },
  { label: "Messages",      href: "/doctor/messages",       icon: "chat" },
  { label: "Settings",      href: "/doctor/settings",       icon: "settings" },
];

const MOBILE_NAV = [
  { label: "Home",     href: "/doctor/dashboard",    icon: "dashboard" },
  { label: "Patients", href: "/doctor/patients",      icon: "group" },
  { label: "Consult",  href: "/doctor/consultations", icon: "video_call" },
  { label: "Rx",       href: "/doctor/prescriptions", icon: "medication" },
  { label: "Schedule", href: "/doctor/availability",  icon: "calendar_month" },
];

export default function DoctorLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen bg-surface">
      <Sidebar navItems={NAV} portalLabel="Clinical Portal" portalIcon="stethoscope" />
      <div className="flex-1 lg:ml-64 min-h-screen pb-24 lg:pb-0">
        {children}
      </div>
      <MobileNav items={MOBILE_NAV} />
    </div>
  );
}
