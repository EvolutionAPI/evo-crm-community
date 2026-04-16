/**
 * Agent service changes for OAuth Codex support.
 *
 * Apply to: evo-ai-frontend-community/services/agentService.ts
 *
 * 2 changes:
 * 1. Add OAuth type imports
 * 2. Add 4 new OAuth API functions at the end of the file
 *
 * All existing functions remain UNCHANGED.
 * The existing ApiKey interface needs auth_type added.
 */


// ===========================================================================
// CHANGE 1: Add import at top of file
// ===========================================================================

// ADD:
// import type {
//   OAuthDeviceCodeResponse,
//   OAuthPollResponse,
//   OAuthStatusResponse,
// } from "@/types/oauth";


// ===========================================================================
// CHANGE 2: Update ApiKey interface
// ===========================================================================

// BEFORE:
// export interface ApiKey {
//   id: string;
//   name: string;
//   provider: string;
//   client_id: string;
//   created_at: string;
//   updated_at: string;
//   is_active: boolean;
// }

// AFTER:
// export interface ApiKey {
//   id: string;
//   name: string;
//   provider: string;
//   client_id: string;
//   created_at: string;
//   updated_at: string;
//   is_active: boolean;
//   auth_type: string;              // <-- NEW: "api_key" or "oauth_codex"
//   oauth_connected?: boolean;      // <-- NEW: computed field from backend
// }


// ===========================================================================
// CHANGE 3: Add 4 OAuth functions at end of file
// ===========================================================================

// ADD:
//
// // --- OAuth Codex API functions ---
//
// export const initiateOAuthDeviceCode = (clientId: string, name: string) =>
//   api.post<OAuthDeviceCodeResponse>("/api/v1/agents/oauth/codex/device-code", {
//     client_id: clientId,
//     name,
//   });
//
// export const pollOAuthDeviceCode = (keyId: string) =>
//   api.post<OAuthPollResponse>("/api/v1/agents/oauth/codex/device-poll", {
//     key_id: keyId,
//   });
//
// export const getOAuthStatus = (keyId: string, clientId: string) =>
//   api.get<OAuthStatusResponse>(
//     `/api/v1/agents/oauth/codex/status/${keyId}`,
//     { headers: { "x-client-id": clientId } }
//   );
//
// export const revokeOAuth = (keyId: string, clientId: string) =>
//   api.delete(
//     `/api/v1/agents/oauth/codex/${keyId}`,
//     { headers: { "x-client-id": clientId } }
//   );


// ===========================================================================
// IMPORTANT: API base URL
// ===========================================================================
//
// These OAuth endpoints are on the PROCESSOR service (port 8000),
// which is the same service that handles /api/v1/agents/apikeys.
// The existing `api` axios instance already points to the correct base URL
// (VITE_AGENT_PROCESSOR_URL or VITE_EVOAI_API_URL).
//
// Verify in frontend/services/api.ts that the base URL is correct.
