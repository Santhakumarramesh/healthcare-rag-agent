"use client";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { formatRelative } from "@/lib/utils";

type Ticket = {
  id: string;
  user_id: string;
  subject: string;
  message: string;
  status: "open" | "in_progress" | "resolved";
  priority: "low" | "medium" | "high";
  created_at: string;
};

const PRIORITY_BADGE: Record<string, string> = {
  high:   "bg-error-container text-on-error-container text-xs font-semibold px-2 py-0.5 rounded-full",
  medium: "badge-info",
  low:    "badge-gray",
};
const STATUS_BADGE: Record<string, string> = {
  open:        "badge-info",
  in_progress: "bg-secondary text-white text-xs font-semibold px-2 py-0.5 rounded-full",
  resolved:    "badge-success",
};

export default function AdminSupportPage() {
  const [statusFilter, setStatusFilter] = useState<"open" | "in_progress" | "resolved" | "all">("open");

  const { data, isLoading } = useQuery({
    queryKey: ["admin-support-tickets", statusFilter],
    queryFn: () =>
      api
        .get("/support/tickets", {
          params: statusFilter !== "all" ? { status: statusFilter } : {},
        })
        .then((r) => r.data),
    retry: false,
  });

  const tickets: Ticket[] = data?.tickets ?? data ?? [];

  return (
    <div className="max-w-5xl mx-auto px-6 py-8 space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-extrabold text-primary font-headline tracking-tight">
            Support Tickets
          </h1>
          <p className="text-on-surface-variant text-sm mt-1">
            Manage user support requests and enquiries
          </p>
        </div>
        <div className="flex items-center gap-2 px-4 py-2 bg-error-container rounded-xl">
          <span className="material-symbols-outlined text-on-error-container ms-fill text-sm">
            support_agent
          </span>
          <span className="text-on-error-container font-semibold text-sm">
            {tickets.filter((t) => t.status === "open").length} open
          </span>
        </div>
      </div>

      {/* Status tabs */}
      <div className="flex gap-1 bg-surface-container p-1 rounded-xl w-fit">
        {(["open", "in_progress", "resolved", "all"] as const).map((s) => (
          <button
            key={s}
            onClick={() => setStatusFilter(s)}
            className={`px-4 py-1.5 rounded-lg text-sm font-semibold capitalize transition-all ${
              statusFilter === s
                ? "bg-surface text-primary shadow-sm"
                : "text-on-surface-variant hover:text-on-surface"
            }`}
          >
            {s.replace("_", " ")}
          </button>
        ))}
      </div>

      {/* Ticket list */}
      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => <div key={i} className="card animate-pulse h-24 bg-surface-container" />)}
        </div>
      ) : tickets.length === 0 ? (
        <div className="card text-center py-16">
          <span className="material-symbols-outlined text-5xl text-on-surface-variant">
            support_agent
          </span>
          <p className="text-on-surface-variant mt-3 font-medium">
            No {statusFilter === "all" ? "" : statusFilter.replace("_", " ")} tickets
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {tickets.map((t) => (
            <div key={t.id} className="card space-y-3">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="font-semibold text-on-surface">{t.subject}</p>
                  <p className="text-xs text-on-surface-variant">
                    User #{t.user_id.slice(-6)} · {formatRelative(t.created_at)}
                  </p>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <span className={PRIORITY_BADGE[t.priority] ?? "badge-gray"}>{t.priority}</span>
                  <span className={STATUS_BADGE[t.status] ?? "badge-gray"}>{t.status.replace("_", " ")}</span>
                </div>
              </div>
              <p className="text-sm text-on-surface-variant bg-surface-container rounded-lg px-3 py-2 line-clamp-2">
                {t.message}
              </p>
              {t.status === "open" && (
                <div className="flex gap-2">
                  <button
                    onClick={() =>
                      api.post(`/support/tickets/${t.id}/assign`).catch(() => {})
                    }
                    className="btn-primary text-sm"
                  >
                    Take Ticket
                  </button>
                  <button
                    onClick={() =>
                      api.post(`/support/tickets/${t.id}/resolve`).catch(() => {})
                    }
                    className="px-4 py-2 rounded-xl border border-outline-variant text-sm font-semibold text-on-surface hover:bg-surface-container transition-colors"
                  >
                    Mark Resolved
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
