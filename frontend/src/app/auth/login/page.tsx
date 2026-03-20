"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import toast from "react-hot-toast";
import { authApi } from "@/lib/api";
import { saveTokens, saveUser, getRedirectPath } from "@/lib/auth";
import { useAuthStore } from "@/lib/store";

const schema = z.object({
  email: z.string().email("Enter a valid email"),
  password: z.string().min(6, "Password must be at least 6 characters"),
});
type FormData = z.infer<typeof schema>;

export default function LoginPage() {
  const router = useRouter();
  const setUser = useAuthStore((s) => s.setUser);
  const [loading, setLoading] = useState(false);
  const [showPass, setShowPass] = useState(false);

  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const onSubmit = async (data: FormData) => {
    setLoading(true);
    try {
      const res = await authApi.login(data);
      const { access_token, refresh_token, user } = res.data;
      saveTokens(access_token, refresh_token);
      saveUser(user);
      setUser(user);
      toast.success(`Welcome back, ${user.full_name.split(" ")[0]}!`);
      router.push(getRedirectPath(user.role));
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } }).response?.data?.detail || "Login failed. Please try again.";
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-mesh flex items-center justify-center px-5 py-12">
      <div className="w-full max-w-sm space-y-8">
        {/* Logo */}
        <div className="text-center space-y-3">
          <div className="w-14 h-14 rounded-2xl bg-primary-container flex items-center justify-center mx-auto">
            <span className="material-symbols-outlined text-3xl text-on-primary ms-fill">
              clinical_notes
            </span>
          </div>
          <div>
            <h1 className="text-2xl font-extrabold text-primary font-headline tracking-tight">
              CareCopilot AI
            </h1>
            <p className="text-sm text-on-surface-variant mt-1">
              Sign in to your health command center
            </p>
          </div>
        </div>

        {/* Form card */}
        <div className="card space-y-5">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-sm font-medium text-on-surface">Email</label>
              <input
                {...register("email")}
                type="email"
                className="input-field"
                placeholder="you@example.com"
                autoComplete="email"
              />
              {errors.email && (
                <p className="text-xs text-error">{errors.email.message}</p>
              )}
            </div>

            <div className="space-y-1.5">
              <div className="flex justify-between items-center">
                <label className="text-sm font-medium text-on-surface">Password</label>
                <Link
                  href="/auth/forgot-password"
                  className="text-xs text-secondary font-semibold hover:underline"
                >
                  Forgot password?
                </Link>
              </div>
              <div className="relative">
                <input
                  {...register("password")}
                  type={showPass ? "text" : "password"}
                  className="input-field pr-10"
                  placeholder="••••••••"
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPass(!showPass)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-on-surface-variant hover:text-on-surface"
                >
                  <span className="material-symbols-outlined text-sm">
                    {showPass ? "visibility_off" : "visibility"}
                  </span>
                </button>
              </div>
              {errors.password && (
                <p className="text-xs text-error">{errors.password.message}</p>
              )}
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Signing in...
                </>
              ) : (
                <>
                  <span className="material-symbols-outlined text-sm">login</span>
                  Sign In
                </>
              )}
            </button>
          </form>

          <div className="text-center text-sm text-on-surface-variant">
            Don&apos;t have an account?{" "}
            <Link href="/auth/register" className="text-secondary font-semibold hover:underline">
              Create account
            </Link>
          </div>
        </div>

        {/* Trust indicator */}
        <div className="flex items-center justify-center gap-2 text-xs text-on-surface-variant">
          <span className="material-symbols-outlined text-on-tertiary-container text-sm ms-fill">
            verified_user
          </span>
          <span className="font-medium">HIPAA-aligned · End-to-end encrypted</span>
        </div>
      </div>
    </div>
  );
}
