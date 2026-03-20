"use client";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { adminApi } from "@/lib/api";
import { formatDate } from "@/lib/utils";

export default function AuditLogPage() {
  const [page, setPage] = useState(1);
  const [action, setAction] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["audit-logs", page, action],
    queryFn: () => adminApi.getAuditLogs({ page, limit: 25, action: action || undefined }).then((r) => r.data),
  });

  const logs = data?.logs ?? [];
  const total = data?.total ?? 0;

  return (
    <div className="max-w-5xl mx-auto px-6 py-8 space-y-6">
      <div>
        <h1 className="text-2xl font-extrabold text-primary font-headline">System Audit Log</h1>
        <p className="text-sm text-on-surface-variant">{total} total audit events</p>
      </div>

      {/* Filter */}
      <div className="flex gap-3">
        <input value={action} onChange={(e) => { setAction(e.target.value); setPage(1); }}
          className="input-field max-w-xs" placeholder="Filter by action…" />
      </div>

      {/* Table */}
      <div className="card overflow-hidden p-0">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-outline-variant/20 bg-surface-container">
                {["Time", "User", "Action", "Resource", "IP"].map((h) => (
                  <th key={h} className="text-left px-4 py-3 text-xs font-semibold text-on-surface-variant uppercase tracking-wider">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/10">
              {isLoading ? (
                [...Array(8)].map((_, i) => (
                  <tr key={i} className="animate-pulse">
                    {[...Array(5)].map((_, j) => (
                      <td key={j} className="px-4 py-3"><div className="h-4 bg-surface-container rounded" /></td>
                    ))}
                  </tr>
                ))
              ) : logs.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-4 py-12 text-center text-on-surface-variant">No audit events found</td>
                </tr>
              ) : (
                logs.map((log: {
                  id: string;
                  created_at: string;
                  user_email?: string;
                  action: string;
                  resource_type?: string;
                  resource_id?: string;
                  ip_address?: string;
                }) => (
                  <tr key={log.id} className="hover:bg-surface-container/50 transition-colors">
                    <td className="px-4 py-3 text-xs text-on-surface-variant whitespace-nowrap">
                      {formatDate(log.created_at, "full")}
                    </td>
                    <td className="px-4 py-3 text-xs text-on-surface">{log.user_email ?? "—"}</td>
                    <td className="px-4 py-3">
                      <span className="font-mono text-xs bg-surface-container px-2 py-0.5 rounded text-on-surface">
                        {log.action}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-xs text-on-surface-variant">
                      {log.resource_type ? `${log.resource_type} ${log.resource_id ?? ""}` : "—"}
                    </td>
                    <td className="px-4 py-3 text-xs font-mono text-on-surface-variant">{log.ip_address ?? "—"}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        {total > 25 && (
          <div className="px-4 py-3 border-t border-outline-variant/20 flex justify-between items-center">
            <span className="text-xs text-on-surface-variant">Page {page} of {Math.ceil(total / 25)}</span>
            <div className="flex gap-2">
              <button disabled={page === 1} onClick={() => setPage((p) => p - 1)}
                className="btn-secondary text-xs px-3 py-1.5 disabled:opacity-50">Previous</button>
              <button disabled={page >= Math.ceil(total / 25)} onClick={() => setPage((p) => p + 1)}
                className="btn-secondary text-xs px-3 py-1.5 disabled:opacity-50">Next</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
