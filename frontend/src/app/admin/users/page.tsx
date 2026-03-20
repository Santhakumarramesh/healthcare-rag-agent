"use client";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { adminApi } from "@/lib/api";
import { formatDate, getRoleBadgeColor } from "@/lib/utils";

export default function AdminUsersPage() {
  const [search, setSearch] = useState("");
  const [role, setRole] = useState("");
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery({
    queryKey: ["admin-users", search, role, page],
    queryFn: () => adminApi.getUsers({ search, role: role || undefined, page, limit: 20 }).then((r) => r.data),
  });

  const users = data?.users ?? [];
  const total = data?.total ?? 0;

  const ROLES = ["", "patient", "doctor", "admin", "caregiver", "pharmacist", "support", "superadmin"];

  return (
    <div className="max-w-5xl mx-auto px-6 py-8 space-y-6">
      <div>
        <h1 className="text-2xl font-extrabold text-primary font-headline">Users</h1>
        <p className="text-sm text-on-surface-variant">{total} total users</p>
      </div>

      {/* Filters */}
      <div className="flex gap-3">
        <div className="relative flex-1">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 material-symbols-outlined text-on-surface-variant text-sm">search</span>
          <input value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            className="input-field pl-9" placeholder="Search by name or email…" />
        </div>
        <select value={role} onChange={(e) => { setRole(e.target.value); setPage(1); }}
          className="input-field w-40">
          <option value="">All Roles</option>
          {ROLES.slice(1).map((r) => <option key={r} value={r}>{r}</option>)}
        </select>
      </div>

      {/* Table */}
      <div className="card overflow-hidden p-0">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-outline-variant/20 bg-surface-container">
                <th className="text-left px-4 py-3 text-xs font-semibold text-on-surface-variant uppercase tracking-wider">User</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-on-surface-variant uppercase tracking-wider">Role</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-on-surface-variant uppercase tracking-wider hidden md:table-cell">Verified</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-on-surface-variant uppercase tracking-wider hidden lg:table-cell">Joined</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/10">
              {isLoading ? (
                [...Array(8)].map((_, i) => (
                  <tr key={i} className="animate-pulse">
                    <td className="px-4 py-3"><div className="h-4 bg-surface-container rounded w-48" /></td>
                    <td className="px-4 py-3"><div className="h-4 bg-surface-container rounded w-20" /></td>
                    <td className="px-4 py-3 hidden md:table-cell"><div className="h-4 bg-surface-container rounded w-12" /></td>
                    <td className="px-4 py-3 hidden lg:table-cell"><div className="h-4 bg-surface-container rounded w-24" /></td>
                  </tr>
                ))
              ) : users.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-4 py-12 text-center text-on-surface-variant">No users found</td>
                </tr>
              ) : (
                users.map((user: {
                  id: string;
                  full_name: string;
                  email: string;
                  role: string;
                  is_verified: boolean;
                  created_at: string;
                }) => (
                  <tr key={user.id} className="hover:bg-surface-container/50 transition-colors">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-primary-fixed flex items-center justify-center text-primary font-bold text-xs shrink-0">
                          {user.full_name.split(" ").map((n) => n[0]).join("").toUpperCase().slice(0, 2)}
                        </div>
                        <div>
                          <p className="font-medium text-on-surface">{user.full_name}</p>
                          <p className="text-xs text-on-surface-variant">{user.email}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`badge ${getRoleBadgeColor(user.role)}`}>{user.role}</span>
                    </td>
                    <td className="px-4 py-3 hidden md:table-cell">
                      {user.is_verified ? (
                        <span className="material-symbols-outlined text-on-tertiary-container text-sm ms-fill">verified</span>
                      ) : (
                        <span className="material-symbols-outlined text-on-surface-variant text-sm">pending</span>
                      )}
                    </td>
                    <td className="px-4 py-3 hidden lg:table-cell text-xs text-on-surface-variant">
                      {formatDate(user.created_at)}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {total > 20 && (
          <div className="px-4 py-3 border-t border-outline-variant/20 flex justify-between items-center">
            <span className="text-xs text-on-surface-variant">
              Page {page} of {Math.ceil(total / 20)}
            </span>
            <div className="flex gap-2">
              <button disabled={page === 1} onClick={() => setPage((p) => p - 1)}
                className="btn-secondary text-xs px-3 py-1.5 disabled:opacity-50">Previous</button>
              <button disabled={page >= Math.ceil(total / 20)} onClick={() => setPage((p) => p + 1)}
                className="btn-secondary text-xs px-3 py-1.5 disabled:opacity-50">Next</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
