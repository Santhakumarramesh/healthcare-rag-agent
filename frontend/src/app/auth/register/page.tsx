"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import toast from "react-hot-toast";
import { authApi } from "@/lib/api";

const schema = z.object({
  full_name: z.string().min(2, "Name must be at least 2 characters"),
  email: z.string().email("Enter a valid email"),
  password: z.string().min(8, "Password must be at least 8 characters"),
  role: z.enum(["patient", "doctor", "caregiver"]),
});
type FormData = z.infer<typeof schema>;

const ROLES = [
  { value: "patient", label: "Patient", icon: "person", desc: "Access your health records & AI insights" },
  { value: "doctor", label: "Doctor / Provider", icon: "stethoscope", desc: "Manage patients & consultations" },
  { value: "caregiver", label: "Caregiver", icon: "supervisor_account", desc: "Support a family member's care" },
];

export default function RegisterPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [showPass, setShowPass] = useState(false);

  const { register, handleSubmit, watch, setValue, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { role: "patient" },
  });

  const selectedRole = watch("role");

  const onSubmit = async (data: FormData) => {
    setLoading(true);
    try {
      await authApi.register(data);
      toast.success("Account created! Check your email to verify.");
      router.push(`/auth/otp?email=${encodeURIComponent(data.email)}`);
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } }).response?.data?.detail || "Registration failed. Please try again.";
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-mesh flex items-center justify-center px-5 py-12">
      <div className="w-full max-w-sm space-y-8">
        {/* Logo */}
        <div className="text-center space-y-2">
          <div className="w-14 h-14 rounded-2xl bg-primary-container flex items-center justify-center mx-auto">
            <span className="material-symbols-outlined text-3xl text-on-primary ms-fill">clinical_notes</span>
          </div>
          <h1 className="text-2xl font-extrabold text-primary font-headline tracking-tight">Create your account</h1>
          <p className="text-sm text-on-surface-variant">Join CareCopilot AI — your care command center</p>
        </div>

        <div className="card space-y-5">
          {/* Role selector */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-on-surface">I am a…</label>
            <div className="grid grid-cols-1 gap-2">
              {ROLES.map((r) => (
                <button
                  key={r.value}
                  type="button"
                  onClick={() => setValue("role", r.value as FormData["role"])}
                  className={`flex items-center gap-3 p-3 rounded-xl border text-left transition-all ${
                    selectedRole === r.value
                      ? "border-primary bg-primary-fixed/20"
                      : "border-outline-variant hover:bg-surface-container"
                  }`}
                >
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                    selectedRole === r.value ? "bg-primary text-white" : "bg-surface-container text-on-surface-variant"
                  }`}>
                    <span className="material-symbols-outlined text-sm">{r.icon}</span>
                  </div>
                  <div>
                    <p className={`text-sm font-semibold ${selectedRole === r.value ? "text-primary" : "text-on-surface"}`}>
                      {r.label}
                    </p>
                    <p className="text-xs text-on-surface-variant">{r.desc}</p>
                  </div>
                  {selectedRole === r.value && (
                    <span className="material-symbols-outlined text-primary ml-auto text-sm ms-fill">check_circle</span>
                  )}
                </button>
              ))}
            </div>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-sm font-medium text-on-surface">Full Name</label>
              <input {...register("full_name")} className="input-field" placeholder="Dr. Jane Smith" />
              {errors.full_name && <p className="text-xs text-error">{errors.full_name.message}</p>}
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium text-on-surface">Email</label>
              <input {...register("email")} type="email" className="input-field" placeholder="you@example.com" />
              {errors.email && <p className="text-xs text-error">{errors.email.message}</p>}
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium text-on-surface">Password</label>
              <div className="relative">
                <input
                  {...register("password")}
                  type={showPass ? "text" : "password"}
                  className="input-field pr-10"
                  placeholder="At least 8 characters"
                />
                <button type="button" onClick={() => setShowPass(!showPass)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-on-surface-variant">
                  <span className="material-symbols-outlined text-sm">{showPass ? "visibility_off" : "visibility"}</span>
                </button>
              </div>
              {errors.password && <p className="text-xs text-error">{errors.password.message}</p>}
            </div>

            <button type="submit" disabled={loading} className="btn-primary w-full flex items-center justify-center gap-2">
              {loading ? (
                <><div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Creating account...</>
              ) : (
                <><span className="material-symbols-outlined text-sm">person_add</span> Create Account</>
              )}
            </button>
          </form>

          <p className="text-center text-sm text-on-surface-variant">
            Already have an account?{" "}
            <Link href="/auth/login" className="text-secondary font-semibold hover:underline">Sign in</Link>
          </p>
        </div>

        <div className="flex items-center justify-center gap-2 text-xs text-on-surface-variant">
          <span className="material-symbols-outlined text-on-tertiary-container text-sm ms-fill">verified_user</span>
          <span className="font-medium">HIPAA-aligned · Privacy-first platform</span>
        </div>
      </div>
    </div>
  );
}
