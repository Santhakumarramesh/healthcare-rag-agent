"use client";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { prescriptionsApi } from "@/lib/api";
import { formatDate, getStatusColor } from "@/lib/utils";
import toast from "react-hot-toast";
import Link from "next/link";

export default function PrescriptionsPage() {
  const qc = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ["prescriptions"],
    queryFn: () => prescriptionsApi.list().then((r) => r.data),
  });

  const { data: ordersData } = useQuery({
    queryKey: ["orders"],
    queryFn: () => prescriptionsApi.getOrders().then((r) => r.data),
  });

  const { mutate: requestRefill } = useMutation({
    mutationFn: (id: string) => prescriptionsApi.requestRefill(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["prescriptions"] }); toast.success("Refill requested!"); },
    onError: (err: unknown) => {
      const msg = (err as { response?: { data?: { detail?: string } } }).response?.data?.detail || "Could not request refill";
      toast.error(msg);
    },
  });

  const prescriptions = data?.prescriptions ?? data ?? [];
  const orders = ordersData?.orders ?? ordersData ?? [];

  return (
    <div className="max-w-2xl mx-auto px-5 py-8 space-y-8">
      <div>
        <h1 className="text-2xl font-extrabold text-primary font-headline">Prescriptions & Refills</h1>
        <p className="text-sm text-on-surface-variant">Manage your medications and refill requests</p>
      </div>

      {/* Active Prescriptions */}
      <section className="space-y-3">
        <h2 className="font-bold text-on-surface font-headline">Active Prescriptions</h2>
        {isLoading ? (
          <div className="space-y-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="card animate-pulse h-20" />
            ))}
          </div>
        ) : prescriptions.length === 0 ? (
          <div className="card text-center py-10">
            <span className="material-symbols-outlined text-5xl text-on-surface-variant">medication</span>
            <p className="font-semibold text-on-surface mt-3">No prescriptions</p>
            <p className="text-sm text-on-surface-variant">Your doctor will add prescriptions here</p>
          </div>
        ) : (
          <div className="space-y-3">
            {prescriptions.map((rx: {
              id: string;
              medication_name: string;
              dosage: string;
              frequency: string;
              refills_remaining: number;
              status: string;
              prescribed_at: string;
              prescribing_doctor?: string;
            }) => (
              <div key={rx.id} className="card">
                <div className="flex justify-between items-start gap-3">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-secondary-fixed/30 flex items-center justify-center shrink-0">
                      <span className="material-symbols-outlined text-on-secondary-container">medication</span>
                    </div>
                    <div>
                      <p className="font-semibold text-on-surface">{rx.medication_name}</p>
                      <p className="text-xs text-on-surface-variant">
                        {rx.dosage} · {rx.frequency}
                      </p>
                      {rx.prescribing_doctor && (
                        <p className="text-xs text-on-surface-variant">Dr. {rx.prescribing_doctor}</p>
                      )}
                    </div>
                  </div>
                  <span className={`badge ${getStatusColor(rx.status)}`}>{rx.status}</span>
                </div>

                <div className="mt-3 pt-3 border-t border-outline-variant/20 flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="text-xs text-on-surface-variant">
                      <span className="font-semibold text-on-surface">{rx.refills_remaining}</span> refills left
                    </div>
                    <div className="text-xs text-on-surface-variant">
                      Prescribed {formatDate(rx.prescribed_at)}
                    </div>
                  </div>
                  {rx.refills_remaining > 0 && rx.status === "active" && (
                    <button
                      onClick={() => requestRefill(rx.id)}
                      className="text-xs font-semibold text-secondary border border-secondary rounded-lg px-3 py-1.5 hover:bg-secondary-fixed/20 transition-colors"
                    >
                      Request Refill
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Orders */}
      {orders.length > 0 && (
        <section className="space-y-3">
          <h2 className="font-bold text-on-surface font-headline">Recent Orders</h2>
          {orders.map((order: {
            id: string;
            status: string;
            total_amount: number;
            created_at: string;
            items?: { medication_name: string }[];
          }) => (
            <div key={order.id} className="card flex items-center gap-4">
              <div className="w-10 h-10 rounded-xl bg-tertiary-fixed/20 flex items-center justify-center shrink-0">
                <span className="material-symbols-outlined text-on-tertiary-container">local_shipping</span>
              </div>
              <div className="flex-1">
                <p className="font-semibold text-on-surface text-sm">
                  {order.items?.map((i) => i.medication_name).join(", ") || "Order"}
                </p>
                <p className="text-xs text-on-surface-variant">{formatDate(order.created_at)} · ${order.total_amount?.toFixed(2)}</p>
              </div>
              <div className="flex flex-col items-end gap-1">
                <span className={`badge ${getStatusColor(order.status)}`}>{order.status}</span>
                <Link href={`/patient/prescriptions/orders/${order.id}`}
                  className="text-xs text-secondary hover:underline">Track</Link>
              </div>
            </div>
          ))}
        </section>
      )}
    </div>
  );
}
