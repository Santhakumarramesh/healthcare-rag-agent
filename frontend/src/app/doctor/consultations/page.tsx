"use client";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { consultationsApi } from "@/lib/api";
import { formatDate } from "@/lib/utils";
import toast from "react-hot-toast";

type Consultation = {
  id: string;
  patient_name?: string;
  patient_user_id: string;
  scheduled_at: string;
  type: string;
  reason?: string;
  status: string;
};

const STATUS_COLORS: Record<string, string> = {
  scheduled:  "badge-info",
  ongoing:    "bg-secondary text-white text-xs font-semibold px-2 py-0.5 rounded-full",
  completed:  "badge-success",
  cancelled:  "badge-gray",
};

const TABS = ["upcoming", "completed", "all"] as const;
type Tab = typeof TABS[number];

export default function DoctorConsultationsPage() {
  const qc = useQueryClient();
  const [tab, setTab] = useState<Tab>("upcoming");
  const [notes, setNotes] = useState<Record<string, string>>({});

  const statusFilter = tab === "upcoming" ? "scheduled" : tab === "completed" ? "completed" : undefined;

  const { data, isLoading } = useQuery({
    queryKey: ["doctor-consultations", tab],
    queryFn: () =>
      consultationsApi.list(statusFilter ? { status: statusFilter } : {}).then((r) => r.data),
    retry: false,
  });

  const completeMutation = useMutation({
    mutationFn: ({ id, note }: { id: string; note: string }) =>
      consultationsApi.complete(id, note),
    onSuccess: () => {
      toast.success("Consultation marked as complete");
      qc.invalidateQueries({ queryKey: ["doctor-consultations"] });
    },
    onError: () => toast.error("Failed to complete consultation"),
  });

  const consultations: Consultation[] = data?.consultations ?? data ?? [];

  return (
    <div className="max-w-4xl mx-auto px-6 py-8 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-extrabold text-primary font-headline tracking-tight">
            Consultations
          </h1>
          <p className="text-on-surface-variant text-sm mt-1">
            Manage your scheduled and past patient consultations
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-surface-container p-1 rounded-xl w-fit">
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-1.5 rounded-lg text-sm font-semibold capitalize transition-all ${
              tab === t
                ? "bg-surface text-primary shadow-sm"
                : "text-on-surface-variant hover:text-on-surface"
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {/* List */}
      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="card animate-pulse h-24 bg-surface-container" />
          ))}
        </div>
      ) : consultations.length === 0 ? (
        <div className="card text-center py-16">
          <span className="material-symbols-outlined text-5xl text-on-surface-variant">
            event_available
          </span>
          <p className="text-on-surface-variant mt-3 font-medium">No {tab} consultations</p>
        </div>
      ) : (
        <div className="space-y-3">
          {consultations.map((c) => (
            <div key={c.id} className="card space-y-3">
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-primary-fixed/30 flex items-center justify-center shrink-0">
                    <span className="material-symbols-outlined text-primary text-sm ms-fill">person</span>
                  </div>
                  <div>
                    <p className="font-semibold text-on-surface">
                      {c.patient_name ?? `Patient #${c.patient_user_id.slice(-6)}`}
                    </p>
                    <p className="text-xs text-on-surface-variant">
                      {formatDate(c.scheduled_at, "full")} · {c.type}
                    </p>
                  </div>
                </div>
                <span className={`${STATUS_COLORS[c.status] ?? "badge-gray"} shrink-0`}>
                  {c.status}
                </span>
              </div>

              {c.reason && (
                <p className="text-sm text-on-surface-variant bg-surface-container rounded-lg px-3 py-2">
                  {c.reason}
                </p>
              )}

              {c.status === "scheduled" && (
                <div className="space-y-2">
                  <textarea
                    placeholder="Clinical notes (optional)…"
                    rows={2}
                    value={notes[c.id] ?? ""}
                    onChange={(e) => setNotes((n) => ({ ...n, [c.id]: e.target.value }))}
                    className="w-full text-sm bg-surface-container-highest rounded-xl px-3 py-2 text-on-surface placeholder:text-on-surface-variant resize-none focus:outline-none focus:ring-2 focus:ring-primary/40"
                  />
                  <button
                    onClick={() => completeMutation.mutate({ id: c.id, note: notes[c.id] ?? "" })}
                    disabled={completeMutation.isPending}
                    className="btn-primary text-sm"
                  >
                    Mark Complete
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
