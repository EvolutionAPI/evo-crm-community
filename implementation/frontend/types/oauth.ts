/**
 * OAuth Codex (OpenAI) TypeScript types.
 *
 * New file — add to: evo-ai-frontend-community/types/oauth.ts
 */

export interface OAuthDeviceCodeResponse {
  user_code: string;
  verification_uri: string;
  expires_in: number;
  interval: number;
  key_id: string;
}

export interface OAuthPollResponse {
  status: "pending" | "complete" | "expired" | "error";
  key_id?: string;
  message?: string;
}

export interface OAuthStatusResponse {
  key_id: string;
  connected: boolean;
  expires_at?: string;
  account_id?: string;
  plan_type?: string;
}
