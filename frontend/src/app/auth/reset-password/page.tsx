"use client";
import { useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import toast from "react-hot-toast";
import { authApi } from "@/lib/api";

const schema = z.object({
  new_password: z
    .string()
    .min(8, "At least 8 characters")
    .regex(/[A-Z]/, "Must include an uppercase letter")
    .regex(/[0-9]/, "Must include a number"),
  confirm_password: z.string(),
}).refine((d) => d.new_password === d.confirm_password, {
  path: ["confirm_password"],
  message: "Passwords don't match",
});
type FormData = z.infer<typeof schema>;

function ResetPasswordForm() {
  const router = useRouter();
  const params = useSearchParams();
  const token = params.get("token") ?? "";
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);
  const [showPass, setShowPass] = useState(false);

  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const onSubmit = async (data: FormData) => {
    if (!token) {
      toast.error("Invalid reset link. Please request a new one.");
      return;
    }
    setLoading(true);
    try {
      await authApi.resetPassword({ token, new_password: data.new_password });
      setDone(true);
      toast.success("Password reset successfully!");
      setTimeout(() => router.push("/auth/login"), 2000);
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
        ?? "Reset failed. The link may have expired.";
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  if (done) {
    return (
      <div className="text-center space-y-4">
        <div className="w-16 h-16 rounded-full bg-on-tertiary-container/10 flex items-center justify-center mx-auto">
          <span className="material-symbols-outlined text-3xl text-on-tertiary-container ms-fill">check_circle</span>
        </div>
        <h2 className="text-xl font-bold text-on-surface">Password updated!</h2>
        <p className="text-sm text-on-surface-variant">Redirecting you to sign in…</p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
      {/* New password */}
      <div className="space-y-1">
        <label className="text-sm font-medium text-on-surface">New password</label>
        <div className="relative">
          <input
            type={showPass ? "text" : "password"}
            placeholder="Min 8 chars, 1 uppercase, 1 number"
            {...register("new_password")}
            className="w-full bg-surface-container rounded-xl px-4 py-3 pr-11 text-on-surface placeholder:text-on-surface-variant text-sm focus:outline-none focus:ring-2 focus:ring-primary/40"
          />
          <button
            type="button"
            onClick={() => setShowPass((v) => !v)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-on-surface-variant"
          >
            <span className="material-symbols-outlined text-sm">{showPass ? "visibility_off" : "visibility"}</span>
          </button>
        </div>
        {errors.new_password && (
          <p className="text-xs text-error">{errors.new_password.message}</p>
        )}
      </div>

      {/* Confirm password */}
      <div className="space-y-1">
        <label className="text-sm font-medium text-on-surface">Confirm password</label>
        <input
          type={showPass ? "text" : "password"}
          placeholder="Re-enter your new password"
          {...register("confirm_password")}
          className="w-full bg-surface-container rounded-xl px-4 py-3 text-on-surface placeholder:text-on-surface-variant text-sm focus:outline-none focus:ring-2 focus:ring-primary/40"
        />
        {errors.confirm_password && (
          <p className="text-xs text-error">{errors.confirm_password.message}</p>
        )}
      </div>

      <button type="submit" disabled={loading} className="btn-primary w-full">
        {loading ? "Resetting…" : "Reset Password"}
      </button>
    </form>
  );
}

export default function ResetPasswordPage() {
  return (
    <div className="min-h-screen bg-mesh flex items-center justify-center px-5 py-12">
      <div className="w-full max-w-sm space-y-8">
        {/* Logo */}
        <div className="text-center space-y-2">
          <div className="w-14 h-14 rounded-2xl bg-primary-container flex items-center justify-center mx-auto">
            <span className="material-symbols-outlined text-3xl text-on-primary ms-fill">lock_reset</span>
          </div>
          <h1 className="text-2xl font-extrabold text-primary font-headline tracking-tight">
            Reset your password
          </h1>
          <p className="text-sm text-on-surface-variant">Enter a new strong password below</p>
        </div>

        <div className="card">
          <Suspense fallback={<div className="animate-pulse h-40 bg-surface-container rounded-xl" />}>
            <ResetPasswordForm />
          </Suspense>
        </div>

        <p className="text-center text-sm text-on-surface-variant">
          Remembered it?{" "}
          <Link href="/auth/login" className="text-primary font-semibold hover:underline">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
