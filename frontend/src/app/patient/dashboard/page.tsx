"use client";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { patientApi } from "@/lib/api";
import { useAuthStore } from "@/lib/store";
import { formatRelative, formatDate } from "@/lib/utils";

// ── Quick action card ─────────────────────────────────────────────────────────
function QuickAction({
  href, icon, label, color = "primary", light = false,
}: {
  href: string; icon: string; label: string; color?: string; light?: boolean;
}) {
  const base = light
    ? "bg-surface-container-lowest border border-outline-variant/20 hover:shadow-card-md"
    : color === "primary"
    ? "bg-primary text-white hover:shadow-card-md"
    : "bg-secondary-container text-white hover:shadow-card-md";

  return (
    <Link href={href}>
      <div className={`flex flex-col items-start p-4 rounded-2xl transition-all active:scale-95 gap-3 cursor-pointer ${base}`}>
        <span className={`material-symbols-outlined text-3xl ${light ? "text-primary" : ""}`}>{icon}</span>
        <span className={`font-bold text-sm tracking-tight ${light ? "text-on-surface" : ""}`}>{label}</span>
      </div>
    </Link>
  );
}

// ── Risk Alert ────────────────────────────────────────────────────────────────
function RiskAlert({ message }: { message: string }) {
  return (
    <div className="bg-error-container rounded-2xl p-4 flex gap-4 items-start shadow-sm border border-error/5">
      <div className="bg-on-error-container text-white p-2 rounded-xl shrink-0">
        <span className="material-symbols-outlined">warning</span>
      </div>
      <div>
        <h3 className="font-bold text-on-error-container text-sm uppercase tracking-wider">
          Urgent Attention Required
        </h3>
        <p className="text-on-error-container text-sm leading-snug mt-0.5">{message}</p>
      </div>
    </div>
  );
}

export default function PatientDashboard() {
  const user = useAuthStore((s) => s.user);

  const { data: dashboard } = useQuery({
    queryKey: ["patient-dashboard"],
    queryFn: () => patientApi.getDashboard().then((r) => r.data),
    retry: false,
  });

  const firstName = user?.full_name?.split(" ")[0] ?? "there";
  const hour = new Date().getHours();
  const greeting = hour < 12 ? "Good morning" : hour < 17 ? "Good afternoon" : "Good evening";

  return (
    <div className="bg-surface text-on-surface min-h-screen pb-32">
      {/* Top App Bar */}
      <header className="fixed top-0 left-0 right-0 lg:left-64 z-30 flex justify-between items-center px-6 py-4 bg-surface/80 backdrop-blur-md shadow-sm">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-primary-fixed flex items-center justify-center text-primary font-bold text-sm">
            {user?.full_name?.split(" ").map((n) => n[0]).join("").toUpperCase().slice(0, 2) ?? "CC"}
          </div>
          <span className="text-xl font-extrabold text-primary font-headline tracking-tight">CareCopilot AI</span>
        </div>
        <Link href="/patient/notifications">
          <button className="w-10 h-10 flex items-center justify-center rounded-full hover:bg-surface-container transition-colors relative">
            <span className="material-symbols-outlined text-primary">notifications</span>
            <span className="absolute top-2 right-2 w-2 h-2 bg-error rounded-full" />
          </button>
        </Link>
      </header>

      <main className="pt-24 px-5 max-w-md mx-auto lg:max-w-2xl space-y-8">

        {/* Hero */}
        <section className="space-y-3">
          <h1 className="text-3xl font-extrabold text-primary font-headline leading-tight tracking-tight">
            {greeting}, {firstName} 👋
          </h1>
          <p className="text-on-surface-variant text-sm">
            {dashboard?.summary || "AI Healthcare Copilot for reports, questions, and follow-up care"}
          </p>
          <div className="flex items-center gap-2 px-3 py-1.5 bg-tertiary-container/10 border border-on-tertiary-container/20 rounded-full w-fit">
            <span className="material-symbols-outlined text-on-tertiary-container text-sm ms-fill">verified_user</span>
            <span className="text-xs font-semibold text-on-tertiary-container tracking-wide uppercase">
              Verified Secure &amp; Privacy-First
            </span>
          </div>
        </section>

        {/* Risk Alerts */}
        {dashboard?.alerts?.filter((a: { severity: string }) => a.severity === "high").map((a: { id: string; message: string }) => (
          <RiskAlert key={a.id} message={a.message} />
        ))}

        {/* Quick Actions */}
        <section>
          <h2 className="text-lg font-bold text-primary font-headline mb-3">Quick Actions</h2>
          <div className="grid grid-cols-2 gap-3">
            <QuickAction href="/patient/records?action=upload" icon="description" label="Analyze Report" />
            <QuickAction href="/patient/ai-chat" icon="chat_bubble" label="Ask AI" color="secondary" />
            <QuickAction href="/patient/consultations" icon="event_repeat" label="Start Follow-up" light />
            <QuickAction href="/patient/records" icon="folder_shared" label="View Records" light />
          </div>
        </section>

        {/* Care Score */}
        {dashboard?.care_score != null && (
          <section className="card">
            <div className="flex items-center justify-between mb-3">
              <h2 className="font-bold text-primary font-headline">Care Score</h2>
              <span className="badge badge-success">{dashboard.care_score}/100</span>
            </div>
            <div className="w-full bg-surface-container rounded-full h-3">
              <div
                className="h-3 rounded-full bg-gradient-to-r from-primary to-secondary-container transition-all duration-500"
                style={{ width: `${dashboard.care_score}%` }}
              />
            </div>
            {dashboard.care_score_breakdown && (
              <div className="grid grid-cols-3 gap-2 mt-3">
                {Object.entries(dashboard.care_score_breakdown).map(([k, v]) => (
                  <div key={k} className="text-center">
                    <div className="text-lg font-bold text-on-surface">{v as number}</div>
                    <div className="text-xs text-on-surface-variant capitalize">{k.replace("_", " ")}</div>
                  </div>
                ))}
              </div>
            )}
          </section>
        )}

        {/* AI Insights */}
        {dashboard?.insights?.length > 0 && (
          <section className="space-y-3">
            <div className="flex justify-between items-center">
              <h2 className="text-lg font-bold text-primary font-headline">AI Insights</h2>
              <Link href="/patient/ai-chat" className="text-xs font-semibold text-secondary uppercase tracking-widest">
                Chat with AI
              </Link>
            </div>
            {dashboard.insights.slice(0, 2).map((insight: {
              id: string;
              title: string;
              what_changed: string;
              why_it_matters: string;
              what_to_do: string;
              severity: string;
            }) => (
              <div key={insight.id} className="card border-l-4 border-secondary">
                <h3 className="font-bold text-on-surface text-sm mb-1">{insight.title}</h3>
                <p className="text-xs text-on-surface-variant">{insight.what_changed}</p>
                <p className="text-xs text-on-surface-variant mt-1">{insight.why_it_matters}</p>
                {insight.what_to_do && (
                  <div className="mt-2 flex items-start gap-2">
                    <span className="material-symbols-outlined text-secondary text-sm ms-fill">tips_and_updates</span>
                    <p className="text-xs font-medium text-on-surface">{insight.what_to_do}</p>
                  </div>
                )}
              </div>
            ))}
          </section>
        )}

        {/* Recent Activity */}
        <section className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-lg font-bold text-primary font-headline">Recent Activity</h2>
            <Link href="/patient/records" className="text-xs font-semibold text-secondary uppercase tracking-widest">
              See All
            </Link>
          </div>

          {dashboard?.recent_reports?.length > 0 ? (
            <div className="space-y-3">
              {dashboard.recent_reports.slice(0, 4).map((report: {
                id: string;
                report_type: string;
                file_name: string;
                status: string;
                created_at: string;
              }) => (
                <Link key={report.id} href={`/patient/records/${report.id}`}>
                  <div className="card flex items-center justify-between cursor-pointer hover:shadow-card-md transition-shadow">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-xl bg-primary-fixed/30 flex items-center justify-center">
                        <span className="material-symbols-outlined text-primary text-sm">description</span>
                      </div>
                      <div>
                        <p className="font-semibold text-sm text-on-surface">{report.report_type || report.file_name}</p>
                        <p className="text-xs text-on-surface-variant">{formatRelative(report.created_at)}</p>
                      </div>
                    </div>
                    <span className={`badge ${report.status === "analyzed" ? "badge-success" : report.status === "processing" ? "badge-info" : "badge-gray"}`}>
                      {report.status}
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            <div className="card text-center py-8">
              <span className="material-symbols-outlined text-4xl text-on-surface-variant">folder_open</span>
              <p className="text-sm text-on-surface-variant mt-2 font-medium">No reports yet</p>
              <Link href="/patient/records?action=upload">
                <button className="btn-primary mt-4 text-sm">Upload your first report</button>
              </Link>
            </div>
          )}
        </section>

        {/* Today's Tracking Summary */}
        {dashboard?.today_summary && (
          <section className="space-y-3">
            <h2 className="text-lg font-bold text-primary font-headline">Today&apos;s Tracking</h2>
            <div className="grid grid-cols-2 gap-3">
              {[
                { key: "hydration", label: "Hydration", icon: "water_drop", unit: "ml" },
                { key: "steps", label: "Steps", icon: "directions_walk", unit: "" },
                { key: "sleep", label: "Sleep", icon: "bedtime", unit: "hrs" },
                { key: "mood", label: "Mood", icon: "mood", unit: "/5" },
              ].map(({ key, label, icon, unit }) =>
                dashboard.today_summary[key] != null ? (
                  <div key={key} className="card flex items-center gap-3">
                    <span className="material-symbols-outlined text-secondary text-2xl">{icon}</span>
                    <div>
                      <div className="text-lg font-bold text-on-surface">
                        {dashboard.today_summary[key]}{unit}
                      </div>
                      <div className="text-xs text-on-surface-variant">{label}</div>
                    </div>
                  </div>
                ) : null
              )}
            </div>
          </section>
        )}

        {/* Upcoming */}
        {dashboard?.upcoming_consultations?.length > 0 && (
          <section className="space-y-3">
            <div className="flex justify-between items-center">
              <h2 className="text-lg font-bold text-primary font-headline">Upcoming</h2>
              <Link href="/patient/consultations" className="text-xs font-semibold text-secondary uppercase tracking-widest">
                All
              </Link>
            </div>
            {dashboard.upcoming_consultations.slice(0, 2).map((c: {
              id: string;
              scheduled_at: string;
              doctor_name: string;
              consultation_type: string;
            }) => (
              <div key={c.id} className="card flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-secondary-fixed flex items-center justify-center shrink-0">
                  <span className="material-symbols-outlined text-on-secondary-container">video_call</span>
                </div>
                <div className="flex-1">
                  <p className="font-semibold text-on-surface text-sm">{c.doctor_name || "Consultation"}</p>
                  <p className="text-xs text-on-surface-variant">{formatDate(c.scheduled_at, "full")}</p>
                </div>
                <span className="badge badge-info">{c.consultation_type}</span>
              </div>
            ))}
          </section>
        )}
      </main>
    </div>
  );
}
