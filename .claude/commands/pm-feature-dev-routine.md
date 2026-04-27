---
name: 'pm-feature-dev-routine'
description: 'Development routine for Linear feature issues in evo-crm-community: discovery, planning, multi-repo implementation, user-testing gate, QA, and delivery with PRs targeting develop.'
disable-model-invocation: true
---

IT IS CRITICAL THAT YOU FOLLOW THESE STEPS EXACTLY:

<steps CRITICAL="TRUE">

0. Code style and language rules:
   - DO NOT write inline comments explaining step-by-step logic or implementation details.
   - Use comments only for non-obvious business logic, edge cases, or critical warnings.
   - ALL external artifacts MUST be in English: branch names, commit messages, PR titles, PR bodies, Linear comments.
   - Conversations with the user remain in Portuguese.
   - PRs ALWAYS target `develop`, never `main`. If `develop` does not exist on an affected submodule upstream, create it from `main` and push before branching off (see step 8).

1. Argument parsing:
   - Parse `$ARGUMENTS` to extract `ISSUE_REF` (accepts Linear issue ID like `EVO-460` or a Linear URL);
   - if `$ARGUMENTS` contains `ISSUE_REF=<value>`, use that value;
   - otherwise, use the entire `$ARGUMENTS` string as `ISSUE_REF`.

2. Critical repository safety rule:
   - NEVER change branches in the root monorepo `evo-crm-community`;
   - perform branch creation, commits, push, PR, and checkout-back ONLY inside the affected individual submodule repositories (e.g., `evo-ai-crm-community`, `evo-ai-frontend-community`, `evo-auth-service-community`, `evolution-api`, `evolution-go`, etc.).
   - The root repo is touched only when top-level orchestration files change (docker-compose, nginx, Makefile). In that case it follows the same `feat/<ISSUE_ID>` pattern on its own branch; even then, submodule-pointer bumps happen AFTER child PRs merge.

3. Resolve issue and load Linear context (mandatory):
   - Extract `ISSUE_ID` in canonical format (e.g., `EVO-460`);
   - Via Linear MCP, load full issue context: title, description, comments (all of them), linked attachments, existing PR URLs, current status, assignee, labels, priority;
   - If the issue has sub-issues (i.e., is an epic), list them via `list_issues` with `parent: <ISSUE_ID>` and load each sub-issue's context too;
   - If the issue is currently in `Todo` or `Backlog`, move it to `In Progress` via `save_issue` before continuing.

4. Load existing specs and codebase state (mandatory):
   - Search `_evo/` for spec/workflow files related to this feature (especially `_evo/bmm/`, `_evo/core/`, `_evo/_memory/`);
   - If a feature-specific specs directory exists (e.g., `_evo/bmm/<feature>/`), read ALL files completely — do not skim;
   - If NO spec exists for this feature, STOP and suggest generating one first via:
     - `evo-create-story` skill for a single-story spec
     - `evo-architect` skill for architecture decisions on anything non-trivial
     - `/bugs-to-linear-routine` is for bug intake only — do NOT use it for features
   - Identify which submodule(s) the work touches based on the issue scope;
   - Explore the affected submodule(s) thoroughly:
     - Rails (`evo-ai-crm-community`, `evo-auth-service-community`): models, controllers, routes, jobs, policies, migrations, specs
     - React (`evo-ai-frontend-community`): routes (react-router), pages, components, hooks, API client usage, contexts/stores, i18n keys
     - Go (`evolution-go`): `cmd/`, `pkg/`, handlers, services, migrations
     - Node (`evolution-api`): controllers/services under `src/`, Prisma schema if present
   - Use the Explore agent for deep codebase searches when the scope is large;
   - Build a complete map of what exists vs what is missing, per submodule.

5. Present discovery summary and wait for approval (mandatory gate):
   - Present to the user:
     - What the issue asks for (acceptance criteria from Linear comment)
     - Which submodules are affected
     - What specs exist under `_evo/` (list files found)
     - What is already implemented vs what is missing (table format, grouped by submodule)
     - Cross-service contracts (API endpoints, event payloads) and whether they need coordinated changes
     - Dependencies on other features or PRs
     - Estimated number of stories/tasks
   - STOP and ask: "Here's what I found. Ready to plan the implementation?";
   - DO NOT proceed until the user confirms.

6. Create implementation plan (mandatory):
   - Re-read every relevant spec file in `_evo/` carefully (every task, subtask, anti-pattern);
   - Create a detailed implementation plan with:
     - Per-submodule breakdown: files to create (with exact paths), files to modify (with what changes)
     - Order of implementation: data layer → backend (Rails/Go/Node) → frontend (React)
     - API contract between backend and React frontend (endpoint, method, request/response shape)
     - Architectural decisions and trade-offs
     - Security considerations (authN/authZ, input validation, rate limiting via `rack-attack` on Rails, CORS, tenant isolation, scope-by-account)
     - Edge cases to handle
   - If specs are incomplete or need architecture work, pause and suggest using evo skills:
     - `evo-architect` for architecture decisions
     - `evo-create-story` for missing story specs
   - Present the plan to the user.

7. Ask for explicit user approval before implementation starts (mandatory gate):
   - Present the implementation plan with scope, affected submodules, files, and order of operations;
   - STOP and ask: "Approve this plan to start coding?";
   - DO NOT start implementation until the user confirms.

8. Branch setup before coding (mandatory):
   - For each affected submodule repository:
     - Verify the working tree is clean (`git status --porcelain` returns empty). If there are uncommitted changes left over from a previous task, STOP and report the repository as blocked — do NOT stash, reset, or force-checkout silently. The user must commit, stash explicitly, or discard before the routine proceeds;
     - `git fetch origin`;
     - Ensure `develop` exists upstream via `git ls-remote --heads origin develop`:
       - If it exists, continue.
       - If it does NOT exist, create it from `main` and push before anything else: `git checkout main && git pull --ff-only origin main && git checkout -b develop && git push -u origin develop`. Report to the user when `develop` is newly created on a repo.
     - Sync `develop` locally: `git checkout develop && git pull --ff-only origin develop`;
     - Create or switch to the feature branch: `git checkout -B feat/<ISSUE_ID> origin/develop` (or `git checkout feat/<ISSUE_ID>` if it already exists and matches);
   - Confirm current branch in each repository and report branch names in the execution log;
   - If any repository fails to end up on `feat/<ISSUE_ID>`, STOP implementation until corrected;
   - NEVER postpone branch creation/switching to delivery time.
   - REMINDER: do NOT touch the branch of the root `evo-crm-community` repo unless top-level orchestration files are being modified.

9. Implement feature story by story:
   - Implement in dependency order: data layer → backend → frontend
   - For each story:
     a. Implement backend changes (migrations, models, policies, controllers, routes)
     b. Run per-submodule validation:
        - **Rails** (`evo-ai-crm-community`, `evo-auth-service-community`): `ruby -c <file>`, `bundle exec rspec <path>`, optionally `bundle exec rubocop <paths>`
        - **Go** (`evolution-go`): `go build ./...`, `go vet ./...`, `make test` or `go test ./...`
        - **Node** (`evolution-api`): inspect `package.json` and run the service's own scripts
     c. Implement frontend changes (service + hooks + components + page integration + i18n)
     d. Run frontend validation: `pnpm exec tsc -b --noEmit`, `pnpm lint`, `pnpm test` (vitest) on affected files
     e. Commit with Conventional Commits in English (e.g., `feat(crm): short description`, `feat(frontend): short description`, `feat(go): short description`);
   - After each commit, verify with `git status` in the affected submodule that the working tree is clean;
   - CRITICAL: before wiring the frontend, verify the REAL user navigation flow — which React route does the user actually hit? Check `evo-ai-frontend-community/src` routing config and the API client to confirm the endpoint shape matches the backend. Do NOT assume.
   - CRITICAL: when a change spans backend + frontend, commit backend first, confirm the API contract by hitting it (curl/httpie) or via a backend test, THEN wire the frontend.

10. Present testable state and wait for user testing (mandatory gate):
    - When there is something the user can visually or functionally test, STOP;
    - Tell the user which services need to be (re)started:
      - Rails: `bundle exec rails s` in the affected Rails service
      - Frontend: `pnpm dev` in `evo-ai-frontend-community`, or `pnpm build` for a prod bundle
      - Go: `make dev` or `make run` in `evolution-go`
      - Node: the service's own run script
      - Full stack: `docker compose up` from repo root if integrating across services
    - Provide specific test instructions:
      - Exact URLs to visit (frontend routes, API endpoints)
      - Exact actions to perform (click X, type Y, verify Z)
      - Expected behavior for each action
      - For API-only changes, provide a ready-to-paste `curl` or `httpie` command
    - STOP and wait for user feedback;
    - DO NOT continue implementation until the user confirms tests pass;
    - If the user reports bugs, fix them before proceeding.

11. Run comprehensive QA review (mandatory):
    - After the user confirms tests pass, run a thorough QA review using the Explore agent;
    - Compare EVERY acceptance criterion from the Linear comment against the implementation;
    - Security audit (scoped per submodule):
      - Authorization: endpoints check account/tenant ownership and user ownership (Rails Pundit-style policies or equivalent; Go/Node middleware)
      - Validation: all inputs validated (Rails strong params + model validations; React forms + API-side validation; Go struct validators)
      - Rate limiting: public/sensitive endpoints throttled (Rails `rack-attack`, nginx coarse limits)
      - XSS: React avoids `dangerouslySetInnerHTML`; Rails JSON views escape user content
      - CSRF: state-changing endpoints protected where session-backed
      - Cross-tenant data leakage: every query scoped by account/org id
      - Secrets: no credentials committed; env wired through compose/.env
    - Edge cases:
      - Null/empty values
      - Concurrent requests (race conditions in Rails callbacks / Go goroutines)
      - Missing relationships (deleted foreign keys, orphaned records)
      - Pagination boundaries
    - Frontend UX:
      - Loading states on async actions (skeleton / spinner)
      - Error feedback (API errors surfaced to the user with i18n keys)
      - Empty states
      - Keyboard accessibility (ESC, arrows, Enter where applicable)
      - Navigation flow consistency
      - i18n coverage (no hardcoded strings in English when pt-BR is supported)
    - Code quality:
      - N+1 queries (Bullet gem output on Rails if enabled)
      - Dead code or redundant checks
      - Naming consistency with existing codebase (per-submodule conventions)
      - TypeScript `any` usage in the frontend
    - Fix ALL issues found;
    - Re-run per-submodule tests after fixes;
    - Commit fixes in the appropriate submodule.

12. Present QA summary and wait for approval (mandatory gate):
    - Present to the user:
      - Issues found and fixed (table format, grouped by submodule)
      - Issues deferred (with justification)
      - Final test count and status per submodule
    - STOP and ask: "QA complete. Ready to ship?";
    - DO NOT proceed until the user confirms.

13. Push and create PR(s) (mandatory):
    - For each modified submodule repository:
      - Push branch to remote: `git push -u origin feat/<ISSUE_ID>`;
      - Create PR targeting `develop` via `gh pr create --base develop`:
        - Title in English: `feat(scope): short description (ISSUE_ID)` where `scope` is the submodule short name (`crm`, `frontend`, `go`, `api`, `auth`, `infra`)
        - Body in English with sections: `## Summary`, `## Security`, `## Test plan`, `## Changed Files`, `## Linked Issue`
        - When the change spans repos, include a `## Related PRs` section cross-linking the sibling PRs
      - Verify each PR was created successfully and report URLs.
    - If the root repo needs a submodule-pointer bump after child PRs merge, call this out explicitly in the final summary (do NOT bump the pointer in this routine; the bump belongs in a separate infra PR against the root).

14. Linear update after delivery:
    - Move the feature issue status to `In Review` via Linear MCP (NOT Done — review gate is owned by the reviewer);
    - Post a new comment on the Linear issue in English using the template in step 19, mentioning `@Davidson` with PR link(s), short summary, validation summary, and QA summary;
    - Reassign issue ownership to `Davidson`;
    - For epics with sub-issues: move each sub-issue to `In Review` too (not Done) and reassign to `Davidson`. The epic itself stays `In Review`.

15. Present final summary:
    - Linear issue ID and URL
    - Sub-issues (if epic) with their individual status + PR links
    - Affected submodule repositories
    - Branches and PRs per repository (with URLs)
    - Whether each PR was reused or created
    - Final Linear issue status (should be `In Review`)
    - Any known limitations, deferred items, or follow-up submodule-pointer bumps pending in the root

16. Post-finalization local git cleanup:
    - In each affected submodule repository, ensure the branch is pushed and the PR is open;
    - Checkout back to local `develop` in each affected repository: `git checkout develop`;
    - Fast-forward the local `develop` to match `origin/develop`: `git pull --ff-only origin develop`. This is mandatory — local `develop` must not be left behind, otherwise the next feature/bug iteration runs against stale code and may reintroduce already-fixed issues;
    - If `git pull --ff-only` fails because local `develop` diverged, STOP and report the repository as blocked — do NOT force-pull, rebase, or reset;
    - If local uncommitted changes block checkout or pull, STOP and report the repository as blocked — do NOT force checkout or stash silently.

17. Formatting rules for PR description and Linear comments:
    - ALWAYS write valid Markdown with real line breaks; NEVER output escaped newline sequences like `\n` or `\\n` in final text;
    - Use short sections with headings (e.g., `## Summary`, `## Security`, `## Test plan`, `## Changed Files`, `## Linked Issue`, `## Related PRs`);
    - Use bullet lists for changed files and validations;
    - Include plain clickable URLs (PR link, issue link) without escaping;
    - Before posting, quickly review rendered text and fix formatting if any literal escape sequence appears;
    - In `## Test plan` / `## Validation`, list only commands that actually apply to each affected submodule's language/tooling.

18. Default Linear comment template when notifying review:
    ```md
    PR(s) ready for review:
    - {repo-or-scope}: {PR_URL}
    {…one line per PR when multi-repo…}

    cc @Davidson

    ## Summary
    - <short feature item 1>
    - <short feature item 2>

    ## Validation
    - `<repo-a>: <actual validation command 1>`
    - `<repo-a>: <actual validation command 2>`
    - `<repo-b>: <actual validation command 1>`

    ## Changed Files
    - `<path/file-1>`
    - `<path/file-2>`

    ## QA Notes
    - <issue found and fixed 1>
    - <issue deferred with justification>

    ## Linked Issue
    - <ISSUE_ID>
    ```

</steps>
