---
name: example-check-lesson-links
description: L23 teaching example (shared lower-level skill). Check the Markdown links in one lesson document and decide what each unresolved file link means — a genuinely broken cross-reference to fix, an illustrative `L<NN>` forward-pointer to leave alone, or a sibling that stage 2 hasn't generated yet. Invoked by higher-level authoring/generation skills that need their cross-references validated. It applies judgment, so it is a skill, not a plain tool; the mechanical extraction is delegated to `extract_links.py`.
---

# Example skill — check lesson links (shared lower-level skill)

> **This is L23 teaching material.** It illustrates a **shared lower-level
> skill**: a small capability that more than one higher-level "operating" skill
> invokes (write-once, reuse-many). In L23's worked system, both
> `author-lesson-roadmap` (validating a roadmap's cross-refs) and
> `generate-materials-from-roadmap` (validating generated materials' cross-refs)
> would `load_skill` this one instead of each re-implementing it — the fan-in
> node `C` in `A → C ← B`. See [../README.md](../README.md).

It is deliberately **not** a pure tool. The mechanical part — find the links,
check which file targets exist on disk — is delegated to a script
(`extract_links.py`). What's left is **judgment**, and that's why this is a
skill: an unresolved link is not automatically a bug.

## When to run it

Run this when you've written or generated a lesson document (a roadmap `.md`, an
intro, a lecture) and want its cross-references checked before handing off. It
checks **one document at a time**.

## Procedure

1. **Extract and resolve.** Run the helper on the document to get every
   unresolved file link (external URLs and in-page anchors are out of scope —
   no network, and anchor validation needs the rendered doc):

   ```sh
   uv run python -c "from pathlib import Path; from fluffy_potato_curriculum.lessons.L23.example_skills.check_lesson_links.extract_links import extract_links, unresolved_file_links; doc=Path('<DOC>'); [print(link.target) for link in unresolved_file_links(extract_links(doc.read_text(), doc.parent))]"
   ```

2. **Judge each unresolved file link.** For every flagged link, decide which
   case it is:
   - **Broken cross-reference** — a real typo or moved file (e.g. `objectvies.md`,
     or a `../L07/…` path that no longer exists). *Fix it* or surface it to the
     caller.
   - **Illustrative `L<NN>` forward-pointer** — the target names a lesson that is
     legitimately not authored yet (e.g. `../L24/objectives.md` referenced from a
     mini-cut doc). *Leave it* — this is the same real-vs-illustrative call
     `sync-lesson-numbering` makes. Note it; don't "fix" it.
   - **Not-yet-generated sibling** — a link to a file stage 2 will create
     (`L2304_lab_empty.ipynb`). *Leave it*, but report it so the caller knows the
     handoff isn't complete.

3. **Report.** Return a short list: broken links to fix, and deferred links
   (forward-pointers / not-yet-generated) with their reason. Don't rewrite
   anything silently — the caller decides.

## Why this is a skill and not a tool

If every caller wanted the same deterministic answer ("do these paths exist?"),
this would be a **tool** — and `extract_links.py` already *is* that tool. The
skill exists because the interesting step is classifying an unresolved link,
which needs context a schema can't carry. That is exactly L23's "a shared skill
that's really a tool" anti-pattern, seen from the good side: keep the judgment in
the skill, push the mechanics into the script.
