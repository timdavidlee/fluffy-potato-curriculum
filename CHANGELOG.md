## v0.9.1 (2026-07-04)

### Refactor

- **L01**: drive L01 client calls through the async achat seam

## v0.9.0 (2026-07-04)

### Feat

- **common**: add async twins to the potato_llm + common seams

## v0.8.0 (2026-07-04)

### Feat

- **L23**: generate stage-2 materials from roadmap

## v0.7.0 (2026-07-04)

### Feat

- **curriculum**: add L14 model/provider selection roadmap (#79)

## v0.6.0 (2026-07-04)

### Feat

- **L13**: re-point eval materials onto the L10 graph producer (#73)

## v0.5.0 (2026-07-04)

### Feat

- **L23**: add script-centric and shared example skills

## v0.4.0 (2026-07-04)

### Feat

- **L12**: re-point tracing materials onto the L10 graph producer (#71)

## v0.3.0 (2026-07-04)

### Feat

- **L13**: regenerate remaining eval materials, Langfuse-forward

## v0.2.0 (2026-07-03)

### Feat

- **local_ui**: lesson search filter and track badges
- **local_ui**: local FastAPI lesson viewer (#21)
- **curriculum**: generate L04/L05 stage-2 materials, split routing out of L04 (#18)
- **curriculum**: add common/ eval harness, L09/L12 materials, and nav CLAUDE.md files
- **curriculum**: add L20 Skills lesson roadmap (objectives + demos)
- **curriculum**: add L11 workflows lesson; renumber L11-L21 to L12-L22; finalize L08/L09/L11/L12 roadmaps
- **L02**: add lesson materials; make notebooks live-by-default via config seam
- add generate-materials-from-roadmap skill and L01 materials

### Fix

- **curriculum**: repair broken item-file refs; add L03 materials (#17)

### Refactor

- **common**: migrate agent loop + tools to LangChain (model-agnostic) (#19)
- **curriculum**: reorder lessons — graph block (L03–L05) early, 23→25 lessons (#16)
- **L01**: apply notebooks.md nav + split demos by concept
