"use client";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { adminApi } from "@/lib/api";
import { formatRelative, capitalize } from "@/lib/utils";
import toast from "react-hot-toast";
import Link from "next/link";

function KpiCard({ label, value, icon, delta, color = "primary" }: {
  label: string; value: string | number; icon: string; delta?: string; color?: string;
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
      <div className="text-3xl font-extrabold text-on-surface font-headline">{value}</div>
      <div className="text-xs text-on-surface-variant mt-0.5">{label}</div>
      {delta && (
        <div className="flex items-center gap-1 mt-2">
          <span className={`material-symbols-outlined text-xs ${delta.startsWith("+") ? "text-on-tertiary-container" : "text-error"}`}>
            {delta.startsWith("+") ? "trending_up" : "trending_down"}
          </span>
          <span className={`text-xs font-medium ${delta.startsWith("+") ? "text-on-tertiary-container" : "text-error"}`}>
            {delta} this week
          </span>
        </div>
      )}
    </div>
  );
}

export default function AdminDashboard() {
  const qc = useQueryClient();

  const { data: dashboard, isLoading } = useQuery({
    queryKey: ["admin-dashboard"],
    queryFn: () => adminApi.getDashboard().then((r) => r.data),
    refetchInterval: 30_000,
  });

  const { data: alerts } = useQuery({
    queryKey: ["admin-alerts"],
    queryFn: () => adminApi.getAlerts().then((r) => r.data),
  });

  const { data: jobs } = useQuery({
    queryKey: ["admin-jobs", "failed"],
    queryFn: () => adminApi.getJobs({ status: "failed", limit: 5 }).then((r) => r.data),
  });

  const { data: approvals } = useQuery({
    queryKey: ["admin-approvals"],
    queryFn: () => adminApi.getDoctorApprovals().then((r) => r.data),
  });

  const { mutate: retryJob } = useMutation({
    mutationFn: (id: string) => adminApi.retryJob(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["admin-jobs"] }); toast.success("Job retried"); },
  });

  const { mutate: resolveAlert } = useMutation({
    mutationFn: (id: string) => adminApi.resolveAlert(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["admin-alerts"] }); toast.success("Alert resolved"); },
  });

  const { mutate: approveDoctor } = useMutation({
    mutationFn: (id: string) => adminApi.approveDoctor(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["admin-approvals"] }); toast.success("Doctor approved!"); },
  });

  if (isLoading) {
    return (
      <div className="max-w-6xl mx-auto px-6 py-8 space-y-6">
        <div className="h-8 bg-surface-container animate-pulse rounded-xl w-64" />
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => <div key={i} className="card h-32 animate-pulse" />)}
        </div>
      </div>
    );
  }

  const activeAlerts = alerts?.alerts?.filter((a: { status: string }) => a.status === "active") ?? [];
  const failedJobs = jobs?.jobs ?? [];
  const pendingApprovals = approvals?.approvals ?? [];

  return (
    <div className="max-w-6xl mx-auto px-6 py-8 space-y-8">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-extrabold text-primary font-headline tracking-tight">Admin Dashboard</h1>
          <p className="text-on-surface-variant text-sm mt-1">HealthCopilot Platform Overview</p>
        </div>
        <Link href="/admin/audit">
          <button className="btn-secondary flex items-center gap-2 text-sm">
            <span className="material-symbols-outlined text-sm">history</span>
            Audit Log
          </button>
        </Link>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard icon="group" label="Total Users" value={dashboard?.stats?.total_users ?? 0} delta="+12" />
        <KpiCard icon="description" label="Reports Processed" value={dashboard?.stats?.total_reports ?? 0} color="secondary" delta="+45" />
        <KpiCard icon="stethoscope" label="Active Doctors" value={dashboard?.stats?.total_doctors ?? 0} color="tertiary" />
        <KpiCard icon="warning" label="Active Alerts" value={activeAlerts.length} color="error" />
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Active Alerts */}
        <section className="space-y-3 lg:col-span-1">
          <h2 className="text-lg font-bold text-primary font-headline flex items-center gap-2">
            <span className="material-symbols-outlined text-error text-xl">warning</span>
            Active Alerts
            {activeAlerts.length > 0 && (
              <span className="badge badge-error ml-auto">{activeAlerts.length}</span>
            )}
          </h2>
          {activeAlerts.length === 0 ? (
            <div className="card text-center py-6">
              <span className="material-symbols-outlined text-3xl text-on-tertiary-container">check_circle</span>
              <p className="text-sm text-on-surface-variant mt-2">All clear!</p>
            </div>
          ) : (
            <div className="space-y-2">
              {activeAlerts.slice(0, 5).map((alert: {
                id: string;
                alert_type: string;
                message: string;
                created_at: string;
              }) => (
                <div key={alert.id} className="bg-error-container rounded-xl p-3 flex gap-3">
                  <div className="flex-1">
                    <p className="text-xs font-bold text-on-error-container uppercase">{alert.alert_type?.replace("_", " ")}</p>
                    <p className="text-xs text-on-error-container/80 mt-0.5">{alert.message}</p>
                    <p className="text-[10px] text-on-error-container/60 mt-1">{formatRelative(alert.created_at)}</p>
                  </div>
                  <button onClick={() => resolveAlert(alert.id)}
                    className="text-xs font-semibold text-on-error-container border border-on-error-container/30 rounded-lg px-2 py-1 h-fit hover:bg-on-error-container/10 transition-colors">
                    Resolve
                  </button>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Failed Jobs */}
        <section className="space-y-3 lg:col-span-1">
          <h2 className="text-lg font-bold text-primary font-headline">Failed Jobs</h2>
          {failedJobs.length === 0 ? (
            <div className="card text-center py-6">
              <span className="material-symbols-outlined text-3xl text-on-tertiary-container">done_all</span>
              <p className="text-sm text-on-surface-variant mt-2">No failed jobs</p>
            </div>
          ) : (
            <div className="space-y-2">
              {failedJobs.map((job: {
                id: string;
                job_type: string;
                status: string;
                error_message?: string;
                created_at: string;
              }) => (
                <div key={job.id} className="card">
                  <div className="flex justify-between items-start gap-2">
                    <div>
                      <p className="text-xs font-bold text-on-surface">{capitalize(job.job_type)}</p>
                      {job.error_message && (
                        <p className="text-xs text-on-surface-variant mt-0.5 truncate max-w-[180px]">{job.error_message}</p>
                      )}
                      <p className="text-[10px] text-on-surface-variant mt-1">{formatRelative(job.created_at)}</p>
                    </div>
                    <button onClick={() => retryJob(job.id)}
                      className="text-xs font-semibold text-secondary border border-secondary/30 rounded-lg px-2 py-1 hover:bg-secondary-fixed/20 transition-colors shrink-0">
                      Retry
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Doctor Approvals */}
        <section className="space-y-3 lg:col-span-1">
          <h2 className="text-lg font-bold text-primary font-headline flex items-center gap-2">
            Pending Approvals
            {pendingApprovals.length > 0 && (
              <span className="badge badge-warning">{pendingApprovals.length}</span>
            )}
          </h2>
          {pendingApprovals.length === 0 ? (
            <div className="card text-center py-6">
              <span className="material-symbols-outlined text-3xl text-on-tertiary-container">verified_user</span>
              <p className="text-sm text-on-surface-variant mt-2">No pending approvals</p>
            </div>
          ) : (
            <div className="space-y-2">
              {pendingApprovals.map((approval: {
                id: string;
                doctor_name: string;
                specialty?: string;
                submitted_at: string;
              }) => (
                <div key={approval.id} className="card">
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-full bg-primary-fixed flex items-center justify-center text-primary font-bold text-xs shrink-0">
                      {approval.doctor_name.split(" ").map((n: string) => n[0]).join("").toUpperCase().slice(0, 2)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-semibold text-on-surface truncate">{approval.doctor_name}</p>
                      {approval.specialty && <p className="text-xs text-on-surface-variant">{approval.specialty}</p>}
                    </div>
                    <button onClick={() => approveDoctor(approval.id)}
                      className="text-xs font-semibold text-on-tertiary-container bg-tertiary-fixed/30 border border-on-tertiary-container/20 rounded-lg px-2 py-1 hover:bg-tertiary-fixed/50 transition-colors shrink-0">
                      Approve
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>

      {/* Job processing summary */}
      {dashboard?.processing_stats && (
        <section className="card">
          <h2 className="font-bold text-primary font-headline mb-4">Job Processing</h2>
          <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
            {Object.entries(dashboard.processing_stats).map(([status, count]) => (
              <div key={status} className="text-center">
                <div className="text-2xl font-extrabold text-on-surface">{count as number}</div>
                <div className="text-xs text-on-surface-variant capitalize">{status.replace("_", " ")}</div>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
