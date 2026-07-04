---
description: Commit current work to a PR branch, squash-merge it, re-pull main, and prune merged worktrees
model: sonnet
---

Commit the current working changes onto a PR branch, merge the PR, sync `main`, and clean up any
worktree left behind by the merge. Keep every message extremely concise.

1. **Sanity-check.** `git status` and `git diff` to see what's staged/unstaged. If there's
   nothing to commit and no open PR, stop and say so.
2. **Branch.** If currently on `main`, create a topic branch first
   (`git switch -c <short-kebab-name>`) — never commit straight to `main`. If already on a
   feature branch, stay on it.
3. **Commit.** `git add -A`, then commit with a one-line Conventional Commit subject (no body):
   e.g. `feat(curriculum): add L12 eval harness`. End the message with:
   ```
   Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
   ```
4. **Push.** `git push -u origin HEAD`.
5. **PR.** If no PR exists for the branch, open one with `gh pr create` — a one-line title and a
   1–3 bullet body, no filler. If a PR already exists, reuse it.
6. **Squash-merge.** `gh pr merge --squash --delete-branch`. Use an extremely concise squash
   commit title (the PR title) and a terse bullet body — no restating the diff.
7. **Wait for CI's version bump, then sync main.** The squash-merge triggers
   [`.github/workflows/bump.yml`](../../.github/workflows/bump.yml), which — a few seconds *after*
   the merge — pushes a `bump:` commit and a `vX.Y.Z` tag onto `main`. A pull fired immediately
   after the merge races ahead of that push and misses the bump (it'd only arrive on some later
   pull), so wait for the run first:
   - Grab the merge commit SHA: `gh pr view <pr> --json mergeCommit -q .mergeCommit.oid`.
   - Poll `gh run list --workflow=bump.yml --branch main --limit 5 --json databaseId,headSha,status`
     until the run whose `headSha` equals that SHA appears, then block on it with
     `gh run watch <databaseId> --exit-status`. The run always completes even when there's nothing
     to release — `cz bump` treats "no eligible commits" as a no-op — so this never hangs waiting
     for a bump that isn't coming.

   Then pull so the local checkout picks up the `bump:` commit and its tag. Find the main checkout
   via `git worktree list` (the entry on the default branch). If you're standing in it,
   `git switch main && git pull --ff-only --tags`. If you're in a separate worktree, don't
   `git switch main` (git forbids the default branch in a second worktree) — sync it in place with
   `git -C <main-checkout> pull --ff-only --tags`.
8. **Remove the current worktree.** Only if this session is in a `.claude/worktrees/<name>/`
   worktree. Prefer `ExitWorktree` with `action: "remove"` — it restores the working directory
   and deletes the worktree dir + branch. Because the merge was a squash, that call may refuse
   over the just-merged commits; once you've confirmed the PR merged, re-invoke with
   `discard_changes: true`. If the worktree wasn't created by this session's `EnterWorktree`,
   fall back to `git worktree remove <path>` run from the main checkout — never `--force`.
9. **Prune other merged worktrees.** `git fetch --prune`, then for each other
   `.claude/worktrees/*` worktree whose branch shows `: gone]` in `git branch -vv` (its PR
   branch was deleted on merge), `git worktree remove <path>` — never `--force`, so a worktree
   with uncommitted changes aborts and is left alone. Skip any whose upstream is still live.
   Finish with `git worktree prune` to clear dangling admin entries.

Report the merged PR number/URL, the new version/tag CI produced (or note there was no bump when
nothing was release-worthy), confirm `main` is up to date, and list which worktrees were removed. If any step fails (e.g. merge conflict, failing required checks, a dirty worktree that
won't remove cleanly), stop and surface the error rather than forcing past it.

If `$ARGUMENTS` is provided, use it as the PR title / commit subject.
