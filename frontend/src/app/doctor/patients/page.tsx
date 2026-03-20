"use client";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { doctorsApi } from "@/lib/api";
import { formatRelative } from "@/lib/utils";

export default function DoctorPatientsPage() {
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState<"all" | "high_risk" | "pending_review">("all");

  const { data, isLoading } = useQuery({
    queryKey: ["doctor-patients", filter],
    queryFn: () => doctorsApi.getPatientQueue().then((r) => r.data),
  });

  const patients = (data?.all_patients ?? []).filter((p: { patient_name: string; condition?: string }) =>
    !search ||
    p.patient_name.toLowerCase().includes(search.toLowerCase()) ||
    p.condition?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="max-w-3xl mx-auto px-6 py-8 space-y-6">
      <div>
        <h1 className="text-2xl font-extrabold text-primary font-headline">Patients</h1>
        <p className="text-sm text-on-surface-variant">Manage your patient list and care plans</p>
      </div>

      {/* Search + filter */}
      <div className="flex gap-3">
        <div className="relative flex-1">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 material-symbols-outlined text-on-surface-variant text-sm">search</span>
          <input value={search} onChange={(e) => setSearch(e.target.value)}
            className="input-field pl-9" placeholder="Search patients…" />
        </div>
      </div>

      {/* Filter tabs */}
      <div className="flex gap-2 overflow-x-auto">
        {(["all", "high_risk", "pending_review"] as const).map((f) => (
          <button key={f} onClick={() => setFilter(f)}
            className={`px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
              filter === f ? "bg-primary text-white" : "bg-surface-container text-on-surface-variant hover:bg-surface-container-high"
            }`}>
            {f === "all" ? "All Patients" : f === "high_risk" ? "High Risk" : "Pending Review"}
          </button>
        ))}
      </div>

      {/* Patient list */}
      {isLoading ? (
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="card animate-pulse h-20" />
          ))}
        </div>
      ) : patients.length === 0 ? (
        <div className="card text-center py-12">
          <span className="material-symbols-outlined text-5xl text-on-surface-variant">group</span>
          <p className="font-semibold text-on-surface mt-3">No patients found</p>
        </div>
      ) : (
        <div className="space-y-2">
          {patients.map((p: {
            patient_id: string;
            patient_name: string;
            condition?: string;
            last_activity?: string;
            risk_level?: string;
            care_score?: number;
            pending_items?: number;
          }) => (
            <Link key={p.patient_id} href={`/doctor/patients/${p.patient_id}`}>
              <div className="card flex items-center gap-4 cursor-pointer hover:shadow-card-md transition-shadow">
                <div className="w-11 h-11 rounded-full bg-primary-fixed flex items-center justify-center text-primary font-bold text-sm shrink-0">
                  {p.patient_name.split(" ").map((n: string) => n[0]).join("").toUpperCase().slice(0, 2)}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-on-surface">{p.patient_name}</p>
                  <div className="flex items-center gap-2 mt-0.5">
                    {p.condition && <p className="text-xs text-on-surface-variant">{p.condition}</p>}
                    {p.last_activity && (
                      <p className="text-xs text-on-surface-variant">· {formatRelative(p.last_activity)}</p>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  {p.care_score != null && (
                    <div className="text-center">
                      <div className="text-sm font-bold text-on-surface">{p.care_score}</div>
                      <div className="text-[10px] text-on-surface-variant">score</div>
                    </div>
                  )}
                  {p.risk_level === "high" && (
                    <span className="material-symbols-outlined text-error text-sm ms-fill">warning</span>
                  )}
                  {p.pending_items != null && p.pending_items > 0 && (
                    <span className="badge badge-warning">{p.pending_items} pending</span>
                  )}
                  <span className="material-symbols-outlined text-on-surface-variant text-sm">chevron_right</span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
