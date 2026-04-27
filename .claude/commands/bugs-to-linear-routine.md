---
name: 'bugs-to-linear-routine'
description: 'Create Linear issues from user-provided bug topics: quick-spec generation -> Linear Todo creation -> spec posted as comment. No external API consumption — user supplies bugs directly in the conversation.'
disable-model-invocation: true
---

IT IS CRITICAL THAT YOU FOLLOW THESE STEPS EXACTLY:

<steps CRITICAL="TRUE">

0. Code style and language rules:
   - ALL Linear content (issue title, description, comments, labels) MUST be in English.
   - Conversations with the user remain in Portuguese.

1. Parse user-provided bugs:
   - Input: bug topics the user pasted in the conversation or `$ARGUMENTS` (typically Markdown bullets or short blocks, one per bug).
   - Split into individual bug items. Each item must at minimum have a short title/description.
   - Hard processing limit: at most 3 bugs per run. If the user sent more than 3, process the first 3 in the order given and report the remaining count at the end.
   - Argument override (optional): if `$ARGUMENTS` (or any of the bug blocks) contains `ASSIGNEE=<email|user_id|"me">`, capture the value as `ASSIGNEE_OVERRIDE` and strip it from the bug body before parsing. Falls back to `me` if not provided. Applies to ALL bugs in this run.
   - For each bug, extract (or prompt the user for) the following fields:
     - `title` (required, short imperative)
     - `description` (required — what happens)
     - `steps_to_reproduce` (optional; if missing, mark `TODO: Missing Input`)
     - `expected_behavior` (optional)
     - `actual_behavior` (optional)
     - `module` (which submodule/area: `crm`, `frontend`, `auth`, `go`, `api`, `infra`, etc.)
     - `environment` (optional — browser, OS, service version)
     - `screenshot_urls` (optional list of URLs)
     - `severity` (required — `critical` | `high` | `medium` | `low`). If missing for any bug, STOP and ask the user per bug before proceeding.
   - If any required field is missing after prompting, do NOT proceed for that bug.

2. Generate an inline bug-spec for EACH bug (mandatory):
   - Do NOT invoke `evo-quick-spec` — the full BMAD quick-spec workflow is too heavy for bug intake. Use the inline template below.
   - Produce each spec directly in memory (no file on disk is required; the spec lives in the Linear comment). If the user wants a local copy, they will ask.
   - Template (English, Markdown):
     ```md
     # <Bug title>

     **Severity:** <critical | high | medium | low> -> Linear priority <1|2|3|4>
     **Module:** <crm | frontend | auth | go | api | infra>
     **Environment:** <browser/OS/service version or `TODO: Missing Input`>

     ## Summary
     <one paragraph describing the bug and its user-visible impact>

     ## Steps to Reproduce
     1. <step 1 or `TODO: Missing Input`>
     2. ...

     ## Expected Behavior
     <what should happen, or `TODO: Missing Input`>

     ## Actual Behavior
     <what happens today>

     ## Scope
     **In scope:** <what the fix must do>
     **Out of scope:** <explicit non-goals>

     ## Acceptance Criteria
     - [ ] <objective, testable criterion 1>
     - [ ] <objective, testable criterion 2>

     ## Suspected Area
     <files/modules worth investigating first; mark `TODO` if unknown>

     ## Evidence
     <screenshot URLs as Markdown image links, or "none provided">
     ```
   - Do NOT hallucinate facts. Keep `TODO: Missing Input` markers verbatim where data was absent.

3. Mandatory spec validation before any Linear write:
   - Validate each generated spec against the source bug fields (`title`, `description`, `steps_to_reproduce`, `expected_behavior`, `actual_behavior`, `module`, `environment`, `screenshot_urls`).
   - Ensure each spec has clear reproduction steps, expected vs actual behavior, scope boundaries, and objective acceptance criteria.
   - If validation fails, STOP and regenerate/fix the spec before presenting for approval.

4. Mandatory Linear priority mapping from severity:
   - `critical` -> Linear priority `1` (Urgent)
   - `high`     -> Linear priority `2` (High)
   - `medium`   -> Linear priority `3` (Normal)
   - `low`      -> Linear priority `4` (Low)
   - Include severity + mapped priority in the Linear issue description.

5. Resolve Linear target (mandatory, via Linear MCP):
   - **Team:** `Evolution` (`EVO`) — id `afbf875a-f524-449c-85fb-e6c66f11ab4b`.
   - **Project:** `Evo CRM Community` — id `794f3f83-ac63-41cb-8f82-7e04eb52d10d`. This is the canonical project for all tickets created from this repo (as of 2026-04-22). Do NOT default to `Evo AI` — that is the legacy project. If the user explicitly says to use a different project, follow that override.
   - **Status:** `Todo` — state id `fc0cc9a6-482b-45e5-b1da-910f04e4545c`.
   - **Assignee:** the user invoking the routine — pass `assignee: "me"` to Linear MCP `save_issue` so each team member sees the bugs they opened in their own queue. The Linear MCP resolves `"me"` against the currently authenticated Linear account. If `ASSIGNEE_OVERRIDE` was captured in step 1, pass that value verbatim instead (the MCP accepts `me`, an email, a Linear user id, or a name).
   - **Label:** `Bug` — id `94e516cc-42be-4c37-b1e6-1cef2c005baf`.
   - Before creating any new ticket, **search the `Evo CRM Community` backlog for potential duplicates** using `list_issues` with a query derived from the bug's key terms. If a strong duplicate exists, prefer enriching the existing ticket with a comment (using `save_comment`) instead of creating a new one, and report the link to the user.
   - If any of the cached IDs above fails (e.g., Linear workspace changes), fall back to discovery (`list_teams`, `list_projects`, `list_issue_statuses`, `list_issue_labels`, `list_users`) and update the `reference_linear_workspace.md` memory afterwards.

6. Mandatory post-generation revision checkpoint:
   - Before asking for approval, run a self-review pass to catch inconsistencies, missing evidence links, and priority-mapping errors.
   - If review finds issues, fix/regenerate specs and re-run step 3 validation before presenting for approval.

7. Mandatory human approval gate before any Linear write:
   - Default mode is `preview-only`: ZERO calls to `create_issue`, `update_issue`, `create_comment`, `create_attachment`.
   - Present a concise review package per bug:
     - Title (English) and severity
     - Mapped Linear priority
     - Short spec summary (3-5 lines)
     - Local spec path
     - Target team, project, status (`Todo`), assignee (`me` by default, or the value captured in `ASSIGNEE_OVERRIDE` if provided)
     - Screenshot URLs (if any) and whether they will be embedded
   - Explicitly ask using this exact prompt: `Aprova subir estes itens para o Linear? Responda: APROVADO`
   - Proceed with Linear writes ONLY after an explicit user confirmation message containing the literal word `APROVADO`.
   - If approval is missing, declined, or ambiguous, STOP after preview and wait for user feedback/revisions.

8. Create Linear issues (only after `APROVADO`):
   - For each approved bug, call `create_issue` via Linear MCP with:
     - `title` in English (short, imperative)
     - `description` in English — include: severity label, mapped priority, module, environment, reproduction steps, expected vs actual, any screenshot URLs inline as Markdown image links
     - `team`, `project`, `state` (Todo), `assignee` (`me` by default, or `ASSIGNEE_OVERRIDE` if captured in step 1), `priority` (from step 4 mapping), `labels` (from step 5)
   - After each issue is created, post the full quick-spec as a Linear comment on that issue using `create_comment` (no file attachment).
   - If `screenshot_urls` exist, embed them in BOTH the description and the comment body.

9. Return a per-bug summary:
   - For each processed bug:
     - Original title as provided by the user
     - Severity -> Linear priority used
     - Linear issue URL and identifier
     - Linear comment URL (where the spec was posted)
     - Local spec path
     - Screenshot propagation status (embedded yes/no)
   - If bugs were skipped due to the 3-per-run limit, list their titles at the end so the user can rerun.

</steps>
