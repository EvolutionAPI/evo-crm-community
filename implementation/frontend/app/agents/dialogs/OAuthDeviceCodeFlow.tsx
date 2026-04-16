/**
 * OAuth Device Code Flow component.
 *
 * New file — add to: evo-ai-frontend-community/app/agents/dialogs/OAuthDeviceCodeFlow.tsx
 *
 * Manages the full device code lifecycle:
 * 1. Calls initiateOAuthDeviceCode to get user_code
 * 2. Displays code + verification URL for user
 * 3. Polls backend at interval for authorization
 * 4. Shows success/error/expired states
 */
"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Copy, CheckCircle, XCircle, Loader2, ExternalLink } from "lucide-react";
import { initiateOAuthDeviceCode, pollOAuthDeviceCode } from "@/services/agentService";

interface OAuthDeviceCodeFlowProps {
  clientId: string;
  name: string;
  onSuccess: (keyId: string) => void;
  onCancel: () => void;
}

type FlowState = "loading" | "waiting" | "complete" | "expired" | "error";

export function OAuthDeviceCodeFlow({
  clientId,
  name,
  onSuccess,
  onCancel,
}: OAuthDeviceCodeFlowProps) {
  const [state, setState] = useState<FlowState>("loading");
  const [userCode, setUserCode] = useState("");
  const [verificationUri, setVerificationUri] = useState("");
  const [keyId, setKeyId] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [copied, setCopied] = useState(false);
  const [secondsLeft, setSecondsLeft] = useState(0);

  const pollIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const countdownRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const cleanup = useCallback(() => {
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
      pollIntervalRef.current = null;
    }
    if (countdownRef.current) {
      clearInterval(countdownRef.current);
      countdownRef.current = null;
    }
  }, []);

  // Initiate device code flow on mount
  useEffect(() => {
    let cancelled = false;

    async function initiate() {
      try {
        const res = await initiateOAuthDeviceCode(clientId, name);
        if (cancelled) return;

        const data = res.data;
        setUserCode(data.user_code);
        setVerificationUri(data.verification_uri);
        setKeyId(data.key_id);
        setSecondsLeft(data.expires_in);
        setState("waiting");

        // Start polling
        const interval = Math.max(data.interval, 5) * 1000;
        pollIntervalRef.current = setInterval(async () => {
          try {
            const pollRes = await pollOAuthDeviceCode(data.key_id);
            const pollData = pollRes.data;

            if (pollData.status === "complete") {
              cleanup();
              setState("complete");
              onSuccess(data.key_id);
            } else if (pollData.status === "expired") {
              cleanup();
              setState("expired");
              setErrorMessage("Device code expired. Please try again.");
            } else if (pollData.status === "error") {
              cleanup();
              setState("error");
              setErrorMessage(pollData.message || "Authentication failed.");
            }
            // "pending" -> keep polling
          } catch {
            // Network error during poll — keep trying
          }
        }, interval);

        // Start countdown timer
        countdownRef.current = setInterval(() => {
          setSecondsLeft((prev) => {
            if (prev <= 1) {
              cleanup();
              setState("expired");
              setErrorMessage("Device code expired. Please try again.");
              return 0;
            }
            return prev - 1;
          });
        }, 1000);
      } catch (err: any) {
        if (cancelled) return;
        setState("error");
        setErrorMessage(err?.response?.data?.detail || "Failed to start OAuth flow.");
      }
    }

    initiate();

    return () => {
      cancelled = true;
      cleanup();
    };
  }, [clientId, name, cleanup, onSuccess]);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(userCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s.toString().padStart(2, "0")}`;
  };

  // --- Loading state ---
  if (state === "loading") {
    return (
      <div className="flex flex-col items-center gap-4 py-8">
        <Loader2 className="h-8 w-8 animate-spin text-emerald-400" />
        <p className="text-sm text-gray-400">Initiating OAuth connection...</p>
      </div>
    );
  }

  // --- Success state ---
  if (state === "complete") {
    return (
      <div className="flex flex-col items-center gap-4 py-8">
        <CheckCircle className="h-12 w-12 text-emerald-400" />
        <p className="text-lg font-medium text-white">Connected!</p>
        <p className="text-sm text-gray-400">
          Your ChatGPT subscription is now linked.
        </p>
      </div>
    );
  }

  // --- Error state ---
  if (state === "error") {
    return (
      <div className="flex flex-col items-center gap-4 py-8">
        <XCircle className="h-12 w-12 text-red-400" />
        <p className="text-sm text-red-400">{errorMessage}</p>
        <Button
          onClick={onCancel}
          variant="outline"
          className="border-[#444] bg-[#222] text-white hover:bg-[#333]"
        >
          Close
        </Button>
      </div>
    );
  }

  // --- Expired state ---
  if (state === "expired") {
    return (
      <div className="flex flex-col items-center gap-4 py-8">
        <XCircle className="h-12 w-12 text-yellow-400" />
        <p className="text-sm text-yellow-400">{errorMessage}</p>
        <Button
          onClick={onCancel}
          variant="outline"
          className="border-[#444] bg-[#222] text-white hover:bg-[#333]"
        >
          Try Again
        </Button>
      </div>
    );
  }

  // --- Waiting state (main UI) ---
  return (
    <div className="flex flex-col items-center gap-6 py-4">
      <p className="text-sm text-gray-400 text-center">
        Visit the link below and enter this code to connect your ChatGPT subscription:
      </p>

      {/* User code display */}
      <div className="flex items-center gap-3">
        <span className="rounded-lg border border-emerald-400/30 bg-[#1a1a1a] px-6 py-3 font-mono text-2xl font-bold tracking-widest text-emerald-400">
          {userCode}
        </span>
        <Button
          size="icon"
          variant="ghost"
          onClick={handleCopy}
          className="text-gray-400 hover:text-emerald-400"
        >
          {copied ? (
            <CheckCircle className="h-5 w-5 text-emerald-400" />
          ) : (
            <Copy className="h-5 w-5" />
          )}
        </Button>
      </div>

      {/* Verification link */}
      <a
        href={verificationUri}
        target="_blank"
        rel="noopener noreferrer"
        className="inline-flex items-center gap-2 rounded-md border border-emerald-400/30 bg-emerald-400/10 px-4 py-2 text-sm text-emerald-400 transition-colors hover:bg-emerald-400/20"
      >
        <ExternalLink className="h-4 w-4" />
        Open {verificationUri}
      </a>

      {/* Polling indicator */}
      <div className="flex items-center gap-2 text-sm text-gray-500">
        <Loader2 className="h-4 w-4 animate-spin" />
        <span>Waiting for authorization... ({formatTime(secondsLeft)})</span>
      </div>

      {/* Cancel button */}
      <Button
        onClick={() => {
          cleanup();
          onCancel();
        }}
        variant="ghost"
        className="text-gray-500 hover:text-gray-300"
      >
        Cancel
      </Button>
    </div>
  );
}
