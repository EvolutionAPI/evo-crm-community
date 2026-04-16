/**
 * AI Models changes for OAuth Codex support.
 *
 * Apply to: evo-ai-frontend-community/types/aiModels.ts
 *
 * 2 changes:
 * 1. Add "openai-codex" to availableModelProviders
 * 2. Add chatgpt/ models to availableModels
 */


// ===========================================================================
// CHANGE 1: Add to availableModelProviders array
// Insert after the "openai" entry
// ===========================================================================

// BEFORE:
// export const availableModelProviders = [
//   { value: "openai", label: "OpenAI" },
//   { value: "gemini", label: "Gemini" },
//   ...

// AFTER:
// export const availableModelProviders = [
//   { value: "openai", label: "OpenAI" },
//   { value: "openai-codex", label: "ChatGPT (OAuth)" },  // <-- NEW
//   { value: "gemini", label: "Gemini" },
//   ...


// ===========================================================================
// CHANGE 2: Add to availableModels array
// Insert at the end of the array, after the last cohere model
// ===========================================================================

// ADD these entries:
//
// // ChatGPT OAuth Codex models (subscription-based, no API key needed)
// { value: "chatgpt/gpt-5.4", label: "GPT-5.4", provider: "openai-codex" },
// { value: "chatgpt/gpt-5.4-pro", label: "GPT-5.4 Pro", provider: "openai-codex" },
// { value: "chatgpt/gpt-5.3-codex", label: "GPT-5.3 Codex", provider: "openai-codex" },
// { value: "chatgpt/gpt-5.3-codex-spark", label: "GPT-5.3 Codex Spark", provider: "openai-codex" },
// { value: "chatgpt/gpt-5.3-instant", label: "GPT-5.3 Instant", provider: "openai-codex" },
// { value: "chatgpt/gpt-5.3-chat-latest", label: "GPT-5.3 Chat Latest", provider: "openai-codex" },
// { value: "chatgpt/gpt-5.2-codex", label: "GPT-5.2 Codex", provider: "openai-codex" },
// { value: "chatgpt/gpt-5.2", label: "GPT-5.2", provider: "openai-codex" },
// { value: "chatgpt/gpt-5.1-codex-max", label: "GPT-5.1 Codex Max", provider: "openai-codex" },
// { value: "chatgpt/gpt-5.1-codex-mini", label: "GPT-5.1 Codex Mini", provider: "openai-codex" },


// ===========================================================================
// NOTE: No changes needed to LLMAgentConfig.tsx
// ===========================================================================
//
// The model filtering in LLMAgentConfig.tsx already works:
//   model.provider === selectedKey.provider
//
// When user selects a key with provider='openai-codex', only
// chatgpt/* models will appear in the dropdown. Zero code changes needed.
