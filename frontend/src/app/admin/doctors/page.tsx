"use client";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { adminApi } from "@/lib/api";
import { formatRelative } from "@/lib/utils";
import toast from "react-hot-toast";

type DoctorApproval = {
  user_id: string;
  name: string;
  email: string;
  specialties?: string[];
  license_number?: string;
  verification_status: "pending" | "approved" | "rejected";
  submitted_at?: string;
};

const STATUS_BADGE: Record<string, string> = {
  pending:  "badge-info",
  approved: "badge-success",
  rejected: "badge-gray",
};

export default function AdminDoctorsPage() {
  const qc = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ["admin-doctor-approvals"],
    queryFn: () => adminApi.getDoctorApprovals().then((r) => r.data),
    retry: false,
  });

  const approveMutation = useMutation({
    mutationFn: (id: string) => adminApi.approveDoctor(id),
    onSuccess: () => {
      toast.success("Doctor approved");
      qc.invalidateQueries({ queryKey: ["admin-doctor-approvals"] });
    },
    onError: () => toast.error("Failed to approve doctor"),
  });

  const doctors: DoctorApproval[] = data?.doctors ?? data ?? [];
  const pending = doctors.filter((d) => d.verification_status === "pending");
  const approved = doctors.filter((d) => d.verification_status === "approved");

  return (
    <div className="max-w-5xl mx-auto px-6 py-8 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-extrabold text-primary font-headline tracking-tight">
          Doctor Approvals
        </h1>
        <p className="text-on-surface-variant text-sm mt-1">
          Verify and onboard new healthcare providers
        </p>
      </div>

      {/* Stats strip */}
      <div className="grid grid-cols-2 gap-4">
        <div className="card flex items-center gap-4">
          <div className="w-10 h-10 rounded-xl bg-error-container flex items-center justify-center">
            <span className="material-symbols-outlined text-on-error-container ms-fill">pending_actions</span>
          </div>
          <div>
            <div className="text-2xl font-extrabold text-on-surface font-headline">{pending.length}</div>
            <div className="text-xs text-on-surface-variant">Pending review</div>
          </div>
        </div>
        <div className="card flex items-center gap-4">
          <div className="w-10 h-10 rounded-xl bg-primary-fixed/20 flex items-center justify-center">
            <span className="material-symbols-outlined text-primary ms-fill">verified</span>
          </div>
          <div>
            <div className="text-2xl font-extrabold text-on-surface font-headline">{approved.length}</div>
            <div className="text-xs text-on-surface-variant">Approved providers</div>
          </div>
        </div>
      </div>

      {/* Pending section */}
      {pending.length > 0 && (
        <section className="space-y-3">
          <h2 className="text-lg font-bold text-primary font-headline">Pending Review</h2>
          {pending.map((doc) => (
            <div key={doc.user_id} className="card border-l-4 border-error/60 space-y-3">
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-error-container flex items-center justify-center shrink-0">
                    <span className="material-symbols-outlined text-on-error-container text-sm ms-fill">
                      stethoscope
                    </span>
                  </div>
                  <div>
                    <p className="font-semibold text-on-surface">{doc.name}</p>
                    <p className="text-xs text-on-surface-variant">{doc.email}</p>
                  </div>
                </div>
                <span className={STATUS_BADGE[doc.verification_status] ?? "badge-gray"}>
                  {doc.verification_status}
                </span>
              </div>
              <div className="grid grid-cols-2 gap-3 text-sm">
                {doc.license_number && (
                  <div className="bg-surface-container rounded-lg px-3 py-2">
                    <span className="text-xs text-on-surface-variant uppercase tracking-wide">License</span>
                    <p className="font-medium text-on-surface">{doc.license_number}</p>
                  </div>
                )}
                {doc.specialties && doc.specialties.length > 0 && (
                  <div className="bg-surface-container rounded-lg px-3 py-2">
                    <span className="text-xs text-on-surface-variant uppercase tracking-wide">Specialties</span>
                    <p className="font-medium text-on-surface">{doc.specialties.join(", ")}</p>
                  </div>
                )}
              </div>
              <button
                onClick={() => approveMutation.mutate(doc.user_id)}
                disabled={approveMutation.isPending}
                className="btn-primary text-sm"
              >
                Approve Doctor
              </button>
            </div>
          ))}
        </section>
      )}

      {/* All doctors */}
      <section className="space-y-3">
        <h2 className="text-lg font-bold text-primary font-headline">
          All Providers ({doctors.length})
        </h2>
        {isLoading ? (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => <div key={i} className="card animate-pulse h-16 bg-surface-container" />)}
          </div>
        ) : doctors.length === 0 ? (
          <div className="card text-center py-12">
            <span className="material-symbols-outlined text-5xl text-on-surface-variant">
              stethoscope
            </span>
            <p className="text-on-surface-variant mt-3 font-medium">No doctor applications yet</p>
          </div>
        ) : (
          doctors.map((doc) => (
            <div key={doc.user_id} className="card flex items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-primary-fixed/20 flex items-center justify-center">
                  <span className="material-symbols-outlined text-primary text-sm ms-fill">person</span>
                </div>
                <div>
                  <p className="font-semibold text-on-surface">{doc.name}</p>
                  <p className="text-xs text-on-surface-variant">{doc.email}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                {doc.specialties?.slice(0, 2).map((s) => (
                  <span key={s} className="badge-gray text-xs">{s}</span>
                ))}
                <span className={STATUS_BADGE[doc.verification_status] ?? "badge-gray"}>
                  {doc.verification_status}
                </span>
              </div>
            </div>
          ))
        )}
      </section>
    </div>
  );
}
