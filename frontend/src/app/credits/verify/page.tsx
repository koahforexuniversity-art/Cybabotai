"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { CheckCircle, XCircle, Loader2 } from "lucide-react";
import { getToken, refreshUser } from "@/lib/auth";

function VerifyContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [message, setMessage] = useState("");
  const [credits, setCredits] = useState<number | null>(null);

  useEffect(() => {
    const reference = searchParams.get("reference") || searchParams.get("trxref");
    if (!reference) {
      setStatus("error");
      setMessage("No payment reference found.");
      return;
    }

    const verify = async () => {
      try {
        const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "/api/backend";
        const res = await fetch(
          `${backendUrl}/api/v1/credits/verify?reference=${reference}`,
          { headers: { Authorization: `Bearer ${getToken()}` } }
        );
        const data = await res.json();

        if (!res.ok) throw new Error(data.detail || "Verification failed");

        await refreshUser();
        setCredits(data.credits);
        setStatus("success");
        setMessage(`${data.credits?.toLocaleString()} credits added to your account!`);

        setTimeout(() => router.push("/builder"), 3000);
      } catch (err) {
        setStatus("error");
        setMessage(err instanceof Error ? err.message : "Verification failed");
      }
    };

    verify();
  }, [searchParams, router]);

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="glass-card p-10 max-w-md w-full text-center"
      >
        {status === "loading" && (
          <>
            <Loader2 className="w-12 h-12 text-cyber-400 animate-spin mx-auto mb-4" />
            <h2 className="text-xl font-bold text-white">Verifying payment...</h2>
            <p className="text-muted-foreground mt-2">Please wait a moment.</p>
          </>
        )}
        {status === "success" && (
          <>
            <CheckCircle className="w-12 h-12 text-emerald-400 mx-auto mb-4" />
            <h2 className="text-xl font-bold text-white">Payment Successful!</h2>
            <p className="text-emerald-400 font-mono text-2xl font-black mt-2">
              +{credits?.toLocaleString()} credits
            </p>
            <p className="text-muted-foreground mt-2">{message}</p>
            <p className="text-xs text-muted-foreground mt-4">Redirecting to builder...</p>
          </>
        )}
        {status === "error" && (
          <>
            <XCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
            <h2 className="text-xl font-bold text-white">Verification Failed</h2>
            <p className="text-muted-foreground mt-2">{message}</p>
            <button
              onClick={() => router.push("/builder")}
              className="mt-6 btn-cyber px-6 py-2 rounded-xl font-semibold text-sm"
            >
              Go to Builder
            </button>
          </>
        )}
      </motion.div>
    </div>
  );
}

export default function VerifyPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-cyber-400" />
      </div>
    }>
      <VerifyContent />
    </Suspense>
  );
}
