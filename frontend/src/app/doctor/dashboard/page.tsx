"use client";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { doctorsApi, consultationsApi } from "@/lib/api";
import { useAuthStore } from "@/lib/store";
import { formatDate, formatRelative } from "@/lib/utils";

function StatCard({ icon, label, value, color = "primary" }: {
  icon: string; label: string; value: string | number; color?: string;
}) {
  const colors: Record<string, string> = {
    primary: "bg-primary-fixed/20 text-primary",
    secondary: "bg-secondary-fixed/30 text-on-secondary-container",
    tertiary: "bg-tertiary-fixed/20 text-on-tertiary-container",
    error: "bg-error-container text-on-error-container",
  };
  return (
    <div className="card">
      <div className={`w-10 h-10 rounded-xl flex items-center justify-center mb-3 ${colors[color]}`}>
        <span className="material-symbols-outlined ms-fill">{icon}</span>
      </div>
      <div className="text-2xl font-extrabold text-on-surface font-headline">{value}</div>
      <div className="text-xs text-on-surface-variant mt-0.5">{label}</div>
    </div>
  );
}

export default function DoctorDashboard() {
  const user = useAuthStore((s) => s.user);

  const { data: queue } = useQuery({
    queryKey: ["doctor-queue"],
    queryFn: () => doctorsApi.getPatientQueue().then((r) => r.data),
    retry: false,
  });

  const { data: upcoming } = useQuery({
    queryKey: ["doctor-consultations"],
    queryFn: () => consultationsApi.list({ status: "scheduled", limit: 5 }).then((r) => r.data),
    retry: false,
  });

  const firstName = user?.full_name?.split(" ")[0] ?? "Doctor";

  return (
    <div className="max-w-5xl mx-auto px-6 py-8 space-y-8">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-primary font-headline tracking-tight">
            Good morning, Dr. {firstName}
          </h1>
          <p className="text-on-surface-variant text-sm mt-1">
            {new Date().toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric" })}
          </p>
        </div>
        <Link href="/doctor/consultations/new">
          <button className="btn-primary flex items-center gap-2 shrink-0">
            <span className="material-symbols-outlined text-sm">add</span>
            New Consultation
          </button>
        </Link>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon="group" label="Active Patients" value={queue?.total_patients ?? 0} />
        <StatCard icon="video_call" label="Today's Consults" value={upcoming?.total ?? 0} color="secondary" />
        <StatCard icon="medication" label="Pending Refills" value={queue?.pending_refills ?? 0} color="tertiary" />
        <StatCard icon="warning" label="Risk Alerts" value={queue?.high_risk_count ?? 0} color="error" />
      </div>

      {/* Two column layout */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Patient Queue */}
        <section className="space-y-3">
          <div className="flex justify-between items-center">
            <h2 className="text-lg font-bold text-primary font-headline">Patient Queue</h2>
            <Link href="/doctor/patients" className="text-xs font-semibold text-secondary uppercase tracking-widest">
              See All
            </Link>
          </div>

          {!queue?.queue_items?.length ? (
            <div className="card text-center py-8">
              <span className="material-symbols-outlined text-4xl text-on-surface-variant">group</span>
              <p className="text-sm font-medium text-on-surface-variant mt-2">Queue is empty</p>
            </div>
          ) : (
            <div className="space-y-2">
              {queue.queue_items.slice(0, 6).map((item: {
                patient_id: string;
                patient_name: string;
                reason: string;
                priority: string;
                wait_time?: string;
              }) => (
                <Link key={item.patient_id} href={`/doctor/patients/${item.patient_id}`}>
                  <div className="card flex items-center gap-3 cursor-pointer hover:shadow-card-md transition-shadow">
                    <div className="w-10 h-10 rounded-full bg-primary-fixed flex items-center justify-center text-primary font-bold text-sm shrink-0">
                      {item.patient_name.split(" ").map((n: string) => n[0]).join("").toUpperCase().slice(0, 2)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-semibold text-on-surface text-sm truncate">{item.patient_name}</p>
                      <p className="text-xs text-on-surface-variant truncate">{item.reason}</p>
                    </div>
                    <span className={`badge shrink-0 ${
                      item.priority === "high" ? "badge-error" :
                      item.priority === "medium" ? "badge-warning" : "badge-gray"
                    }`}>
                      {item.priority}
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </section>

        {/* Upcoming Consultations */}
        <section className="space-y-3">
          <div className="flex justify-between items-center">
            <h2 className="text-lg font-bold text-primary font-headline">Upcoming</h2>
            <Link href="/doctor/consultations" className="text-xs font-semibold text-secondary uppercase tracking-widest">
              All
            </Link>
          </div>

          {!upcoming?.consultations?.length ? (
            <div className="card text-center py-8">
              <span className="material-symbols-outlined text-4xl text-on-surface-variant">calendar_today</span>
              <p className="text-sm font-medium text-on-surface-variant mt-2">No upcoming consultations</p>
            </div>
          ) : (
            <div className="space-y-2">
              {upcoming.consultations.slice(0, 5).map((c: {
                id: string;
                patient_name: string;
                scheduled_at: string;
                consultation_type: string;
                status: string;
              }) => (
                <Link key={c.id} href={`/doctor/consultations/${c.id}`}>
                  <div className="card flex items-center gap-3 cursor-pointer hover:shadow-card-md transition-shadow">
                    <div className="w-10 h-10 rounded-xl bg-secondary-fixed/30 flex items-center justify-center shrink-0">
                      <span className="material-symbols-outlined text-on-secondary-container">video_call</span>
                    </div>
                    <div className="flex-1">
                      <p className="font-semibold text-on-surface text-sm">{c.patient_name}</p>
                      <p className="text-xs text-on-surface-variant">{formatDate(c.scheduled_at, "full")}</p>
                    </div>
                    <span className="badge badge-info">{c.consultation_type}</span>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </section>
      </div>

      {/* Risk Queue */}
      {queue?.risk_patients?.length > 0 && (
        <section className="space-y-3">
          <div className="flex justify-between items-center">
            <h2 className="text-lg font-bold text-primary font-headline flex items-center gap-2">
              <span className="material-symbols-outlined text-error">warning</span>
              Risk Queue
            </h2>
          </div>
          <div className="bg-error-container rounded-2xl p-4 space-y-3">
            {queue.risk_patients.map((p: {
              patient_id: string;
              patient_name: string;
              risk_level: string;
              risk_reason: string;
              last_activity: string;
            }) => (
              <Link key={p.patient_id} href={`/doctor/patients/${p.patient_id}`}>
                <div className="bg-white/50 rounded-xl p-3 flex items-center gap-3 cursor-pointer">
                  <div className="w-8 h-8 rounded-full bg-on-error-container text-white flex items-center justify-center text-xs font-bold shrink-0">
                    {p.patient_name.split(" ").map((n: string) => n[0]).join("").toUpperCase().slice(0, 2)}
                  </div>
                  <div className="flex-1">
                    <p className="font-semibold text-on-error-container text-sm">{p.patient_name}</p>
                    <p className="text-xs text-on-error-container/80">{p.risk_reason}</p>
                  </div>
                  <span className="text-xs text-on-error-container/60">{formatRelative(p.last_activity)}</span>
                </div>
              </Link>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
