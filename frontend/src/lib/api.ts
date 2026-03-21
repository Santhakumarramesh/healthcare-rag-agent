import axios from "axios";
import Cookies from "js-cookie";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_URL,
  headers: { "Content-Type": "application/json" },
  timeout: 30_000,
});

// Attach access token to every request
api.interceptors.request.use((config) => {
  const token = Cookies.get("access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Refresh token on 401
api.interceptors.response.use(
  (res) => res,
  async (err) => {
    const original = err.config;
    if (err.response?.status === 401 && !original._retry) {
      original._retry = true;
      const refresh = Cookies.get("refresh_token");
      if (refresh) {
        try {
          const { data } = await axios.post(`${API_URL}/auth/refresh`, {
            refresh_token: refresh,
          });
          // Backend returns { access_token, refresh_token, token_type, user }
          const newToken = data.access_token;
          Cookies.set("access_token", newToken, { expires: 1 });
          original.headers.Authorization = `Bearer ${newToken}`;
          return api(original);
        } catch {
          Cookies.remove("access_token");
          Cookies.remove("refresh_token");
          window.location.href = "/auth/login";
        }
      }
    }
    return Promise.reject(err);
  }
);

// ── Auth ──────────────────────────────────────────────────────────────────────
export const authApi = {
  register: (data: RegisterPayload) => api.post("/auth/register", data),
  login: (data: LoginPayload) => api.post<AuthResponse>("/auth/login", data),
  sendOtp: (data: { email: string }) => api.post("/auth/send-otp", data),
  verifyOtp: (data: { email: string; otp: string }) => api.post("/auth/verify-otp", data),
  forgotPassword: (email: string) => api.post("/auth/forgot-password", { email }),
  resetPassword: (data: ResetPayload) => api.post("/auth/reset-password", data),
  me: () => api.get<UserResponse>("/auth/me"),
  logout: () => api.post("/auth/logout"),
};

// ── Patient ───────────────────────────────────────────────────────────────────
export const patientApi = {
  getDashboard: () => api.get("/patients/dashboard"),
  getProfile: () => api.get("/patients/profile"),
  updateProfile: (data: object) => api.put("/patients/profile", data),
};

// ── Reports ───────────────────────────────────────────────────────────────────
export const reportsApi = {
  upload: (form: FormData) =>
    api.post("/reports/upload", form, { headers: { "Content-Type": "multipart/form-data" } }),
  list: (params?: object) => api.get("/reports", { params }),
  get: (id: string) => api.get(`/reports/${id}`),
  analyze: (id: string) => api.post(`/reports/${id}/analyze`),
};

// ── Tracking ──────────────────────────────────────────────────────────────────
export const trackingApi = {
  logSymptom: (data: object) => api.post("/tracking/symptoms", data),
  logMedication: (data: object) => api.post("/tracking/medications", data),
  logHydration: (data: object) => api.post("/tracking/hydration", data),
  logVitals: (data: object) => api.post("/tracking/vitals", data),
  logSleep: (data: object) => api.post("/tracking/sleep", data),
  getSummary: () => api.get("/tracking/summary"),
  getTrends: (metric: string, days: number) =>
    api.get(`/tracking/trends/${metric}?days=${days}`),
};

// ── Prescriptions ─────────────────────────────────────────────────────────────
export const prescriptionsApi = {
  list: () => api.get("/prescriptions"),
  get: (id: string) => api.get(`/prescriptions/${id}`),
  requestRefill: (id: string) => api.post(`/prescriptions/${id}/refill`),
  getOrders: () => api.get("/prescriptions/orders"),
  trackOrder: (id: string) => api.get(`/prescriptions/orders/${id}/track`),
};

// ── Insurance ─────────────────────────────────────────────────────────────────
export const insuranceApi = {
  get: () => api.get("/insurance"),
  create: (data: object) => api.post("/insurance", data),
  update: (id: string, data: object) => api.put(`/insurance/${id}`, data),
  verify: (id: string) => api.post(`/insurance/${id}/verify`),
  snapshot: () => api.get("/insurance/snapshot"),
};

// ── Consultations ─────────────────────────────────────────────────────────────
export const consultationsApi = {
  book: (data: object) => api.post("/consultations/book", data),
  list: (params?: object) => api.get("/consultations", { params }),
  get: (id: string) => api.get(`/consultations/${id}`),
  sendMessage: (id: string, message: string) =>
    api.post(`/consultations/${id}/messages`, { message }),
  complete: (id: string, notes: string) =>
    api.post(`/consultations/${id}/complete`, { clinical_notes: notes }),
};

// ── Doctors ───────────────────────────────────────────────────────────────────
export const doctorsApi = {
  search: (params: object) => api.get("/doctors/search", { params }),
  getProfile: () => api.get("/doctors/profile"),
  updateProfile: (data: object) => api.put("/doctors/profile", data),
  getAvailability: () => api.get("/doctors/availability"),
  setAvailability: (data: object) => api.post("/doctors/availability", data),
  getPatientQueue: () => api.get("/doctors/patients/queue"),
};

// ── AI ────────────────────────────────────────────────────────────────────────
export const aiApi = {
  chat: (message: string, conversationId?: string) =>
    api.post("/reports/chat", { message, conversation_id: conversationId }),
  getInsights: () => api.get("/patients/insights"),
};

// ── Admin ─────────────────────────────────────────────────────────────────────
export const adminApi = {
  getDashboard: () => api.get("/admin/dashboard"),
  getUsers: (params?: object) => api.get("/admin/users", { params }),
  getJobs: (params?: object) => api.get("/admin/jobs", { params }),
  retryJob: (id: string) => api.post(`/admin/jobs/${id}/retry`),
  getAlerts: () => api.get("/admin/alerts"),
  resolveAlert: (id: string) => api.post(`/admin/alerts/${id}/resolve`),
  getDoctorApprovals: () => api.get("/admin/doctor-approvals"),
  approveDoctor: (id: string) => api.post(`/admin/doctor-approvals/${id}/approve`),
  getAuditLogs: (params?: object) => api.get("/admin/audit-logs", { params }),
};

// ── Types ─────────────────────────────────────────────────────────────────────
export interface RegisterPayload {
  full_name: string;
  email: string;
  password: string;
  role?: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface ResetPayload {
  token: string;
  new_password: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: UserResponse;
}

export interface UserResponse {
  id: string;
  full_name: string;
  email: string;
  role: string;
  is_verified: boolean;
  created_at: string;
}
