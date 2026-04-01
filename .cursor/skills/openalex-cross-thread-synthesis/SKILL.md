---
name: openalex-cross-thread-synthesis
description: Decomposes a problem into sub-problems, discovers or accepts multiple research threads from different subfields within the same domain, retrieves high-impact papers per thread via OpenAlex MCP, extracts per-thread claims, runs cross-thread compatibility analysis, constructs an Integration Blueprint showing how threads combine into a unified solution, generates cross-thread hypotheses, scores, proposes structural fixes, and persists to MongoDB (research_agent.synthesis_runs). Use for combining research from multiple subfields to solve a problem, cross-thread synthesis, integration blueprints, multi-thread literature-driven solution design, or TigerBeetle-style research integration.
---

# Cross-Thread Research Synthesis (V2)

## When to use

- The user has a **problem to solve** and the solution likely requires combining insights from **multiple research subfields** within the same domain.
- The user mentions **combining research**, **integrating approaches**, **cross-thread**, **multi-subfield synthesis**, or describes a problem that requires pulling together different research lines.
- The TigerBeetle pattern: "pull together research from different subfields (e.g., consensus, quorums, recovery) into one coherent system/solution."

## When NOT to use (use V1 `openalex-high-impact-research` instead)

- The user wants a **single-topic literature review** (one subfield, one retrieval pass).
- The user wants a **shortlist of papers** on one topic with claims and hypotheses.
- There is no clear multi-subfield integration need.

In ambiguous cases, **ask the user** which workflow they want.

## How to invoke

**Reliable triggers — paste or say one of:**

- "Run the **cross-thread synthesis** skill for this problem: …"
- "Use V2: decompose → discover threads → retrieve per thread → compatibility → integration blueprint → save to **research_agent.synthesis_runs**."
- "Combine research from multiple subfields to solve: …"
- "I want a TigerBeetle-style integration of research threads for: …"
- "@openalex-cross-thread-synthesis" (if your Cursor build lists project skills in @-mention)

If the agent does not pick it up, **name the skill explicitly** in the first message.

## Auto-detection: V1 vs V2

The agent **auto-detects** which pipeline to run:

| Signal | Route to |
|--------|----------|
| "What does the literature say about X?" | V1 |
| "Find high-impact papers on X" | V1 |
| "How can I solve problem P by combining research?" | **V2** |
| "Integrate multiple research areas to build X" | **V2** |
| Problem statement that decomposes into 2+ distinct sub-problems requiring different subfield expertise | **V2** |
| Single-topic query, one subfield | V1 |

When uncertain, default to asking the user.

## Domain guardrail (mandatory)

- Identify a **single primary domain** from the problem (e.g., Computer Science, Biology, Materials Science, Mechanical Engineering).
- All threads must stay **within that domain** — they may span different **subfields** but not different **domains**.
- **Reject** threads that cross domain boundaries unless the user explicitly requests cross-domain synthesis.
- Use the OpenAlex hierarchy (domain → field → subfield → topic) to enforce this.

## Preconditions

- **OpenAlex MCP** available (check tool descriptors under the workspace `mcps` folder before calling tools).
- **MongoDB MCP** available for the final insert step.
- If abstracts are missing, proceed with **title/metadata-only** claims and lower `evidenceStrength`.

## Hard defaults (unless the user overrides in-chat)

- **Citation floor**: `cited_by_count:>100` per thread.
- **Thread limit**: up to **8** threads.
- **Works per thread**: **5–15**, default sort `cited_by_count:desc`. Use `publication_year:` filters only when the user asks for **recent** work.
- **Mongo target**: database `research_agent`, collection `synthesis_runs`. **One document per completed run.**

Full BSON shape and field meanings: [mongo-schema-v2.md](mongo-schema-v2.md)

---

## Pipeline (execute in order)

Copy and track:

```
Run progress:
- [ ] 1. Problem Intake & Decomposition
- [ ] 2. Thread Discovery or Acceptance
- [ ] 3. Per-Thread Retrieval (OpenAlex MCP)
- [ ] 4. Per-Thread Claim Extraction
- [ ] 5. Cross-Thread Compatibility Analysis
- [ ] 6. Integration Blueprint Construction
- [ ] 7. Cross-Thread Hypotheses
- [ ] 8. Scoring
- [ ] 9. Structural Failure Analysis
- [ ] 10. Refinement
- [ ] 11. Output + MongoDB insert
```

### 1. Problem Intake & Decomposition

- Restate the user's problem as a **clear problem statement** (`problemDecomposition.statement`).
- Identify the **primary domain** from the problem. Record it — all threads must stay within this domain.
- Decompose the problem into **2–8 sub-problems**. Each sub-problem describes a distinct capability, property, or constraint the solution must satisfy.
- Each sub-problem gets:
  - `id`: sp1, sp2, …
  - `description`: what needs to be solved
  - `requiredCapability`: what kind of research insight is needed

If the problem is too vague for decomposition, **ask the user for clarification** before proceeding.

**Example (TigerBeetle — for illustration across any domain):**

| ID | Description | Required capability |
|----|-------------|---------------------|
| sp1 | Database must automatically failover without manual intervention | Consensus algorithm for state-machine replication |
| sp2 | Deployment must tolerate partial cluster outages | Quorum flexibility allowing fewer nodes for commits |
| sp3 | System must remain available during and after recovery | Recovery protocol that doesn't block normal operations |

### 2. Thread Discovery or Acceptance

**Two modes — the agent auto-selects based on what the user provides:**

#### Mode A — User supplies threads

If the user provides explicit research threads or topics:

1. Accept them as-is.
2. Map each thread to one or more sub-problems from Step 1.
3. Validate that all threads fall within the **same domain**. If any thread crosses domain boundaries, **warn the user** and ask whether to proceed or substitute.
4. Assign each thread an `id` (t1, t2, …), record its `label`, `subfield`, `rationale`, `targetSubProblems`, and mark `source: "user-supplied"`.
5. Proceed directly to Step 3.

#### Mode B — Agent discovers threads

If the user provides only a problem statement (no explicit threads):

1. For each sub-problem, identify which research **subfields within the domain** could address it.
2. Propose **2–8 threads**, each with:
   - `label`: short descriptive name (e.g., "Viewstamped Replication", "Flexible Quorums")
   - `subfield`: the OpenAlex subfield or topic area
   - `rationale`: why this thread is relevant to the sub-problem (1–2 sentences)
   - `targetSubProblems`: which sub-problem(s) it addresses
3. **Present the proposed threads to the user in a clear table and wait for confirmation.**
4. The user may: confirm all, modify labels/rationale, add new threads, or remove proposed threads.
5. **Only proceed to Step 3 after explicit user confirmation.**

Mark agent-discovered threads as `source: "agent-proposed"`.

#### Thread quality checks (both modes)

- Every sub-problem must be addressed by **at least one thread**. Flag any uncovered sub-problem.
- If multiple threads address the same sub-problem, note the overlap — this is acceptable but should be documented.
- If all threads map to the same subfield, note that the problem may not require cross-thread synthesis. Suggest V1 as an alternative, but proceed if the user insists.

### 3. Per-Thread Retrieval (OpenAlex MCP)

**Before any call:** read the JSON tool schemas for `openalex_search_works`, `openalex_get_work`, and any other tools you plan to use.

For **each confirmed thread** (up to 8), execute a separate retrieval:

1. Infer the best OpenAlex topic filters for the thread's subfield. Use `primary_topic.subfield.id`, `primary_topic.field.id`, or `primary_topic.id` as appropriate — but all threads must share the same `primary_topic.domain.id`.
2. Build `filter` (comma-separated, AND):
   - `cited_by_count:>100`
   - Subfield or topic clause for this specific thread
   - Prefer `type:article` unless the user wants preprints
3. `search`: concise keywords specific to **this thread's focus**, not the overall problem statement.
4. `sort`: `cited_by_count:desc`.
5. `per_page`: 5–15 (use the lower end when thread count is high to keep total volume manageable).
6. `select` (lean): `id,title,doi,publication_year,cited_by_count,primary_topic` for the list pass. Batch `openalex_get_work` for abstracts when needed.
7. **Topic-fit screening** per thread: remove works that don't match the thread's subfield focus. Keep an audit note of what was removed and why.
8. Record `inferredFilters` per thread (search, filter, sort, per_page).

**Edge case — zero results for a thread:**
If a thread's retrieval returns zero usable papers after screening, flag it to the user. Options:
- Broaden the search terms (relax keywords, not the domain)
- Lower the citation floor for this thread only
- Replace the thread with a different one

**Domain enforcement:** if a thread's best papers are primarily from a different domain, flag this discrepancy and consult the user before including them.

### 4. Per-Thread Claim Extraction

For **each thread's** shortlisted works:

- Produce **atomic** claims (one mechanism or finding per claim).
- **Prefix claim IDs with thread ID**: `t1-c1`, `t1-c2`, `t2-c1`, `t2-c2`, etc. This prefix is critical for cross-thread traceability.
- Each claim **must** cite `workIds` (OpenAlex `https://openalex.org/W…`) from that thread's shortlist.
- `evidence`: short quote, abstract snippet, or "title-only inference" — label honestly.
- `evidenceStrength`: `high` (clear quote/abstract), `medium` (abstract-level), `low` (title/metadata only).
- **Focus claims on aspects relevant to the sub-problem** the thread is meant to address. Generic findings from a paper that don't relate to the sub-problem should be omitted.

**Never invent** authors, venues, or findings not supported by retrieved metadata/text.

### 5. Cross-Thread Compatibility Analysis

**This is a dedicated pipeline step — not folded into contradiction detection.**

#### 5a. Pairwise assessment

For every **pair** of threads (t1↔t2, t1↔t3, t2↔t3, …):

1. **Shared assumptions**: list assumptions both threads rely on (e.g., "both assume a synchronous model", "both require a central coordinator").
2. **Conflicts**: identify where one thread's assumptions contradict another's (e.g., "Thread A assumes total ordering; Thread B assumes eventual consistency").
3. **Integration feasibility**: can these threads' mechanisms coexist in a single solution?
   - `compatible` — no conflicts, can combine directly
   - `conditionally_compatible` — can combine with specific adaptations (document the conditions)
   - `incompatible` — fundamental conflict that cannot be resolved without replacing one thread
4. **Integration notes**: concretely describe how the two threads would interface — what output of one feeds into the other, what modifications each requires.

#### 5b. Global risks

Identify risks that emerge only when combining **3+ threads** simultaneously:
- Shared dependencies that multiple threads assume but that may not hold when combined
- Emergent complexity from layering multiple mechanisms
- Resource / performance / scalability concerns from the combination

#### 5c. Feasibility rating

Assign an overall feasibility: `high`, `medium`, or `low`.

- **high**: all pairs are compatible or conditionally compatible with minor adaptations.
- **medium**: some pairs have significant conditions, or one pair is incompatible but replaceable.
- **low**: multiple pairs are incompatible or global risks are severe.

If feasibility is `low`, **stop and flag this to the user** before proceeding. Suggest alternative threads or problem reframing. Only continue if the user explicitly chooses to proceed.

### 6. Integration Blueprint Construction

This is the **core deliverable** of V2 — the structured document showing how threads combine into a unified solution.

#### 6a. Sub-problem → Thread mapping

For each sub-problem from Step 1, document:

| Sub-problem | Thread(s) | Mechanism | Confidence |
|-------------|-----------|-----------|------------|
| sp1 | t1 | [specific mechanism from t1's claims that solves sp1] | strong / moderate / weak |

- **Confidence levels**:
  - `strong`: multiple high-evidence claims directly support the mechanism
  - `moderate`: claims support it but evidence is abstract-level or sparse
  - `weak`: thread is tangentially related; coverage is thin
- Flag any sub-problem with **no coverage** or only **weak** coverage — these are gaps in the solution.

#### 6b. Interface points

For each pair of threads that must interact in the combined solution:

- **Connection**: how one thread's output feeds into another's input, or how one modifies the other's behavior. Be specific — cite claim IDs.
- **Adaptation needed**: what modifications are required to make them work together. (e.g., "VR's fixed quorum size must be parameterized to accept Flexible Quorums' variable sizes — requires modifying VR's commit rule per t2-c3.")
- **Open questions**: unresolved integration issues that need further research or experimentation.

Not all thread pairs need interface points — only those whose mechanisms must interact in the combined solution.

#### 6c. Unified solution narrative

Write a **1–3 paragraph** description of the combined solution:

- How all threads fit together as a coherent whole
- The flow of control / data / logic across thread boundaries
- What emergent properties the combined solution has that no individual thread provides alone

This narrative is the "elevator pitch" for the integrated solution.

#### 6d. Novelty and limitations

- **Novelty over existing approaches**: what this combination achieves that existing single-thread or single-subfield approaches cannot. Be specific — compare to the state of the art.
- **Limitations**: known gaps, uncovered sub-problems, weak integration points, assumptions that need empirical validation.

### 7. Cross-Thread Hypotheses

Generate **3–8** hypotheses about the combined solution:

- Each hypothesis **must reference claims from at least two different threads** (this is the cross-thread requirement — single-thread hypotheses belong in V1).
- Each must be **falsifiable**: state what observation or experiment would undermine it.
- Tag `status`: `supported` (grounded in cross-thread claims with compatible evidence) vs `speculative` (plausible but without strong grounding).
- Link `groundingClaimIds` to claim IDs from Step 4 (e.g., `["t1-c2", "t3-c1"]`).

**Example:**
"Combining viewstamped replication (t1-c1) with flexible quorums (t2-c3) allows the system to maintain consensus with fewer than majority nodes, reducing failover time by >50% compared to standard VR. Falsifiable by: measuring failover latency with and without flexible quorum integration under identical failure scenarios."

### 8. Scoring

Use a **0–10** scale (integers):

| Metric | What it measures |
|--------|------------------|
| `evidenceStrength` | How well claims across all threads are backed by retrieved text |
| `threadCoverage` | Do threads cover all sub-problems? (10 = full, 0 = major gaps) |
| `integrationCoherence` | How well do threads fit together at interface points? (10 = seamless, 0 = incompatible) |
| `feasibility` | Practical implementability of the combined solution |
| `novelty` | How novel is the combination compared to existing single-subfield approaches? |
| `contradictionSeverity` | How damaging are unresolved cross-thread conflicts? (0 = none, 10 = fatal) |

Include `scores.notes` (short rationale). These score the **synthesis quality**, not individual paper impact.

**Automatic triggers:**
- `threadCoverage < 5` → flag uncovered sub-problems, suggest additional threads.
- `integrationCoherence < 4` → revisit compatibility analysis, consider thread replacement.
- `contradictionSeverity > 7` → warn the user the integration may not be viable.

### 9. Structural Failure Analysis

Answer: **what could fail when integrating these threads, and what structural changes would fix it?**

Focus on:

- **Assumption mismatches** between threads that weren't fully resolved in compatibility analysis
- **Missing interface specifications** — where two threads need to connect but no mechanism has been defined
- **Sub-problem gaps** — sub-problems with weak or no thread coverage
- **Scalability / generalization concerns** — does the integration hold under different scales, contexts, or conditions?
- **Empirical gaps** — what experiments, prototypes, or validations would confirm the integration works?

Emit `structuralInterventions[]`, each with:
- `failureMode`: what could go wrong
- `structuralChange`: what design-level change would prevent or fix it

### 10. Refinement

- Update hypotheses, blueprint, and scores based on structural interventions.
- `refinementNotes.pass1`: what changed after compatibility analysis and blueprint construction.
- `refinementNotes.pass2`: what changed after structural failure analysis.

### 11. Output + MongoDB insert

**User-facing output** — use this template:

```markdown
## Problem statement
[problemDecomposition.statement]

## Domain
[domain]

## Sub-problems
| ID | Description | Required capability |
|----|-------------|---------------------|
| sp1 | … | … |

## Research threads

### T1 — [label]
- **Subfield:** …
- **Rationale:** …
- **Addresses:** sp1, sp2
- **Source:** user-supplied | agent-proposed

#### Shortlist
[Table: title, year, citations, OpenAlex ID, DOI]

#### Claims
- **t1-c1** [strength]: …
- **t1-c2** [strength]: …

### T2 — [label]
(same structure)

## Cross-thread compatibility

### T1 ↔ T2
- **Feasibility:** compatible | conditionally_compatible | incompatible
- **Shared assumptions:** …
- **Conflicts:** …
- **Integration notes:** …

### Global risks
- …

### Overall feasibility: [high | medium | low]

## Integration Blueprint

### Sub-problem coverage
| Sub-problem | Thread(s) | Mechanism | Confidence |
|-------------|-----------|-----------|------------|
| sp1 | T1 | … | strong |

### Interface points
| Threads | Connection | Adaptation needed | Open questions |
|---------|-----------|-------------------|----------------|
| T1 ↔ T2 | … | … | … |

### Unified solution
[1–3 paragraphs describing how all threads combine into one coherent solution]

### Novelty over existing approaches
…

### Limitations
- …

## Cross-thread hypotheses

### H1 — [supported | speculative]
- …
- **Grounded in:** t1-c2, t3-c1
- **Falsifiable by:** …

## Scores (0–10)
- evidenceStrength: …
- threadCoverage: …
- integrationCoherence: …
- feasibility: …
- novelty: …
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
2. Build **one** document matching [mongo-schema-v2.md](mongo-schema-v2.md); set `skillVersion` to `2.0`, `createdAt` to ISO UTC, embed all per-thread data separately.
3. Call `insert-many` with:
   - `database`: `research_agent`
   - `collection`: `synthesis_runs`
   - `documents`: `[ <the run document> ]`
4. Confirm `insertedCount` / `insertedIds` to the user. If insert fails, report the error and keep the markdown output — do not claim persistence succeeded.

---

## Abstract handling

If OpenAlex returns `abstract_inverted_index`, **reconstruct** the abstract faithfully; if reconstruction is uncertain, state that the claim is abstract-level only. If no abstract is available, **do not** pretend full-text detail exists.

## Tool discipline

- Always **read MCP JSON descriptors** before calling tools.
- Never put secrets in `mcpProvenance` or user-visible summaries.
