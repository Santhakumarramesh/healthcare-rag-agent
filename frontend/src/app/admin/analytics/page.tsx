"use client";
import { useQuery } from "@tanstack/react-query";
import { adminApi } from "@/lib/api";

type Metric = { label: string; value: string | number; delta?: string; icon: string; color: string };

function MetricCard({ label, value, delta, icon, color }: Metric) {
  const colorMap: Record<string, string> = {
    primary:   "bg-primary-fixed/20 text-primary",
    secondary: "bg-secondary-fixed/30 text-on-secondary-container",
    tertiary:  "bg-tertiary-fixed/20 text-on-tertiary-container",
    error:     "bg-error-container text-on-error-container",
  };
  return (
    <div className="card">
      <div className={`w-10 h-10 rounded-xl flex items-center justify-center mb-3 ${colorMap[color]}`}>
        <span className="material-symbols-outlined ms-fill">{icon}</span>
      </div>
      <div className="text-3xl font-extrabold text-on-surface font-headline">{value}</div>
      <div className="text-xs text-on-surface-variant mt-0.5">{label}</div>
      {delta && (
        <div className="flex items-center gap-1 mt-2">
          <span className={`material-symbols-outlined text-xs ${delta.startsWith("+") ? "text-on-tertiary-container" : "text-error"}`}>
            {delta.startsWith("+") ? "trending_up" : "trending_down"}
          </span>
          <span className={`text-xs font-medium ${delta.startsWith("+") ? "text-on-tertiary-container" : "text-error"}`}>
            {delta} vs last week
          </span>
        </div>
      )}
    </div>
  );
}

export default function AdminAnalyticsPage() {
  const { data } = useQuery({
    queryKey: ["admin-dashboard"],
    queryFn: () => adminApi.getDashboard().then((r) => r.data),
    retry: false,
  });

  const metrics: Metric[] = [
    { label: "Total Users",          value: data?.total_users ?? "—",          delta: "+12",  icon: "group",         color: "primary"   },
    { label: "Active Patients",      value: data?.active_patients ?? "—",      delta: "+8",   icon: "personal_injury", color: "secondary" },
    { label: "Verified Doctors",     value: data?.verified_doctors ?? "—",     delta: "+3",   icon: "stethoscope",   color: "tertiary"  },
    { label: "Reports Analyzed",     value: data?.reports_analyzed ?? "—",     delta: "+47",  icon: "description",   color: "primary"   },
    { label: "AI Queries (7d)",      value: data?.ai_queries_7d ?? "—",        delta: "+120", icon: "smart_toy",     color: "secondary" },
    { label: "Consultations (7d)",   value: data?.consultations_7d ?? "—",     delta: "+6",   icon: "video_call",    color: "tertiary"  },
    { label: "Avg Response Time",    value: data?.avg_response_ms ? `${data.avg_response_ms}ms` : "—", icon: "speed", color: "primary"   },
    { label: "Error Rate",           value: data?.error_rate ? `${data.error_rate}%` : "—",  delta: "-0.2", icon: "bug_report", color: "error"   },
  ];

  return (
    <div className="max-w-6xl mx-auto px-6 py-8 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-extrabold text-primary font-headline tracking-tight">
          Analytics
        </h1>
        <p className="text-on-surface-variant text-sm mt-1">
          Platform usage metrics and performance KPIs
        </p>
      </div>

      {/* Metrics grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {metrics.map((m) => <MetricCard key={m.label} {...m} />)}
      </div>

      {/* Usage breakdown */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Role distribution */}
        <div className="card space-y-4">
          <h2 className="font-bold text-primary font-headline">User Roles</h2>
          {[
            { role: "Patients",   count: data?.patients_count ?? 0,   icon: "person",              pct: 70 },
            { role: "Doctors",    count: data?.doctors_count ?? 0,    icon: "stethoscope",         pct: 15 },
            { role: "Caregivers", count: data?.caregivers_count ?? 0, icon: "supervisor_account",  pct: 12 },
            { role: "Admins",     count: data?.admins_count ?? 0,     icon: "admin_panel_settings", pct: 3  },
          ].map(({ role, count, icon, pct }) => (
            <div key={role} className="space-y-1">
              <div className="flex justify-between items-center text-sm">
                <div className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-base text-on-surface-variant ms-fill">{icon}</span>
                  <span className="font-medium text-on-surface">{role}</span>
                </div>
                <span className="text-on-surface-variant">{count}</span>
              </div>
              <div className="w-full bg-surface-container rounded-full h-1.5">
                <div
                  className="h-1.5 rounded-full bg-primary transition-all duration-500"
                  style={{ width: `${pct}%` }}
                />
              </div>
            </div>
          ))}
        </div>

        {/* Platform health */}
        <div className="card space-y-4">
          <h2 className="font-bold text-primary font-headline">Platform Health</h2>
          {[
            { label: "API Uptime",       value: "99.9%",  ok: true  },
            { label: "RAG Pipeline",     value: "Online", ok: true  },
            { label: "Vector DB",        value: "Online", ok: true  },
            { label: "Auth Service",     value: "Online", ok: true  },
            { label: "Email Service",    value: "Degraded", ok: false },
            { label: "Payments",         value: "Not configured", ok: false },
          ].map(({ label, value, ok }) => (
            <div key={label} className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${ok ? "bg-on-tertiary-container" : "bg-error"}`} />
                <span className="text-sm text-on-surface">{label}</span>
              </div>
              <span className={`text-xs font-medium ${ok ? "text-on-tertiary-container" : "text-error"}`}>
                {value}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
