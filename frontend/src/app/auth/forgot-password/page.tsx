"use client";
import { useState } from "react";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import toast from "react-hot-toast";
import { authApi } from "@/lib/api";

const schema = z.object({ email: z.string().email() });
type FormData = z.infer<typeof schema>;

export default function ForgotPasswordPage() {
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const { register, handleSubmit, getValues, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const onSubmit = async (data: FormData) => {
    setLoading(true);
    try {
      await authApi.forgotPassword(data.email);
      setSent(true);
    } catch {
      toast.error("Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  if (sent) {
    return (
      <div className="min-h-screen bg-mesh flex items-center justify-center px-5">
        <div className="w-full max-w-sm card text-center space-y-4">
          <div className="w-14 h-14 rounded-2xl bg-tertiary-fixed/30 flex items-center justify-center mx-auto">
            <span className="material-symbols-outlined text-3xl text-on-tertiary-container ms-fill">mark_email_read</span>
          </div>
          <h2 className="text-xl font-bold font-headline text-primary">Check your email</h2>
          <p className="text-sm text-on-surface-variant">
            We sent a reset link to <span className="font-semibold text-on-surface">{getValues("email")}</span>.
            Check your inbox and follow the link.
          </p>
          <Link href="/auth/login" className="btn-primary inline-flex items-center gap-2">
            <span className="material-symbols-outlined text-sm">arrow_back</span> Back to Sign In
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-mesh flex items-center justify-center px-5 py-12">
      <div className="w-full max-w-sm space-y-8">
        <div className="text-center space-y-2">
          <div className="w-14 h-14 rounded-2xl bg-primary-container flex items-center justify-center mx-auto">
            <span className="material-symbols-outlined text-3xl text-on-primary ms-fill">lock_reset</span>
          </div>
          <h1 className="text-2xl font-extrabold text-primary font-headline">Reset Password</h1>
          <p className="text-sm text-on-surface-variant">Enter your email to receive a reset link</p>
        </div>

        <div className="card space-y-4">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-sm font-medium text-on-surface">Email address</label>
              <input {...register("email")} type="email" className="input-field" placeholder="you@example.com" />
              {errors.email && <p className="text-xs text-error">{errors.email.message}</p>}
            </div>
            <button type="submit" disabled={loading} className="btn-primary w-full flex items-center justify-center gap-2">
              {loading ? (
                <><div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Sending...</>
              ) : (
                "Send Reset Link"
              )}
            </button>
          </form>
          <div className="text-center">
            <Link href="/auth/login" className="text-sm text-secondary font-semibold hover:underline flex items-center justify-center gap-1">
              <span className="material-symbols-outlined text-sm">arrow_back</span> Back to Sign In
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
