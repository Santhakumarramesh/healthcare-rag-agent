"use client";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { consultationsApi } from "@/lib/api";
import { formatDate, getStatusColor } from "@/lib/utils";
import Link from "next/link";

export default function ConsultationsPage() {
  const [tab, setTab] = useState<"upcoming" | "past">("upcoming");

  const { data, isLoading } = useQuery({
    queryKey: ["consultations", tab],
    queryFn: () => consultationsApi.list({
      status: tab === "upcoming" ? "scheduled" : "completed",
    }).then((r) => r.data),
  });

  const consultations = data?.consultations ?? data ?? [];

  return (
    <div className="max-w-2xl mx-auto px-5 py-8 space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-primary font-headline">Consultations</h1>
          <p className="text-sm text-on-surface-variant">Book and manage your doctor visits</p>
        </div>
        <Link href="/patient/consultations/book">
          <button className="btn-primary flex items-center gap-2 text-sm">
            <span className="material-symbols-outlined text-sm">add</span>
            Book
          </button>
        </Link>
      </div>

      {/* Tabs */}
      <div className="flex gap-2">
        {(["upcoming", "past"] as const).map((t) => (
          <button key={t} onClick={() => setTab(t)}
            className={`px-5 py-2 rounded-xl text-sm font-semibold capitalize transition-all ${
              tab === t ? "bg-primary text-white" : "bg-surface-container text-on-surface-variant hover:bg-surface-container-high"
            }`}>
            {t}
          </button>
        ))}
      </div>

      {/* List */}
      {isLoading ? (
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => <div key={i} className="card animate-pulse h-24" />)}
        </div>
      ) : consultations.length === 0 ? (
        <div className="card text-center py-12">
          <span className="material-symbols-outlined text-5xl text-on-surface-variant">video_call</span>
          <p className="font-semibold text-on-surface mt-3">No {tab} consultations</p>
          {tab === "upcoming" && (
            <Link href="/patient/consultations/book">
              <button className="btn-primary mt-4 text-sm">Book a Consultation</button>
            </Link>
          )}
        </div>
      ) : (
        <div className="space-y-3">
          {consultations.map((c: {
            id: string;
            doctor_name?: string;
            consultation_type: string;
            scheduled_at: string;
            status: string;
            notes?: string;
          }) => (
            <Link key={c.id} href={`/patient/consultations/${c.id}`}>
              <div className="card flex gap-4 cursor-pointer hover:shadow-card-md transition-shadow">
                <div className="w-12 h-12 rounded-xl bg-secondary-fixed/30 flex items-center justify-center shrink-0">
                  <span className="material-symbols-outlined text-on-secondary-container">
                    {c.consultation_type === "video" ? "video_call" : "phone_in_talk"}
                  </span>
                </div>
                <div className="flex-1">
                  <p className="font-semibold text-on-surface">{c.doctor_name || "Consultation"}</p>
                  <p className="text-xs text-on-surface-variant mt-0.5">{formatDate(c.scheduled_at, "full")}</p>
                  <p className="text-xs text-on-surface-variant capitalize">{c.consultation_type}</p>
                </div>
                <span className={`badge shrink-0 ${getStatusColor(c.status)}`}>{c.status}</span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
