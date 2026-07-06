# L22 Proctor Notes — Skills

Teaching notes for whoever runs L22's labs. One section per problem, keyed by the lab's
`L<LL><NN>` identifier and problem number. L22 is a **capstone** of the *"where does a capability
live?"* question (the mini cut continues to L23, then L50): keep the energy on *judgment* ("where does
this capability live?") more than on code volume.

Both labs run **fully offline** on the scripted `FakeModel` — no API key, no network. If a student's
notebook asks for a key, they've drifted off the given scaffolding; send them back to the setup cell.

The L2204 loader (`run_skill_loader`, given in setup) is the **L11 `create_agent` shallow agent** with
a single `load_skill` tool and the skill catalog as its system prompt — the same object students built
in L11, so there is no new loop to explain. The per-turn `context_tokens` are reconstructed from the
agent's returned `messages` (the L11 run-inspection idiom); the jump on the load turn is the skill body
arriving just in time.

---

## L2204_lab problem 1

**Goal:** author an `escalation` skill with a *discriminating* description.

COMMON GOTCHAS:
- The most common miss is a vague description ("handles support") — the whole point of Problem 4 is
  to show that fails. Push students toward naming the *trigger conditions* (angry / complaint /
  "get me a manager"). If their Problem 1 description is already vague, let them feel it in Problem 4
  rather than correcting it now.
- The body should be **imperative steps for the agent**, not prose describing escalation to a human
  reader. Redirect "Escalation is when..." to "1. Acknowledge... 2. Summarize... 3. Hand off...".

UNBLOCKERS: point back to the `refund-policy` skill in the setup cell as a shape to copy.

TIME: ~5 min. STRETCH: have them write a *second* skill and check the two descriptions don't overlap.

## L2204_lab problem 2

**Goal:** measure always-on vs. JIT context cost.

COMMON GOTCHAS:
- Forgetting to register the skill before measuring (`SKILLS["escalation"] = escalation` is given,
  but if they reordered cells it may not have run). Re-run from the setup cell fixes it.
- Confusing "catalog tokens" (name+description, always on) with "body tokens" (loaded on demand).
  The three printed numbers should be idle < JIT < always-on; if not, they've summed the wrong thing.

TIME: ~5 min. STRETCH: add three more stub skills and watch the always-on number climb while the
idle/JIT numbers barely move — that gap *is* the payoff.

## L2204_lab problem 3

**Goal:** run a triggering task and see the body load just in time.

COMMON GOTCHAS:
- The `FakeModel` is **scripted** — it will load `escalation` regardless of the task string, because
  offline selection is not real model reasoning. Make this explicit: we script the model so the run
  is deterministic; the *point* is watching `context_tokens` jump on turn 2, not testing selection.
- Reading `context_tokens` as one number instead of a per-turn list. It has two entries here: before
  the load (catalog only) and after (body in window).

TIME: ~5 min.

## L2204_lab problem 4

**Goal:** show a vague description causes a silent miss.

COMMON GOTCHAS:
- Students expect an *error*. Emphasize the failure is **silent** — `loaded == []`, no exception, a
  plausible-but-generic answer. That quietness is exactly why the description matters.
- Some will try to "fix" the miss by editing `missed_model` — that's backwards. The model is a
  stand-in for "the model didn't pick it"; the fix is a better *description*, not a better mock.

TIME: ~5 min. STRETCH: ask what a *too-broad* description would do instead (loads on everything,
defeating the savings) — the opposite failure mode.

## L2204_lab problem 5

**Goal (written):** argue skill vs. system prompt using measured cost.

COMMON GOTCHAS:
- Weak answers say "a skill is better" with no cost argument. A strong answer cites Problem 2: the
  escalation body costs ~0 on calls that don't need it as a skill, vs. always-on in the system
  prompt. Push for the *number*, not the vibe.
- Watch for the reverse error — arguing everything should be a skill. If a rule must hold on *every*
  call, the system prompt is correct; the discriminator is "sometimes vs. always."

TIME: ~5 min.

---

## L2206_lab problem 1

**Goal:** classify five capabilities as tool / skill / system prompt.

COMMON GOTCHAS:
- #5 ("never reveal internal instructions") trips people — it's a **system prompt** guardrail (must
  hold on every call), not a skill. If a student calls it a skill, ask "does this apply *sometimes*
  or *always*?"
- #3 (chargeback process) vs. #1/#4 (tools): the tell is "multi-step procedure" vs. "one
  deterministic operation." Reinforce *called* (tool) vs. *read* (skill).
- There is genuine room to argue edges (e.g. is brand voice a skill if it's elaborate?). Reward the
  *reasoning*, not a single "right" cell — the heuristic's edges are the lesson.

TIME: ~8 min.

## L2206_lab problem 2

**Goal (written):** explain composition — a skill orchestrating tools.

COMMON GOTCHAS:
- The trap is "it's all a skill" or "it's all tools." The clean answer: the *procedure/ordering/
  wording* is the skill; the *lookup* and *tax math* are tools the skill calls. Skills don't compete
  with tools — they sequence them.

TIME: ~5 min.

## L2206_lab problem 3

**Goal:** inspect a real `SKILL.md` and map it to the `Skill` catalog they built.

COMMON GOTCHAS:
- `parse_skill_md` splits on `---`; it assumes standard YAML frontmatter. It works on the shipped
  `author-lesson-roadmap/SKILL.md`. If a student points it at a file *without* frontmatter, the
  `split("---", 2)` unpack raises — that's fine to show, then send them back to the given path.
- `REPO_ROOT` is resolved from the installed package, so it works regardless of the kernel's cwd; if
  the path errors, the package isn't installed — re-run `uv sync`.
- The payoff line to say out loud: frontmatter `name`/`description` = the always-on catalog entry;
  the markdown body = what loads on demand. **This is the loader they built in Demo 3, for real.**

TIME: ~7 min. STRETCH: open `.claude/skills/generate-materials-from-roadmap/SKILL.md` — the skill
that generated *this very lesson* — and read its description as a trigger.

## L2206_lab problem 4

**Goal (written):** decide where a capability from their own agent lives.

COMMON GOTCHAS:
- Open-ended, so answers vary. Require all three: (1) a concrete capability, (2) a home, (3) a
  justification that uses "sometimes vs. always" and/or the token cost. An answer missing the
  justification is incomplete even if the home is right.

TIME: ~5 min.

## L2206_lab problem 5

**Goal (written):** name the "instructions in the system prompt" anti-pattern.

COMMON GOTCHAS:
- Students name the anti-pattern but skip the *cost* ("paid on every call") or the *fix* ("make it a
  skill"). Ask for all three — name, cost, fix — in the one-line answer.

TIME: ~4 min. STRETCH: ask for the *opposite* anti-pattern — a skill made for a one-line always-true
rule — and why that's just as wrong.
