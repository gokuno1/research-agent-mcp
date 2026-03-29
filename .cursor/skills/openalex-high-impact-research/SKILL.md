---
name: openalex-high-impact-research
description: Runs a structured literature workflow using OpenAlex MCP (high-citation shortlist with topic-aligned filters), extracts claims, generates hypotheses, detects contradictions, scores and refines, proposes structural study-design fixes, persists one run document to MongoDB. Use for literature review, high-impact paper shortlists, synthesis, hypotheses from papers, contradiction analysis, or saving research sessions to MongoDB.
---

# OpenAlex high-impact research workflow

## When to use

- The user wants **high-impact** papers and synthesis, not an unfiltered dump.
- They mention **OpenAlex**, **hypotheses**, **contradictions**, **scoring**, or **MongoDB** persistence.
- The task is **research reasoning on retrieved works**, with explicit provenance.

## How to invoke (no special slash command)

Cursor loads this skill from `.cursor/skills/` and may apply it when the **description** matches the task. There is **no separate built-in command** unless you add one (e.g. a [Cursor rule](https://docs.cursor.com/context/rules) or a team convention).

**Reliable triggers — paste or say one of:**

- “Run the **openalex-high-impact-research** skill for this question: …”
- “Use the project research workflow: OpenAlex high-impact retrieve → claims → hypotheses → contradictions → score → structural fixes → save to **research_agent.research_runs**.”
- “@openalex-high-impact-research” (if your Cursor build lists project skills in @-mention)

If the agent does not pick it up, **name the skill explicitly** in the first message so it is unambiguous.

## Topic filters: intent-gated (domain strictness)

- **Nothing is fixed to a single subfield.** The agent **infers** the best OpenAlex topic filters **from each input question** and records them in `inferredFilters`.
- **`primary_topic.subfield.id:1708`** in this file is an **example** (Computer Science → Hardware and Architecture). Use **`primary_topic.domain.id`**, **`primary_topic.field.id`**, **`primary_topic.subfield.id`**, and/or **`primary_topic.id`** (OpenAlex topic `T#####`) when the question fits — including **non–computer-science** domains (e.g. materials, mechanical/thermal engineering) when that matches the user’s intent.
- If the user **names** a field, subfield, or topic (or pastes an OpenAlex topic URL/ID), **prefer that** over guessing.
- After retrieval, run a **topic-fit gate** before final shortlist:
  - Keep works only if the title/primary topic clearly matches the user's intended domain.
  - Drop high-citation works that are cross-domain but not central to the asked problem.
  - If too few papers remain, relax query breadth **inside the same domain** before crossing domains.

### Domain drift guardrail (mandatory)

- Infer a **primary intent domain** from the question first (for example: software architecture, chip architecture, networking, biology).
- Build retrieval and screening around that domain, not just broad keyword overlap.
- Treat adjacent domains as **out-of-scope by default** unless the user explicitly requests them.

Example for app-latency queries:

- Input intent: "Event-driven architecture for low-latency applications" (software/application architecture).
- Reject by default: 5G, MEC, SDN-NFV, CloudSim, mobile-network slicing, wireless edge-telecom studies.
- Keep: event-driven software systems, broker/queue behavior, serialization, runtime scheduling, backpressure, tail-latency in application services.

## Preconditions

- **OpenAlex MCP** available (check tool descriptors under the workspace `mcps` folder for the OpenAlex server before calling tools).
- **MongoDB MCP** available for the final `insert-many` step.
- If abstracts are missing, proceed with **title/metadata-only** claims and lower `evidenceStrength`.

## Hard defaults (unless the user overrides in-chat)

- **Citation floor**: `cited_by_count:>100` in OpenAlex `filter`.
- **Topic alignment**: Infer the best OpenAlex filters from the question — typically `primary_topic.subfield.id`, `primary_topic.domain.id`, and/or `primary_topic.id` — and **combine** with the citation floor using comma-separated `filter` clauses.
- **Shortlist size**: **10–25** works, default sort `cited_by_count:desc`. Use `publication_year:2020-` (or similar) only when the user asks for **recent** work.
- **Mongo target**: database `research_agent`, collection `research_runs`. **One document per completed run.**

Full BSON shape and field meanings: [mongo-schema.md](mongo-schema.md)

---

## Pipeline (execute in order)

Copy and track:

```
Run progress:
- [ ] 1. Input Question
- [ ] 2. Retrieve (OpenAlex MCP)
- [ ] 3. Extract Claims
- [ ] 4. Generate Hypotheses
- [ ] 5. Detect Contradictions
- [ ] 6. Refine (pass 1)
- [ ] 7. Score
- [ ] 8. Structural failure analysis
- [ ] 9. Refine (pass 2)
- [ ] 10. Output + MongoDB insert
```

### 1. Input Question

- Restate as a **precision retrieval query** (`researchQuery.statement`).
- List **inclusions** and **exclusions** explicitly.
- Note implied **domain** (e.g., architecture vs materials) to drive topic filters.

### 2. Retrieve (OpenAlex MCP)

**Before any call:** read the JSON tool schemas for `openalex_search_works`, `openalex_get_work`, and any other tools you use.

**Search strategy**

1. From the question, identify:
   - **Primary intent domain** (must-have),
   - **Allowed adjacent domains** (optional),
   - **Explicit reject domains** (must-not-include).
2. Choose topic filters for the primary domain (**do not default to 1708** unless the question is clearly computer architecture / microarchitecture). Examples (illustrative only):
   - Computer architecture / microarchitecture: `primary_topic.subfield.id:1708` (Hardware and Architecture).
   - Software/application architecture: prefer topic/field filters that map to distributed systems, software architecture, and application performance (avoid telecom/networking/other fields unless requested).
   - When the question maps cleanly to a single OpenAlex topic: `primary_topic.id:T#####`.
   - Other disciplines: infer the appropriate `domains/fields/subfields` IDs from the question (or from user-supplied OpenAlex topic metadata).
3. Build `filter` (comma-separated, AND):
   - `cited_by_count:>100`
   - Topic clause(s) from step 1
   - Prefer `type:article` unless the user wants preprints or books
4. `search`: concise keywords or noun phrases from the question (not the entire essay).
5. Add **negative intent terms** in your screening logic from `researchQuery.exclusions` (for example: "5G", "MEC", "SDN", "network slicing", "CloudSim" when the user asks about software application latency).
6. `sort`: default `cited_by_count:desc`.
7. `per_page`: 10–25.
8. `select` (lean): `id,title,doi,publication_year,cited_by_count,primary_topic` for the list pass. If the API returns `abstract_inverted_index`, include it; otherwise batch `openalex_get_work` for the shortlist with `select` that requests abstract fields when supported.
9. **Mandatory shortlist screening pass** before synthesis:
   - Remove papers whose domain is primarily in reject domains.
   - Remove papers that only share generic terms (latency/performance) but not the target system context.
   - Keep an audit note in `refinementNotes.pass1` describing what was removed and why.

**Record** the exact `inferredFilters` object (search, filter, sort, per_page) for MongoDB provenance.

### 3. Extract Claims

For **each** shortlisted work:

- Produce **atomic** claims (one mechanism or finding per claim).
- Each claim **must** cite `workIds` (OpenAlex `https://openalex.org/W…`) and DOI in `shortlist`, not free-floating citations.
- `evidence`: short quote, abstract snippet, or “title-only inference” — label honestly.
- `evidenceStrength`: `high` (clear quote/abstract), `medium` (abstract-level), `low` (title/metadata only).

**Never invent** authors, venues, or findings not supported by retrieved metadata/text.

### 4. Generate Hypotheses

- **3–8** hypotheses; each must be **falsifiable** (what observation would undermine it?).
- Tag `status`: `supported` (strongly grounded in claims) vs `speculative`.
- Link `groundingClaimIds` to stable claim `id`s you assign.

### 5. Detect Contradictions

Compare claims and hypotheses. Classify each tension:

| `type` | Meaning |
|--------|---------|
| `direct_contradiction` | Same scope; incompatible conclusions |
| `scope_mismatch` | Different populations, workload, or hardware generation |
| `measurement_mismatch` | Metrics or definitions differ (power vs temp vs energy) |

Output `contradictions[]` with `summary` and `claimOrHypothesisRefs`.

### 6. Refine (pass 1)

- Merge duplicate claims; remove unsupported leaps.
- Narrow vague hypotheses; mark remaining uncertainty explicitly.

### 7. Score

Use a **0–10** scale (integers) for:

- `evidenceStrength` — how well the synthesis is backed by retrieved text
- `specificity` — precision of claims and hypotheses
- `reproducibility` — whether a reader could repeat the reasoning from cited works
- `topicFit` — alignment with the user question
- `contradictionSeverity` — how damaging unresolved tensions are (0 = none)
- `topicFit` must penalize domain drift; if shortlist contains mostly adjacent-domain papers, score `topicFit` low and re-run retrieval before finalizing.

Include `scores.notes` (short rationale). These score the **synthesis quality**, not the papers’ journal impact.

### 8. Structural failure analysis

Answer: **what structural changes could resolve synthesis failures or empirical gaps?**

Focus on **study / research design**, not polishing prose:

- definitions and operationalization
- control conditions and baselines
- separating confounds (e.g., power cap vs thermal cap)
- needed measurements or datasets
- scope boundaries (chip vs system vs workload suite)

Emit `structuralInterventions[]` with `failureMode` + `structuralChange`.

### 9. Refine (pass 2)

- Update hypotheses and scores after structural interventions.
- `refinementNotes.pass1` / `pass2`: bullet what changed.

### 10. Output + MongoDB

**User-facing output** — use this template:

```markdown
## Research summary
[researchQuery.statement]

## Shortlist (high-impact)
[Table or list: title, year, citations, OpenAlex ID, DOI]

## Claims
### C1 — [strength]
- **Claim:** …
- **Evidence:** …
- **Works:** …

## Hypotheses
### H1 — [supported|speculative]
- …

## Contradictions
- …

## Scores (0–10)
- evidenceStrength: …
- specificity: …
- reproducibility: …
- topicFit: …
- contradictionSeverity: …
**Rationale:** …

## Structural interventions
- …

## Refinement notes
- Pass 1: …
- Pass 2: …
```

**MongoDB insert (mandatory end step)**

1. Read `insert-many` schema from the MongoDB MCP tool descriptor.
2. Build **one** document matching [mongo-schema.md](mongo-schema.md); set `skillVersion` to `1.0`, `createdAt` to ISO UTC, embed `finalSummary` (can be the markdown report or a shortened executive summary).
3. Call `insert-many` with:
   - `database`: `research_agent`
   - `collection`: `research_runs`
   - `documents`: `[ <the run document> ]`
4. Confirm `insertedCount` / `insertedIds` to the user. If insert fails, report the error and keep the markdown output — do not claim persistence succeeded.

---

## Abstract handling

If OpenAlex returns `abstract_inverted_index`, **reconstruct** the abstract faithfully; if reconstruction is uncertain, state that the claim is abstract-level only. If no abstract is available, **do not** pretend full-text detail exists.

## Tool discipline

- Always **read MCP JSON descriptors** before calling tools.
- Never put secrets in `mcpProvenance` or user-visible summaries.
