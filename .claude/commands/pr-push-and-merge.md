---
description: Commit current work to a PR branch, squash-merge it, and re-pull main
model: sonnet
---

Commit the current working changes onto a PR branch, merge the PR, and sync `main`. Keep every
message extremely concise.

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
7. **Re-pull main.** `git switch main && git pull --ff-only`.

Report the merged PR number/URL and confirm `main` is up to date. If any step fails (e.g. merge
conflict, failing required checks), stop and surface the error rather than forcing past it.

If `$ARGUMENTS` is provided, use it as the PR title / commit subject.
