"use client";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { insuranceApi } from "@/lib/api";
import { formatDate, getStatusColor } from "@/lib/utils";
import toast from "react-hot-toast";

export default function InsurancePage() {
  const qc = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ["insurance"],
    queryFn: () => insuranceApi.snapshot().then((r) => r.data),
  });

  const { mutate: verify } = useMutation({
    mutationFn: (id: string) => insuranceApi.verify(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["insurance"] }); toast.success("Verification requested"); },
  });

  if (isLoading) {
    return <div className="max-w-2xl mx-auto px-5 py-8"><div className="card animate-pulse h-48" /></div>;
  }

  const insurance = data?.insurance ?? data;

  return (
    <div className="max-w-2xl mx-auto px-5 py-8 space-y-6">
      <div>
        <h1 className="text-2xl font-extrabold text-primary font-headline">Insurance</h1>
        <p className="text-sm text-on-surface-variant">Manage your health insurance coverage</p>
      </div>

      {!insurance ? (
        <div className="card text-center py-12 space-y-3">
          <span className="material-symbols-outlined text-5xl text-on-surface-variant">health_and_safety</span>
          <p className="font-semibold text-on-surface">No insurance on file</p>
          <p className="text-sm text-on-surface-variant">Add your insurance information to enable benefits verification</p>
          <button className="btn-primary">Add Insurance</button>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Insurance card */}
          <div className="bg-gradient-to-br from-primary to-primary-container rounded-2xl p-6 text-white space-y-4">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-xs font-semibold opacity-70 uppercase tracking-wider">Insurance Provider</p>
                <p className="text-xl font-extrabold font-headline mt-1">{insurance.provider_name}</p>
              </div>
              <span className="material-symbols-outlined text-3xl opacity-80 ms-fill">health_and_safety</span>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs opacity-70">Member ID</p>
                <p className="font-bold font-mono">{insurance.member_id}</p>
              </div>
              <div>
                <p className="text-xs opacity-70">Group #</p>
                <p className="font-bold font-mono">{insurance.group_number || "—"}</p>
              </div>
              <div>
                <p className="text-xs opacity-70">Plan Type</p>
                <p className="font-semibold">{insurance.plan_type || "—"}</p>
              </div>
              <div>
                <p className="text-xs opacity-70">Coverage End</p>
                <p className="font-semibold">{insurance.coverage_end_date ? formatDate(insurance.coverage_end_date) : "—"}</p>
              </div>
            </div>
          </div>

          {/* Status + verify */}
          <div className="card flex items-center gap-4">
            <span className={`badge ${getStatusColor(insurance.verification_status ?? "pending")}`}>
              {insurance.verification_status ?? "unverified"}
            </span>
            <div className="flex-1">
              <p className="text-sm font-medium text-on-surface">Verification Status</p>
              {insurance.last_verified_at && (
                <p className="text-xs text-on-surface-variant">Last verified {formatDate(insurance.last_verified_at)}</p>
              )}
            </div>
            {insurance.verification_status !== "verified" && (
              <button onClick={() => verify(insurance.id)}
                className="text-sm font-semibold text-secondary border border-secondary rounded-xl px-4 py-2 hover:bg-secondary-fixed/20 transition-colors">
                Verify Now
              </button>
            )}
          </div>

          {/* Coverage details */}
          {(insurance.copay || insurance.deductible || insurance.out_of_pocket_max) && (
            <div className="card space-y-3">
              <h3 className="font-bold text-on-surface font-headline">Coverage Details</h3>
              <div className="grid grid-cols-3 gap-4">
                {insurance.copay && (
                  <div className="text-center">
                    <div className="text-xl font-extrabold text-on-surface">${insurance.copay}</div>
                    <div className="text-xs text-on-surface-variant">Copay</div>
                  </div>
                )}
                {insurance.deductible && (
                  <div className="text-center">
                    <div className="text-xl font-extrabold text-on-surface">${insurance.deductible}</div>
                    <div className="text-xs text-on-surface-variant">Deductible</div>
                  </div>
                )}
                {insurance.out_of_pocket_max && (
                  <div className="text-center">
                    <div className="text-xl font-extrabold text-on-surface">${insurance.out_of_pocket_max}</div>
                    <div className="text-xs text-on-surface-variant">OOP Max</div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
