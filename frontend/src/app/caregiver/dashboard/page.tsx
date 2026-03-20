"use client";
import { useAuthStore } from "@/lib/store";
import Link from "next/link";

export default function CaregiverDashboard() {
  const user = useAuthStore((s) => s.user);
  const firstName = user?.full_name?.split(" ")[0] ?? "there";

  return (
    <div className="max-w-2xl mx-auto px-5 py-8 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-extrabold text-primary font-headline">Hello, {firstName} 👋</h1>
        <p className="text-sm text-on-surface-variant mt-1">Caregiver overview — supporting your loved one&apos;s care</p>
      </div>

      {/* Quick Actions */}
      <section>
        <h2 className="font-bold text-on-surface font-headline mb-3">Quick Actions</h2>
        <div className="grid grid-cols-2 gap-3">
          {[
            { href: "/caregiver/patients", icon: "supervisor_account", label: "View Patient", color: "primary" },
            { href: "#", icon: "medication", label: "Medication Check", color: "secondary" },
            { href: "#", icon: "warning", label: "Emergency Alert", color: "error" },
            { href: "/caregiver/messages", icon: "chat", label: "Secure Message", color: "light" },
          ].map((a) => (
            <Link key={a.label} href={a.href}>
              <div className={`flex flex-col items-start p-4 rounded-2xl transition-all active:scale-95 gap-3 cursor-pointer ${
                a.color === "primary" ? "bg-primary text-white" :
                a.color === "secondary" ? "bg-secondary-container text-white" :
                a.color === "error" ? "bg-error-container border border-error/10" :
                "bg-surface-container-lowest border border-outline-variant/20"
              }`}>
                <span className={`material-symbols-outlined text-3xl ${
                  a.color === "error" ? "text-on-error-container" :
                  a.color === "light" ? "text-primary" : ""
                }`}>{a.icon}</span>
                <span className={`font-bold text-sm ${
                  a.color === "error" ? "text-on-error-container" :
                  a.color === "light" ? "text-on-surface" : ""
                }`}>{a.label}</span>
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* Patient overview placeholder */}
      <section className="card space-y-4">
        <h2 className="font-bold text-primary font-headline">Patient Overview</h2>
        <div className="flex flex-col items-center py-6 gap-3">
          <span className="material-symbols-outlined text-5xl text-on-surface-variant">supervisor_account</span>
          <p className="font-medium text-on-surface">No linked patient yet</p>
          <p className="text-sm text-on-surface-variant text-center">
            Your care recipient will appear here once linked by a care coordinator.
          </p>
          <Link href="/caregiver/patients">
            <button className="btn-primary text-sm">View Patients</button>
          </Link>
        </div>
      </section>
    </div>
  );
}
