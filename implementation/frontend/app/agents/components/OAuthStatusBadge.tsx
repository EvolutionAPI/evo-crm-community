/**
 * OAuth Status Badge component.
 *
 * New file — add to: evo-ai-frontend-community/app/agents/components/OAuthStatusBadge.tsx
 *
 * Compact badge showing OAuth connection status for API key list items.
 * Green = connected, Red = disconnected/expired.
 */
"use client";

import { useState, useEffect } from "react";
import { RefreshCw } from "lucide-react";
import { getOAuthStatus } from "@/services/agentService";

interface OAuthStatusBadgeProps {
  keyId: string;
  clientId: string;
}

export function OAuthStatusBadge({ keyId, clientId }: OAuthStatusBadgeProps) {
  const [connected, setConnected] = useState<boolean | null>(null);
  const [planType, setPlanType] = useState<string | null>(null);
  const [expiresAt, setExpiresAt] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchStatus = async () => {
    setLoading(true);
    try {
      const res = await getOAuthStatus(keyId, clientId);
      const data = res.data;
      setConnected(data.connected);
      setPlanType(data.plan_type || null);
      setExpiresAt(data.expires_at || null);
    } catch {
      setConnected(false);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, [keyId, clientId]);

  const getExpiryLabel = () => {
    if (!expiresAt) return null;
    const exp = new Date(expiresAt);
    const now = new Date();
    const hoursLeft = Math.floor((exp.getTime() - now.getTime()) / (1000 * 60 * 60));
    if (hoursLeft < 0) return "Expired";
    if (hoursLeft < 24) return `${hoursLeft}h left`;
    return null;
  };

  if (loading) {
    return (
      <span className="inline-flex items-center gap-1 text-xs text-gray-500">
        <RefreshCw className="h-3 w-3 animate-spin" />
        Checking...
      </span>
    );
  }

  if (connected) {
    const expiryLabel = getExpiryLabel();
    return (
      <span className="inline-flex items-center gap-1.5">
        <span className="inline-flex items-center gap-1 rounded-full bg-emerald-400/10 px-2 py-0.5 text-xs font-medium text-emerald-400">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
          Connected
        </span>
        {planType && (
          <span className="rounded-full bg-[#333] px-2 py-0.5 text-xs text-gray-400">
            {planType === "plus" ? "Plus" : planType === "pro" ? "Pro" : planType}
          </span>
        )}
        {expiryLabel && (
          <span className="text-xs text-yellow-400">{expiryLabel}</span>
        )}
        <button
          onClick={(e) => {
            e.stopPropagation();
            fetchStatus();
          }}
          className="text-gray-500 transition-colors hover:text-gray-300"
          title="Refresh status"
        >
          <RefreshCw className="h-3 w-3" />
        </button>
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1 rounded-full bg-red-400/10 px-2 py-0.5 text-xs font-medium text-red-400">
      <span className="h-1.5 w-1.5 rounded-full bg-red-400" />
      Disconnected
    </span>
  );
}
