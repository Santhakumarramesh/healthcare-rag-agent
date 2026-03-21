"use client";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { prescriptionsApi } from "@/lib/api";
import { formatRelative } from "@/lib/utils";
import toast from "react-hot-toast";

type RefillRequest = {
  id: string;
  patient_name?: string;
  medication_name: string;
  requested_at: string;
  status: "pending" | "approved" | "denied";
  notes?: string;
};

const STATUS_BADGE: Record<string, string> = {
  pending:  "badge-info",
  approved: "badge-success",
  denied:   "badge-gray",
};

export default function DoctorPrescriptionsPage() {
  const qc = useQueryClient();
  const [filter, setFilter] = useState<"pending" | "approved" | "all">("pending");

  const { data, isLoading } = useQuery({
    queryKey: ["doctor-prescriptions", filter],
    queryFn: () => prescriptionsApi.list().then((r) => r.data),
    retry: false,
  });

  const approveMutation = useMutation({
    mutationFn: (id: string) =>
      fetch(`${process.env.NEXT_PUBLIC_API_URL}/prescriptions/${id}/approve`, {
        method: "POST",
        headers: { Authorization: `Bearer ${document.cookie.match(/access_token=([^;]+)/)?.[1] ?? ""}` },
      }),
    onSuccess: () => {
      toast.success("Refill approved");
      qc.invalidateQueries({ queryKey: ["doctor-prescriptions"] });
    },
  });

  const allRefills: RefillRequest[] = data?.refill_requests ?? data?.items ?? [];
  const filtered = filter === "all"
    ? allRefills
    : allRefills.filter((r) => r.status === filter);

  return (
    <div className="max-w-4xl mx-auto px-6 py-8 space-y-6">
      <div>
        <h1 className="text-3xl font-extrabold text-primary font-headline tracking-tight">
          Prescription Refills
        </h1>
        <p className="text-on-surface-variant text-sm mt-1">
          Review and approve patient refill requests
        </p>
      </div>

      {/* Filter tabs */}
      <div className="flex gap-1 bg-surface-container p-1 rounded-xl w-fit">
        {(["pending", "approved", "all"] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-4 py-1.5 rounded-lg text-sm font-semibold capitalize transition-all ${
              filter === f
                ? "bg-surface text-primary shadow-sm"
                : "text-on-surface-variant hover:text-on-surface"
            }`}
          >
            {f}
          </button>
        ))}
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => <div key={i} className="card animate-pulse h-20 bg-surface-container" />)}
        </div>
      ) : filtered.length === 0 ? (
        <div className="card text-center py-16">
          <span className="material-symbols-outlined text-5xl text-on-surface-variant">medication</span>
          <p className="text-on-surface-variant mt-3 font-medium">
            No {filter === "all" ? "" : filter} refill requests
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map((r) => (
            <div key={r.id} className="card flex items-start justify-between gap-4">
              <div className="flex items-start gap-3 flex-1">
                <div className="w-10 h-10 rounded-xl bg-tertiary-fixed/20 flex items-center justify-center shrink-0">
                  <span className="material-symbols-outlined text-on-tertiary-container ms-fill">medication</span>
                </div>
                <div className="flex-1">
                  <p className="font-semibold text-on-surface">{r.medication_name}</p>
                  <p className="text-xs text-on-surface-variant">
                    {r.patient_name ? `Patient: ${r.patient_name} · ` : ""}
                    Requested {formatRelative(r.requested_at)}
                  </p>
                  {r.notes && (
                    <p className="text-xs text-on-surface-variant mt-1 bg-surface-container rounded px-2 py-1">
                      {r.notes}
                    </p>
                  )}
                </div>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <span className={STATUS_BADGE[r.status] ?? "badge-gray"}>{r.status}</span>
                {r.status === "pending" && (
                  <button
                    onClick={() => approveMutation.mutate(r.id)}
                    disabled={approveMutation.isPending}
                    className="btn-primary text-xs px-3 py-1.5"
                  >
                    Approve
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
