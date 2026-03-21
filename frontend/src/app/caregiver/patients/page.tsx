"use client";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import Link from "next/link";

type CarePatient = {
  id: string;
  name: string;
  email: string;
  relationship?: string;
  care_score?: number;
  last_check?: string;
  active_alerts?: number;
};

function ScoreRing({ score }: { score: number }) {
  const color = score >= 75 ? "text-on-tertiary-container" : score >= 50 ? "text-secondary" : "text-error";
  return (
    <div className={`text-2xl font-extrabold font-headline ${color}`}>{score}</div>
  );
}

export default function CaregiverPatientsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["caregiver-patients"],
    queryFn: () => api.get("/caregiver/patients").then((r) => r.data),
    retry: false,
  });

  const patients: CarePatient[] = data?.patients ?? data ?? [];

  return (
    <div className="max-w-3xl mx-auto px-6 py-8 space-y-6">
      <div>
        <h1 className="text-3xl font-extrabold text-primary font-headline tracking-tight">
          My Care Recipients
        </h1>
        <p className="text-on-surface-variant text-sm mt-1">
          Monitor health status for everyone in your care
        </p>
      </div>

      {isLoading ? (
        <div className="space-y-4">
          {[1, 2].map((i) => <div key={i} className="card animate-pulse h-28 bg-surface-container" />)}
        </div>
      ) : patients.length === 0 ? (
        <div className="card text-center py-16 space-y-4">
          <span className="material-symbols-outlined text-5xl text-on-surface-variant">
            family_restroom
          </span>
          <p className="text-on-surface-variant font-medium">No care recipients linked yet</p>
          <p className="text-sm text-on-surface-variant max-w-xs mx-auto">
            Ask the patient to add you as their caregiver from their profile settings.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {patients.map((p) => (
            <Link key={p.id} href={`/caregiver/patients/${p.id}`}>
              <div className="card flex items-center gap-4 cursor-pointer hover:shadow-card-md transition-shadow">
                {/* Avatar */}
                <div className="w-14 h-14 rounded-2xl bg-primary-fixed flex items-center justify-center shrink-0 text-primary font-bold text-lg">
                  {p.name.split(" ").map((n) => n[0]).join("").toUpperCase().slice(0, 2)}
                </div>

                {/* Info */}
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-on-surface">{p.name}</p>
                  <p className="text-xs text-on-surface-variant truncate">{p.email}</p>
                  {p.relationship && (
                    <span className="badge-gray text-xs mt-1 inline-block">{p.relationship}</span>
                  )}
                </div>

                {/* Care score */}
                {p.care_score != null && (
                  <div className="text-center shrink-0">
                    <ScoreRing score={p.care_score} />
                    <div className="text-xs text-on-surface-variant">Care Score</div>
                  </div>
                )}

                {/* Alerts badge */}
                {(p.active_alerts ?? 0) > 0 && (
                  <div className="shrink-0 w-6 h-6 rounded-full bg-error flex items-center justify-center">
                    <span className="text-white text-xs font-bold">{p.active_alerts}</span>
                  </div>
                )}

                <span className="material-symbols-outlined text-on-surface-variant shrink-0">
                  chevron_right
                </span>
              </div>
            </Link>
          ))}
        </div>
      )}

      {/* Quick tip */}
      <div className="flex gap-3 bg-primary-fixed/10 border border-primary/20 rounded-2xl p-4">
        <span className="material-symbols-outlined text-primary mt-0.5 shrink-0">info</span>
        <p className="text-sm text-on-surface">
          You&apos;ll receive alerts when a care recipient uploads a new report or has abnormal lab values.
          Make sure notifications are enabled in your settings.
        </p>
      </div>
    </div>
  );
}
