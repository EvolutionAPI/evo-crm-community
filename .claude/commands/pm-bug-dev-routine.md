---
name: 'pm-bug-dev-routine'
description: 'Development routine for bugs already created in Linear: implement fix using BMAD quick-dev, reuse existing review context, open/update PR targeting develop.'
disable-model-invocation: true
---

IT IS CRITICAL THAT YOU FOLLOW THESE STEPS EXACTLY:

<steps CRITICAL="TRUE">

0. Argument parsing:
   - Parse `$ARGUMENTS` to extract `ISSUE_REF` (accepts Linear issue ID like `EVO-460` or a Linear URL);
   - if `$ARGUMENTS` contains `ISSUE_REF=<value>`, use that value;
   - otherwise, use the entire `$ARGUMENTS` string as `ISSUE_REF`.

1. Code style and language rules:
   - DO NOT write inline comments explaining step-by-step logic or implementation details.
   - Use comments only for non-obvious business logic, edge cases, or critical warnings.
   - ALL external artifacts MUST be in English: branch names, commit messages, PR titles, PR bodies, Linear comments.
   - Conversations with the user remain in Portuguese.

2. No external PM status update:
   - This routine does NOT update any external PM/bug-tracker status. Only Linear is touched.

3. Critical repository safety rule:
   - NEVER change branches in the root monorepo `evo-crm-community`;
   - perform branch creation, commits, push, PR, and checkout-back ONLY inside the affected individual submodule repositories (e.g., `evo-ai-crm-community`, `evo-ai-frontend-community`, `evo-auth-service-community`, `evolution-api`, `evolution-go`, etc.).

4. Resolve issue and load Linear context:
   - Use the `ISSUE_REF` extracted in step 0;
   - Extract `ISSUE_ID` in canonical format (e.g., `EVO-460`);
   - Via Linear MCP, load full issue context: title, description, comments (all of them), linked attachments, existing PR URLs, current status, assignee, labels, priority.

5. Detect review feedback before coding (mandatory):
   - Inspect the latest review comment(s) in Linear and classify by canonical marker line `Review Decision: <APPROVE|CHANGES_REQUESTED|BLOCKED>`;
   - If the marker line is absent, treat decision as `unknown` and continue using the original spec (from the issue's comment posted by the intake routine);
   - If latest decision is `BLOCKED`, STOP and report the blocker verbatim;
   - If latest decision is `CHANGES_REQUESTED`, extract the mandatory correction checklist and treat it as implementation input alongside the original spec;
   - If no prior review exists, continue with the original spec implementation.

6. Determine branch/PR strategy:
   - Branch pattern is mandatory: `fix/<ISSUE_ID>` (e.g., `fix/EVO-460`);
   - Before any code change, verify current branch in each affected submodule; if the branch name differs, STOP and switch/create `fix/<ISSUE_ID>` first (step 8);
   - If an existing active PR for this issue exists, REUSE it ONLY when ALL of these are true:
     - PR status is open;
     - PR source branch matches `fix/<ISSUE_ID>`;
     - PR target branch is `develop`.
   - If `CHANGES_REQUESTED` was detected, DO NOT create a new PR: push new commits to the existing valid PR;
   - Create a new PR only when no valid PR exists yet for `ISSUE_ID`.

7. Ask for explicit user approval before implementation starts:
   - Present the implementation plan with:
     - Scope (original spec from Linear comment + any review corrections);
     - Affected submodule repositories;
     - Target branch per repo (`fix/<ISSUE_ID>`) and PR strategy (reuse vs new);
     - Planned per-submodule validation commands;
   - Ask explicit confirmation to start coding;
   - DO NOT start implementation until the user confirms.

8. Branch setup before coding (mandatory):
   - In each affected submodule repository:
     - Verify the working tree is clean (`git status --porcelain` returns empty). If there are uncommitted changes left over from a previous task, STOP and report the repository as blocked — do NOT stash, reset, or force-checkout silently. The user must commit, stash explicitly, or discard before the routine proceeds;
     - `git fetch origin`;
     - Ensure `develop` exists upstream. If not, create it from `main` and push before anything else: `git checkout main && git pull --ff-only origin main && git checkout -b develop && git push -u origin develop`. Report to the user when `develop` is newly created on a repo.
     - Sync `develop` locally: `git checkout develop && git pull --ff-only origin develop`;
     - Create or switch to the issue branch: `git checkout -B fix/<ISSUE_ID> origin/develop` (or `git checkout fix/<ISSUE_ID>` if it already exists and matches);
   - Confirm current branch in each repository and report branch names in the execution log;
   - If any repository fails to end up on `fix/<ISSUE_ID>`, STOP implementation until corrected;
   - NEVER postpone branch creation/switching to delivery time.
   - REMINDER: do NOT touch the branch of the root `evo-crm-community` repo.

9. Implement fix (mandatory — BMAD quick-dev):
   - IT IS CRITICAL THAT YOU FOLLOW THIS COMMAND: LOAD the FULL file `{project-root}/_evo/bmm/workflows/evo-quick-flow/quick-dev/workflow.md`, READ its entire contents, and follow its directions exactly.
   - During quick-dev, retrieve the plan via Linear MCP and use the spec saved in the issue comment (posted by the `/bugs-to-linear-routine` intake) as the source of truth.
   - When `CHANGES_REQUESTED` exists, merge the review checklist + original spec as the required scope.
   - Implement the fix and run local tests per affected submodule:
     - **Rails** (`evo-ai-crm-community`, `evo-auth-service-community`): `ruby -c <file>`, `bundle exec rspec <path>`, optionally `bundle exec rubocop <paths>`;
     - **React frontend** (`evo-ai-frontend-community`): `pnpm exec tsc -b --noEmit`, `pnpm lint`, `pnpm test` (vitest);
     - **Go** (`evolution-go`): `go build ./...`, `go vet ./...`, `make test` or `go test ./...`;
     - **Node** (`evolution-api`): inspect `package.json` and run the service's own scripts;

10. Ask for explicit user approval before code delivery:
    - Present a short pre-delivery summary with:
      - Affected repositories;
      - Target branch names (`fix/<ISSUE_ID>`);
      - Existing vs new PR plan;
      - Actual validation commands that were run and their results;
    - Ask explicit confirmation to proceed with commit/push/PR actions;
    - DO NOT commit, push, or create/update PR until the user confirms.

11. Code delivery:
    - Identify all affected submodule repositories;
    - For each repository, use the issue branch `fix/<ISSUE_ID>` (create only if missing — should already exist from step 8);
    - Pre-delivery branch validation is mandatory: if any affected submodule is not on `fix/<ISSUE_ID>`, block delivery and report the mismatch;
    - Commit changes with Conventional Commits in English (e.g., `fix(crm): short description`, `fix(frontend): short description`, `fix(go): short description`);
    - Push branch to remote: `git push -u origin fix/<ISSUE_ID>`;
    - If a PR already exists for this issue, update that PR with the new commits only;
    - If no PR exists, create a PR targeting `develop` via `gh pr create --base develop`;
    - When the change spans multiple submodules, cross-link the PRs in each body under a `## Related PRs` section.

12. Linear update after delivery:
    - Move the issue status to `In Review` via Linear MCP;
    - Post a new comment on the Linear issue using the template in step 19, mentioning `@Davidson` with PR link(s), short fix summary, and validation summary;
    - Reassign issue ownership to `Davidson`.

13. Wait for review and approval (this routine does NOT loop; it returns after Linear is updated). The `/pm-bug-review-routine` (future) handles the reviewer side.

14. Ask for explicit user approval before finalization (when the user re-invokes this routine after review is done):
    - If the user re-runs this routine for the same `ISSUE_ID` after a review decision has been posted, present a short summary with affected repositories, branch(es), PR link(s), and detected review status;
    - Ask explicit confirmation to proceed with final status updates;
    - Do NOT finalize the issue in Linear until the user confirms.

15. After user confirmation on finalization:
    - DO NOT move the Linear issue to `Done`; keep the issue in its current Linear status;
    - Ensure issue status is `In Review` before ending the flow (if not, update it to `In Review`);
    - Post a final comment in Linear with PR link(s), fix summary, and validation summary.

16. Post-finalization local git cleanup:
    - In each affected repository, ensure branch changes are pushed and the PR is open;
    - Checkout back to local `develop` in each affected repository: `git checkout develop`;
    - Fast-forward the local `develop` to match `origin/develop`: `git pull --ff-only origin develop`. This is mandatory — local `develop` must not be left behind, otherwise the next feature/bug iteration runs against stale code and may reintroduce already-fixed issues;
    - If `git pull --ff-only` fails because local `develop` diverged, STOP and report the repository as blocked — do NOT force-pull, rebase, or reset;
    - If local uncommitted changes block checkout or pull, STOP and report the repository as blocked — do NOT force checkout or stash silently.

17. Return final summary with:
    - Linear issue ID and URL;
    - Detected review decision: `APPROVE | CHANGES_REQUESTED | BLOCKED | unknown`;
    - Affected submodule repositories;
    - Branches and PRs per repository;
    - Whether each PR was reused or created;
    - Checkout-back-to-`develop` status per repository;
    - Link to the Linear comment that notified the reviewer;
    - Final Linear issue status.

18. Formatting rules for PR description and Linear comments:
    - ALWAYS write valid Markdown with real line breaks; NEVER output escaped newline sequences like `\n` or `\\n` in final text;
    - Use short sections with headings (e.g., `## Summary`, `## Validation`, `## Linked Issue`, `## Related PRs`);
    - Use bullet lists for changed files and validations;
    - Include plain clickable URLs (PR link, issue link) without escaping;
    - Before posting, quickly review rendered text and fix formatting if any literal escape sequence appears;
    - In `## Validation`, list only commands that actually apply to each affected submodule's language/tooling.

19. Default comment template when notifying review in Linear:
    ```md
    PR ready for review: <PR_URL(s)>

    cc @Davidson

    ## Summary
    - <short fix item 1>
    - <short fix item 2>

    ## Validation
    - `<repo-a>: <actual validation command 1>`
    - `<repo-a>: <actual validation command 2>`
    - `<repo-b>: <actual validation command 1>`

    ## Changed Files
    - `<path/file-1>`
    - `<path/file-2>`

    ## Linked Issue
    - <ISSUE_ID>
    ```

</steps>
