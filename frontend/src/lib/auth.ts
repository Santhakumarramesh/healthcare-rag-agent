import Cookies from "js-cookie";
import { UserResponse } from "./api";

const COOKIE_OPTS = { expires: 1, sameSite: "strict" as const };
const REFRESH_OPTS = { expires: 30, sameSite: "strict" as const };

export function saveTokens(accessToken: string, refreshToken: string) {
  Cookies.set("access_token", accessToken, COOKIE_OPTS);
  Cookies.set("refresh_token", refreshToken, REFRESH_OPTS);
}

export function clearTokens() {
  Cookies.remove("access_token");
  Cookies.remove("refresh_token");
  Cookies.remove("user_role");
}

export function saveUser(user: UserResponse) {
  Cookies.set("user_role", user.role, COOKIE_OPTS);
  if (typeof window !== "undefined") {
    localStorage.setItem("cc_user", JSON.stringify(user));
  }
}

export function getUser(): UserResponse | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem("cc_user");
  if (!raw) return null;
  try { return JSON.parse(raw); } catch { return null; }
}

export function clearUser() {
  if (typeof window !== "undefined") {
    localStorage.removeItem("cc_user");
  }
}

export function getRedirectPath(role: string): string {
  switch (role) {
    case "admin":
    case "superadmin": return "/admin/dashboard";
    case "doctor":      return "/doctor/dashboard";
    case "caregiver":   return "/caregiver/dashboard";
    default:            return "/patient/dashboard";
  }
}

export function isAuthenticated(): boolean {
  return !!Cookies.get("access_token");
}
