import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(date: string | Date, format = "short"): string {
  const d = new Date(date);
  if (format === "short") return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
  if (format === "time") return d.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" });
  if (format === "full") return d.toLocaleString("en-US", { month: "long", day: "numeric", year: "numeric", hour: "2-digit", minute: "2-digit" });
  return d.toLocaleDateString();
}

export function formatRelative(date: string | Date): string {
  const d = new Date(date);
  const now = new Date();
  const diff = now.getTime() - d.getTime();
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);
  if (minutes < 1) return "just now";
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  if (days < 7) return `${days}d ago`;
  return formatDate(date, "short");
}

export function capitalize(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

export function getInitials(name: string): string {
  return name.split(" ").map((n) => n[0]).join("").toUpperCase().slice(0, 2);
}

export function getRoleBadgeColor(role: string): string {
  const map: Record<string, string> = {
    superadmin: "bg-purple-100 text-purple-800",
    admin: "bg-primary-fixed text-primary",
    doctor: "bg-secondary-fixed text-on-secondary-container",
    pharmacist: "bg-tertiary-fixed/30 text-on-tertiary-container",
    patient: "bg-surface-container text-on-surface-variant",
    caregiver: "bg-amber-100 text-amber-800",
    support: "bg-blue-100 text-blue-800",
  };
  return map[role] || "bg-surface-container text-on-surface-variant";
}

export function getStatusColor(status: string): string {
  const map: Record<string, string> = {
    active: "badge-success",
    completed: "badge-info",
    pending: "badge-warning",
    cancelled: "badge-gray",
    failed: "badge-error",
    processing: "badge-info",
  };
  return map[status.toLowerCase()] || "badge-gray";
}
