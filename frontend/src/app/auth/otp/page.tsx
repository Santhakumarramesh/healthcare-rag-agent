"use client";
import { useState, useRef, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import toast from "react-hot-toast";
import { authApi } from "@/lib/api";

function OTPContent() {
  const router = useRouter();
  const params = useSearchParams();
  const email = params.get("email") || "";
  const [otp, setOtp] = useState(["", "", "", "", "", ""]);
  const [loading, setLoading] = useState(false);
  const [resending, setResending] = useState(false);
  const [countdown, setCountdown] = useState(60);
  const inputs = useRef<(HTMLInputElement | null)[]>([]);

  useEffect(() => {
    if (countdown > 0) {
      const t = setTimeout(() => setCountdown((c) => c - 1), 1000);
      return () => clearTimeout(t);
    }
  }, [countdown]);

  const handleChange = (i: number, val: string) => {
    if (!/^[0-9]?$/.test(val)) return;
    const next = [...otp];
    next[i] = val;
    setOtp(next);
    if (val && i < 5) inputs.current[i + 1]?.focus();
  };

  const handleKeyDown = (i: number, e: React.KeyboardEvent) => {
    if (e.key === "Backspace" && !otp[i] && i > 0) inputs.current[i - 1]?.focus();
  };

  const handlePaste = (e: React.ClipboardEvent) => {
    const text = e.clipboardData.getData("text").replace(/\D/g, "").slice(0, 6);
    if (text.length === 6) {
      setOtp(text.split(""));
      inputs.current[5]?.focus();
    }
  };

  const handleVerify = async () => {
    const code = otp.join("");
    if (code.length < 6) return toast.error("Enter the full 6-digit code");
    setLoading(true);
    try {
      await authApi.verifyOtp({ email, otp: code });
      toast.success("Email verified! Please sign in.");
      router.push("/auth/login");
    } catch {
      toast.error("Invalid or expired code. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleResend = async () => {
    setResending(true);
    try {
      await authApi.sendOtp({ email });
      toast.success("New code sent to your email");
      setCountdown(60);
      setOtp(["", "", "", "", "", ""]);
      inputs.current[0]?.focus();
    } catch {
      toast.error("Failed to resend. Please try again.");
    } finally {
      setResending(false);
    }
  };

  return (
    <div className="min-h-screen bg-mesh flex items-center justify-center px-5 py-12">
      <div className="w-full max-w-sm space-y-8">
        <div className="text-center space-y-2">
          <div className="w-14 h-14 rounded-2xl bg-secondary-fixed flex items-center justify-center mx-auto">
            <span className="material-symbols-outlined text-3xl text-on-secondary-container ms-fill">mark_email_read</span>
          </div>
          <h1 className="text-2xl font-extrabold text-primary font-headline">Verify Your Email</h1>
          <p className="text-sm text-on-surface-variant">
            We sent a 6-digit code to<br />
            <span className="font-semibold text-on-surface">{email}</span>
          </p>
        </div>

        <div className="card space-y-6">
          <div className="flex justify-center gap-3" onPaste={handlePaste}>
            {otp.map((digit, i) => (
              <input
                key={i}
                ref={(el) => { inputs.current[i] = el; }}
                type="text"
                inputMode="numeric"
                maxLength={1}
                value={digit}
                onChange={(e) => handleChange(i, e.target.value)}
                onKeyDown={(e) => handleKeyDown(i, e)}
                className={`w-12 h-14 text-center text-xl font-bold rounded-xl border-2 bg-surface-container-lowest focus:outline-none transition-all ${
                  digit ? "border-primary bg-primary-fixed/10" : "border-outline-variant focus:border-primary"
                }`}
              />
            ))}
          </div>

          <button
            onClick={handleVerify}
            disabled={loading || otp.join("").length < 6}
            className="btn-primary w-full flex items-center justify-center gap-2"
          >
            {loading ? (
              <><div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Verifying...</>
            ) : (
              <><span className="material-symbols-outlined text-sm">verified</span> Verify Email</>
            )}
          </button>

          <div className="text-center text-sm text-on-surface-variant">
            {countdown > 0 ? (
              <span>Resend code in <span className="font-semibold text-on-surface">{countdown}s</span></span>
            ) : (
              <button onClick={handleResend} disabled={resending} className="text-secondary font-semibold hover:underline">
                {resending ? "Sending..." : "Resend code"}
              </button>
            )}
          </div>
        </div>

        <div className="text-center">
          <Link href="/auth/login" className="text-sm text-on-surface-variant hover:text-on-surface flex items-center justify-center gap-1">
            <span className="material-symbols-outlined text-sm">arrow_back</span> Back to Sign In
          </Link>
        </div>
      </div>
    </div>
  );
}

export default function OTPPage() {
  return (
    <Suspense>
      <OTPContent />
    </Suspense>
  );
}
