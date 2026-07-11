# Build the agent, not the prompt

```yaml
title: Build the agent, not the prompt
keywords: course intro, ai agents, overview, tool calling, langgraph, langfuse, tracing, evaluation, shallow agent, capstone, why agents, what you build
estimated duration: 12
```

> **L00 — the course front door.** This is the overview deck: what this course is, what you'll
> build, and why it's worth your ~30 hours. It is not a taught lesson (no lab, no roadmap) — it's
> the pitch. You already *use* AI every day; by the end of this course you'll be able to *build the
> agent underneath it* — design its tools, wire its loop, trace it, and prove it works. The full
> plan lives in the [syllabus](../SYLLABUS.md); the course proper starts at the K-series prework,
> then L01.

cover-diagram: two stacked visuals on the right of the cover. **Top — a short "who's talking"
transcript** that grounds *model vs. tool* for anyone new to the idea that an AI calls tools: `you`
asks "How many more people live in Tokyo than Paris?"; `model` (a cyan chip — the decider) replies
"I'll look those up: `lookup("Tokyo"), lookup("Paris")`"; `tool` (a neutral outlined chip — the
plumbing) returns `37,000,000 · 11,000,000`; `model` answers "Tokyo has about **26M more** people
than Paris." A one-line legend reads *model = the AI that decides & replies · tool = code it calls
for real facts*. **Bottom — the compact agent loop** (the slide-1.3 motif): a cyan `model (decides)`
node and `tool (runs)` node joined by a "calls a tool" forward edge and an animated cyan back-edge
"loops until done", with a `done → END` exit. The transcript is the concrete grounding; the loop is
the abstraction it illustrates.

## section 1. Why agents, and why you

### slide 1.1 You use AI every day. Could you build the thing underneath?

- Anyone can *prompt* a chatbot. Who can build the **agent** that calls tools, loops, and gets
  real work done?
- This isn't a "prompting tips" course. It's an engineering course: you'll write typed Python,
  wire real control flow, call real models, and ship something that runs.
- Can you write functions? Can you call APIs? Do you understand JSON contracts? Then you can learn
  **agent engineering**.
- diagram: a wide contrast — a large ink-faint field of chat-bubble figures labeled "everyone: uses
  AI" on the left, and a single small cyan node labeled "you: builds the agent underneath" on the
  right, a cyan arrow crossing the gap between them tagged "this course." The point is the gap: most
  people ride on top; you'll build what they ride on.

### slide 1.2 From "prompting a chatbot" to "shipping an agent"

- **What is an agent?** An **AI call** takes one prompt and returns one answer — it can't *act* on
  the world. An **agent** wraps that model in a loop with **tools**, so it can decide, act, check
  the result, and repeat until the job is done.
- That's the two columns below: a flat chatbot call vs. an agent's stack — **tools** to act,
  **control flow** to decide, **traces** to see what it did, **evals** to prove it still works
  tomorrow. Every one is a lesson here, and the gap between them is the distance this course covers.
- And that distance is the skill teams are hiring for right now — taking a model from "impressive
  demo" to "thing we can trust in a workflow."
- diagram: a two-column ladder. Left column "prompt a chatbot" — a single ink-faint `request →
  response` pair, flat. Right column "ship an agent" — a taller cyan stack: `tools · control flow ·
  memory · tracing · evaluation`, each rung a labeled block. A cyan arrow spans left→right captioned
  "the course is the gap between them."

### slide 1.3 An agent isn't magic — it's a loop you'll wire by hand

- Strip away the hype and an agent is one small loop: the **model** decides, a **tool** runs, the
  result comes back, and the loop repeats until the job is done. That's it.
- No black boxes. Build the loop **node by node** in LangGraph, then understand what `create_agent`
  and `create_deepagent` do under the hood.
- Once you can see the loop, agents stop being intimidating and start being *designable*.
- diagram: an SVG cycle — `model (decide)` → a diamond `tool call needed?` → `run tool` → `observe
  result` → a cyan **back-edge** returning to `model`, with a separate `done → END` branch leaving
  the loop. The whole cycle in cyan (the happy path), the back-edge emphasized and labeled "the one
  edge that makes it an agent." Caption: this exact loop is what you build in L10.

### slide 1.4 Here's an agent. Six lines.

- This is a real, running agent — a model, two tools, and the loop that lets it **decide for
  itself**. Not a teaching toy: it's the exact one-line `create_agent` you build in L11.
- Ask it a plain question and *you* wrote none of the steps — it chooses to look each city up,
  subtract with the calculator, then answer. That choosing is the whole idea of an agent.
- If these six lines feel within reach, so is the course — you'll be writing them yourself within
  the first few lessons.

```python
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from fluffy_potato_curriculum.common.tools import calculator, lookup

model = init_chat_model("anthropic:claude-sonnet-4-6")   # key via the config seam
agent = create_agent(model, [calculator, lookup])        # ← the whole agent, one line

result = await agent.ainvoke(
    {"messages": [{"role": "user",
                   "content": "How many more people live in Tokyo than Paris?"}]}
)
print(result["messages"][-1].content)
```

- diagram: a two-pane "editor + run" mock. **Left pane:** the six-line snippet above in mono, with
  `create_agent(model, [calculator, lookup])` highlighted cyan and tagged "the whole agent — one
  line." **Right pane:** the agent's *own* trace as a small stack it chose step by step —
  `model → lookup("Tokyo")` → `37000000`, `model → lookup("Paris")` → `11000000`,
  `model → calculator("37000000 - 11000000")` → `26000000`, then a bright cyan final row
  `answer → "Tokyo has about 26M more people than Paris."` The three tool-call rows in cyan (the
  model's self-chosen steps), the pane tagged "illustrative run." Caption: you wrote six lines; the
  model chose those three steps itself — that's the agent.

### slide 1.5 The same six lines, grown up

- You never *outgrow* `create_agent` — you just hand it more. Same one-line constructor, more
  config: extra tools, a system prompt, skills it loads on demand, a guardrail around the loop.
- Every new line here is a **lesson you'll take** — this slide is a map of the course, written as
  one function call.
- Nothing here is exotic. By the end you'll assemble this yourself, piece by piece, on the exact
  agent from the last slide.

```python
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from fluffy_potato_curriculum.common.tools import calculator, lookup, web_search
from fluffy_potato_curriculum.common.skills import list_skills, load_skill  # L22–L23
from fluffy_potato_curriculum.common.guards import budget_guard            # L16

model = init_chat_model("anthropic:claude-sonnet-4-6")

agent = create_agent(
    model,
    tools=[calculator, lookup, web_search,   # more tools — you design these  (L07–L08)
           list_skills, load_skill],          # + skills it loads on demand    (L22–L23)
    system_prompt=SKILL_CATALOG,             # who it is + the skill menu      (L02, L22)
    middleware=[budget_guard],               # a guardrail around the loop     (L16)
)
```

- diagram: a "grows into" pair. **Left:** the slide-1.4 six-line snippet, faint and small, tagged
  a cyan `L11`. A cyan arrow labeled "grows into" crosses to the **right:** the expanded
  `create_agent(...)` call, each added argument joined by a thin cyan leader line to a small lesson
  chip — `tools → L07–08`, `list_skills/load_skill → L22–23`, `system_prompt → L02`,
  `middleware → L16`. The constructor name `create_agent` is highlighted identically in both panes
  to make the point that *it doesn't change*. Caption: same constructor, more config — every added
  line is a lesson you'll take.

## section 2. What you'll learn & practice

### slide 2.1 Five things you'll be able to *do* — not just know about

- These are your five **takeaways**, and they're all **verbs**: things you can point to and say "I
  built that," not topics you can recite.
- Everything in the syllabus ladders up to one of these five.
- table: the five takeaways you leave with.

| Takeaway | What that means concretely |
| --- | --- |
| Design a tool for an agent | name it, schema its inputs/outputs, handle its errors |
| Build a directed LLM pipeline | typed nodes + fixed & conditional edges — you control the path |
| Build a free-form agent | a customized, model-driven agent that drives its own tools |
| Measure what an agent does | read its state, logs, traces & extracts; evaluate the quality |
| Ship a hackathon project | an end-to-end app: your agent + a UI + a provided database |

### slide 2.2 You ship one real project, end to end

- The course closes with a **hackathon capstone**: you consolidate everything into one shippable
  project — your **agent**, a **UI**, and a **provided database** — built end to end.
- The skills stack into one build: **design a tool → wire the agent loop → trace the run →
  evaluate it**, wrapped in something you can actually demo.
- Not a toy notebook you throw away. It runs on the same real stack the lessons use, and the code
  is **yours to keep**, extend, and show off.
- diagram: a four-stage SVG pipeline in cyan — `design a tool` → `wire the agent loop` → `trace the
  run` → `evaluate it` — the four stages feeding into a final rounded node labeled "a hackathon
  project: agent + UI + database." Each stage tagged with the lesson it comes from. Caption: the
  capstone is the whole course, shipped as one project.

### slide 2.3 Not 25 disconnected topics — six coherent themes

- This isn't a pile of unrelated lessons. All 25 organize into **six themes**, each touched by
  several lessons that build on the last — so you're always extending something you already
  understand.
- The **mini track** is a focused slice through these six; the **full track** covers them all.
- diagram: a 2×3 grid of six cyan theme cards, each with the theme name, a one-line descriptor, and
  its lesson range — **LLM foundations** (tokens, context, cost, prompting · L01–L02) ·
  **Orchestration** (graphs, the agent loop, patterns, multi-agent · L03–L24) · **Tool ecosystem**
  (the tool-call protocol, tool design, MCP · L07–L09) · **Agent instruction & guidance**
  (chain-of-thought, skills, middleware · L06, L16, L22–L23) · **Agents & outside systems** (memory,
  context management, embeddings, RAG · L18–L21) · **Budgets & performance** (cost/latency, model
  choice, tracing & eval · L01, L12–L14, L25). Caption: six themes tie the whole course together —
  the mini track is a slice, the full track the whole map.

## section 3. How you'll learn it — and how to start

### slide 3.1 Real tools and real model calls, from lesson one

- You learn on the stack working engineers actually ship with: **Claude** models through a thin
  provider seam, **LangGraph** for the agent graph, **Langfuse** for tracing and evals, **Docker**
  and **uv** to run it all locally. No made-up teaching framework you'll never touch again — every
  tool here is one you can put on a résumé.
- It's hands-on from the very first notebook: you call a **real model** in lesson one and read the
  actual token receipt — not a screenshot of one. Labs are built to be **broken on purpose** (push
  a prompt until it fails, then fix it), because that's how the ideas stick.
- Calls stay small and cheap — cents, not dollars — and everything runs on your machine, so you can
  experiment freely.
- diagram: two paired panels. Left, a chip row of the real stack — `Claude` (model) · `LangGraph`
  (agent graph) · `Langfuse` (traces + evals) · `Docker` + `uv` (runs it locally), each a cyan CSS
  block with its one-word role. Right, an SVG of one live cell — `notebook cell → real model call →
  answer + usage receipt` in cyan, with a small coral side-loop "break it → watch it fail → fix it."
  Caption: real tools, real calls, safe to experiment.

### slide 3.2 Is this you? Prereqs, prework, and two ways to take it

- **Who it's for:** semi-technical builders with basic Python — functions, classes, types, calling
  an API. No ML background, no math required.
- **Everyone starts level.** A gated **prework** track (K01–K06) gets your environment, keys, and
  the Docker stack working *before* L01, so the whole cohort begins from one baseline.
- **Two ways to take it:** a focused **mini track** (13 lessons + the capstone, ~32 hours, anchored
  on the five student takeaways) or the **full track** all the way to multi-agent systems and RAG.
- diagram: a branching SVG — a single cyan **prework gate** `K01–K06` on the left (tagged "everyone
  starts here") feeding forward into two labeled tracks: `Mini · 13 lessons + capstone · ~32 hrs`
  and `Full · through multi-agent + RAG`. Both branches in cyan. Caption: one on-ramp, two
  destinations.

### slide 3.3 You've used the tools. Time to build the thing that uses the tools.

- You came in able to prompt a model. You'll leave able to design its tools, wire its loop, trace
  its runs, and prove it works — an agent you built and understand top to bottom.
- Every lesson moves you one step along that line; the capstone is where it all comes together.
- diagram: a before→after transformation arc — a left node in ink-faint "day one: you prompt a
  model" and a cyan arrow sweeping right into a bright node "by the end: you design, wire, trace &
  evaluate an agent," small lesson tick-marks along the arc. Caption: same you, a much bigger toolbox.

### slide 3.4 What it takes: format, time, and what to bring

- **Format:** proctor-led and cohort-based — each lesson is a short lecture, then a hands-on lab you
  work through yourself, in ~15-minute focused segments.
- **Time:** the **mini track** runs ~32 hours end to end (about 23 h of pure build time plus breaks
  and Q&A); the **full track** goes longer, all the way through multi-agent systems and RAG.
- **What you need day one:** a laptop that runs **Docker** and an **API key** — the K-prework gets
  both working before L01, and lab calls stay in the **cents, not dollars**.
- **Start here:** clear the K-series prework, then join L01 with your cohort.
- diagram: this is the deck's **closing slide** — a one-line closing statement ("Ready when you are:
  clear the K-prework, then start L01") above a three-column grid — **Format** (proctor-led · lecture
  + lab · cohort · ~15-min segments) · **Time** (mini ~32 h · full longer) · **What you need** (a
  Docker-capable laptop + an API key · the prework sets it up). The "Start here" statement in cyan as
  the call to action; the three columns in ink-faint. Caption: here's exactly what starting looks like.
