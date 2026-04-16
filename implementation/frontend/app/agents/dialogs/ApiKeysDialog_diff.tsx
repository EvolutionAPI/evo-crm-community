/**
 * ApiKeysDialog changes for OAuth Codex support.
 *
 * Apply to: evo-ai-frontend-community/app/agents/dialogs/ApiKeysDialog.tsx
 *
 * 3 changes:
 * 1. Add imports for OAuthDeviceCodeFlow and OAuthStatusBadge
 * 2. Add state for OAuth flow
 * 3. Conditional rendering: when provider === "openai-codex",
 *    hide key_value field, show OAuth connect button
 */


// ===========================================================================
// CHANGE 1: Add imports at top of file
// ===========================================================================

// ADD:
// import { OAuthDeviceCodeFlow } from "./OAuthDeviceCodeFlow";
// import { OAuthStatusBadge } from "../components/OAuthStatusBadge";


// ===========================================================================
// CHANGE 2: Add state variable inside the component
// ===========================================================================

// ADD after existing state declarations:
// const [showOAuthFlow, setShowOAuthFlow] = useState(false);


// ===========================================================================
// CHANGE 3: Modify the form section (inside the add/edit form)
// ===========================================================================

// In the form where provider select and key_value input are rendered,
// WRAP the key_value input in a conditional:
//
// BEFORE:
//   <label>Key Value</label>
//   <input type="password" ... />
//
// AFTER:
//   {currentApiKey.provider === "openai-codex" ? (
//     /* OAuth flow — no key_value needed */
//     showOAuthFlow ? (
//       <OAuthDeviceCodeFlow
//         clientId={clientId}  /* from parent props or localStorage */
//         name={currentApiKey.name || "ChatGPT OAuth"}
//         onSuccess={(keyId) => {
//           setShowOAuthFlow(false);
//           setIsAddingApiKey(false);
//           // Reload API keys list
//           onOpenChange(true);  /* or call loadApiKeys() */
//         }}
//         onCancel={() => setShowOAuthFlow(false)}
//       />
//     ) : (
//       <Button
//         onClick={() => {
//           if (!currentApiKey.name) {
//             /* Require name before starting OAuth */
//             return;
//           }
//           setShowOAuthFlow(true);
//         }}
//         className="w-full bg-emerald-600 text-white hover:bg-emerald-700"
//       >
//         <ExternalLink className="mr-2 h-4 w-4" />
//         Connect with ChatGPT
//       </Button>
//     )
//   ) : (
//     /* Standard API key input — UNCHANGED */
//     <>
//       <label>Key Value</label>
//       <input type="password" ... />
//     </>
//   )}


// ===========================================================================
// CHANGE 4: Modify the key list item rendering
// ===========================================================================

// In the list where each API key is displayed, add OAuthStatusBadge
// for OAuth keys:
//
// BEFORE (for each key in the list):
//   <span>{key.name}</span>
//   <span className="text-gray-500">Key: ********</span>
//
// AFTER:
//   <span>{key.name}</span>
//   {key.auth_type === "oauth_codex" ? (
//     <OAuthStatusBadge keyId={key.id} clientId={clientId} />
//   ) : (
//     <span className="text-gray-500">Key: ********</span>
//   )}


// ===========================================================================
// CHANGE 5: Hide edit key_value for OAuth keys
// ===========================================================================

// In the edit form, when editing an OAuth key:
//   - Do NOT show the key_value password field
//   - Instead show "Reconnect" button that triggers OAuthDeviceCodeFlow
//   - Name and is_active can still be edited normally


// ===========================================================================
// CHANGE 6: Add ExternalLink icon import
// ===========================================================================

// ADD to lucide-react imports:
// import { ..., ExternalLink } from "lucide-react";


// ===========================================================================
// FULL FLOW SUMMARY
// ===========================================================================
//
// Adding a standard API key (UNCHANGED):
//   1. User selects provider "OpenAI" from dropdown
//   2. User enters name + key value
//   3. Click "Add" -> POST /apikeys with auth_type="api_key"
//
// Adding an OAuth Codex key (NEW):
//   1. User selects provider "ChatGPT (OAuth)" from dropdown
//   2. Key value field is HIDDEN
//   3. User enters a name (e.g., "My ChatGPT")
//   4. Clicks "Connect with ChatGPT" button
//   5. OAuthDeviceCodeFlow component appears:
//      - Shows user_code in large monospace font
//      - Shows link to auth.openai.com/codex/device
//      - Polls backend every 5s for authorization
//   6. User opens link, enters code, authorizes on ChatGPT
//   7. Backend receives tokens, encrypts, stores in DB
//   8. OAuthDeviceCodeFlow shows "Connected!" green checkmark
//   9. Dialog reloads key list
//   10. Key appears in list with OAuthStatusBadge (green "Connected")
//
// Viewing OAuth keys in list:
//   - Shows OAuthStatusBadge instead of "Key: ********"
//   - Badge shows Connected/Disconnected + plan type (Plus/Pro)
//   - Refresh button to re-check status
//
// Editing OAuth keys:
//   - Can edit name and is_active
//   - Cannot edit key_value (doesn't exist)
//   - "Reconnect" button available if token expired
