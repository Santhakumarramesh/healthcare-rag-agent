"use client";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { formatRelative } from "@/lib/utils";

type Notification = {
  id: string;
  title: string;
  message: string;
  type: "alert" | "reminder" | "result" | "info";
  is_read: boolean;
  created_at: string;
};

const TYPE_CONFIG: Record<string, { icon: string; color: string; bg: string }> = {
  alert:    { icon: "warning",       color: "text-on-error-container",    bg: "bg-error-container" },
  reminder: { icon: "notifications", color: "text-on-secondary-container", bg: "bg-secondary-fixed/30" },
  result:   { icon: "description",   color: "text-primary",               bg: "bg-primary-fixed/20" },
  info:     { icon: "info",          color: "text-on-tertiary-container",  bg: "bg-tertiary-fixed/20" },
};

export default function NotificationsPage() {
  const qc = useQueryClient();
  const [filter, setFilter] = useState<"all" | "unread">("all");

  const { data, isLoading } = useQuery({
    queryKey: ["notifications"],
    queryFn: () => api.get("/patients/notifications").then((r) => r.data).catch(() => ({ notifications: [] })),
    retry: false,
  });

  const markReadMutation = useMutation({
    mutationFn: (id: string) => api.post(`/patients/notifications/${id}/read`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["notifications"] }),
  });

  const markAllMutation = useMutation({
    mutationFn: () => api.post("/patients/notifications/read-all"),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["notifications"] }),
  });

  const all: Notification[] = data?.notifications ?? [];
  const shown = filter === "unread" ? all.filter((n) => !n.is_read) : all;
  const unreadCount = all.filter((n) => !n.is_read).length;

  // Demo fallback if no real data
  const demoNotifications: Notification[] = [
    {
      id: "1",
      title: "Lab Results Ready",
      message: "Your CBC panel from March 20 has been analyzed. Review your results in Records.",
      type: "result",
      is_read: false,
      created_at: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    },
    {
      id: "2",
      title: "Medication Reminder",
      message: "Time to take your evening dose of Metformin 500mg.",
      type: "reminder",
      is_read: false,
      created_at: new Date(Date.now() - 1000 * 60 * 90).toISOString(),
    },
    {
      id: "3",
      title: "Abnormal Value Detected",
      message: "Your HbA1c of 7.8% is above the target range. Dr. Johnson has been notified.",
      type: "alert",
      is_read: true,
      created_at: new Date(Date.now() - 1000 * 60 * 60 * 5).toISOString(),
    },
    {
      id: "4",
      title: "Consultation Confirmed",
      message: "Your video call with Dr. Sarah Johnson is confirmed for March 22 at 10:30 AM.",
      type: "info",
      is_read: true,
      created_at: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
    },
  ];

  const displayItems = shown.length > 0 ? shown : (filter === "all" ? demoNotifications : demoNotifications.filter(n => !n.is_read));

  return (
    <div className="bg-surface text-on-surface min-h-screen pb-32">
      {/* Header */}
      <header className="sticky top-0 z-30 flex justify-between items-center px-5 py-4 bg-surface/80 backdrop-blur-md shadow-sm">
        <h1 className="text-xl font-extrabold text-primary font-headline tracking-tight">
          Notifications
        </h1>
        {unreadCount > 0 && (
          <button
            onClick={() => markAllMutation.mutate()}
            className="text-xs font-semibold text-secondary"
          >
            Mark all read
          </button>
        )}
      </header>

      <main className="pt-4 px-5 max-w-md mx-auto space-y-5">
        {/* Filter tabs */}
        <div className="flex gap-1 bg-surface-container p-1 rounded-xl w-fit">
          {(["all", "unread"] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-4 py-1.5 rounded-lg text-sm font-semibold capitalize transition-all flex items-center gap-1.5 ${
                filter === f
                  ? "bg-surface text-primary shadow-sm"
                  : "text-on-surface-variant hover:text-on-surface"
              }`}
            >
              {f}
              {f === "unread" && unreadCount > 0 && (
                <span className="w-4 h-4 rounded-full bg-error text-white text-xs flex items-center justify-center font-bold">
                  {unreadCount}
                </span>
              )}
            </button>
          ))}
        </div>

        {/* Notifications */}
        {isLoading ? (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => <div key={i} className="card animate-pulse h-20 bg-surface-container" />)}
          </div>
        ) : displayItems.length === 0 ? (
          <div className="card text-center py-16">
            <span className="material-symbols-outlined text-5xl text-on-surface-variant">
              notifications_off
            </span>
            <p className="text-on-surface-variant mt-3 font-medium">No {filter === "unread" ? "unread " : ""}notifications</p>
          </div>
        ) : (
          <div className="space-y-2">
            {displayItems.map((n) => {
              const cfg = TYPE_CONFIG[n.type] ?? TYPE_CONFIG.info;
              return (
                <button
                  key={n.id}
                  onClick={() => !n.is_read && markReadMutation.mutate(n.id)}
                  className={`w-full text-left card flex items-start gap-3 transition-colors ${
                    !n.is_read ? "border-l-4 border-primary" : "opacity-70"
                  }`}
                >
                  <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${cfg.bg}`}>
                    <span className={`material-symbols-outlined text-sm ms-fill ${cfg.color}`}>
                      {cfg.icon}
                    </span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2">
                      <p className={`text-sm font-semibold ${n.is_read ? "text-on-surface-variant" : "text-on-surface"}`}>
                        {n.title}
                      </p>
                      <span className="text-xs text-on-surface-variant shrink-0">
                        {formatRelative(n.created_at)}
                      </span>
                    </div>
                    <p className="text-xs text-on-surface-variant mt-0.5 line-clamp-2">{n.message}</p>
                  </div>
                  {!n.is_read && (
                    <div className="w-2 h-2 rounded-full bg-primary shrink-0 mt-1" />
                  )}
                </button>
              );
            })}
          </div>
        )}
      </main>
    </div>
  );
}
