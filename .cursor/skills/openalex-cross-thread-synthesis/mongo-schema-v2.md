# MongoDB document: `research_agent.synthesis_runs`

One document per completed V2 cross-thread synthesis run. Insert via MongoDB MCP `insert-many` with a single-element `documents` array.

## Field glossary

| Field | Type | Description |
|-------|------|-------------|
| `createdAt` | string (ISO 8601) | UTC timestamp when the run finished |
| `skillVersion` | string | `2.0` — bump when this schema changes |
| `inputQuestion` | string | Raw user question / problem statement |
| `problemDecomposition` | object | Structured breakdown of the problem (see below) |
| `threads` | array | Per-thread retrieval results, claims, and metadata (see below) |
| `compatibilityAnalysis` | object | Pairwise and global compatibility assessment (see below) |
| `integrationBlueprint` | object | Core deliverable — sub-problem map, interface points, unified solution (see below) |
| `hypotheses` | array | Cross-thread hypotheses with `groundingClaimIds` spanning multiple threads |
| `scores` | object | Rubric outputs (see main skill) |
| `structuralInterventions` | array | Design-level fixes for integration failure modes |
| `refinementNotes` | object | `pass1`, `pass2` — what changed and why |
| `finalSummary` | string | Markdown or plain-text executive summary |
| `mcpProvenance` | object | Safe summary of tool names + non-secret parameters |

## Nested object schemas

### `problemDecomposition`

| Field | Type | Description |
|-------|------|-------------|
| `statement` | string | Clarified problem statement |
| `domain` | string | Primary domain (e.g., "Computer Science", "Biology") |
| `domainContext` | string | Why this domain was chosen; any scope notes |
| `subProblems` | array | List of sub-problems (see below) |

#### `subProblems[]`

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | `sp1`, `sp2`, … |
| `description` | string | What needs to be solved |
| `requiredCapability` | string | What kind of research insight is needed |

### `threads[]`

Each element represents one research thread with its own retrieval pass and claims.

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | `t1`, `t2`, … |
| `label` | string | Short descriptive name (e.g., "Viewstamped Replication") |
| `subfield` | string | OpenAlex subfield or topic area |
| `rationale` | string | Why this thread is relevant (1–2 sentences) |
| `targetSubProblems` | array of strings | Which sub-problem IDs this thread addresses (e.g., `["sp1"]`) |
| `source` | string | `"user-supplied"` or `"agent-proposed"` |
| `inferredFilters` | object | OpenAlex `filter`, `search`, `sort`, `per_page` used for this thread |
| `shortlist` | array | Works retrieved for this thread (see below) |
| `claims` | array | Claims extracted from this thread's works (see below) |

#### `threads[].shortlist[]`

| Field | Type | Description |
|-------|------|-------------|
| `openalexId` | string | `https://openalex.org/W…` |
| `title` | string | Work title |
| `doi` | string | DOI URL (if available) |
| `year` | integer | Publication year |
| `citedByCount` | integer | Citation count at retrieval time |
| `primaryTopic` | object | `{ id, displayName }` from OpenAlex |

#### `threads[].claims[]`

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Thread-prefixed: `t1-c1`, `t1-c2`, etc. |
| `text` | string | Atomic claim (one mechanism or finding) |
| `evidence` | string | Quote, abstract snippet, or "title-only inference" |
| `evidenceStrength` | string | `high`, `medium`, or `low` |
| `workIds` | array of strings | OpenAlex work IDs supporting this claim |

### `compatibilityAnalysis`

| Field | Type | Description |
|-------|------|-------------|
| `pairwiseAssessments` | array | One entry per thread pair (see below) |
| `globalRisks` | array of strings | Risks spanning 3+ threads |
| `feasibilityRating` | string | `"high"`, `"medium"`, or `"low"` |

#### `pairwiseAssessments[]`

| Field | Type | Description |
|-------|------|-------------|
| `threadPair` | array of strings | `["t1", "t2"]` |
| `sharedAssumptions` | array of strings | Assumptions both threads rely on |
| `conflicts` | array of strings | Where assumptions contradict |
| `feasibility` | string | `"compatible"`, `"conditionally_compatible"`, or `"incompatible"` |
| `integrationNotes` | string | How the two threads would interface |

### `integrationBlueprint`

| Field | Type | Description |
|-------|------|-------------|
| `subProblemMap` | array | Thread-to-sub-problem mapping (see below) |
| `interfacePoints` | array | Where threads connect (see below) |
| `unifiedSolution` | object | Combined solution narrative (see below) |

#### `subProblemMap[]`

| Field | Type | Description |
|-------|------|-------------|
| `subProblemId` | string | References `problemDecomposition.subProblems[].id` |
| `addressedByThreads` | array of strings | Thread IDs that address this sub-problem |
| `mechanism` | string | How the thread(s) solve this sub-problem (cite claim IDs) |
| `confidence` | string | `"strong"`, `"moderate"`, or `"weak"` |

#### `interfacePoints[]`

| Field | Type | Description |
|-------|------|-------------|
| `between` | array of strings | Thread IDs (e.g., `["t1", "t2"]`) |
| `connection` | string | How one thread's output feeds into the other |
| `adaptationNeeded` | string | Modifications required for integration |
| `openQuestions` | array of strings | Unresolved integration issues |

#### `unifiedSolution`

| Field | Type | Description |
|-------|------|-------------|
| `summary` | string | 1–3 paragraph description of the combined solution |
| `noveltyOverExisting` | string | What the combination achieves beyond individual threads |
| `limitations` | array of strings | Known gaps, weak points, untested assumptions |

### `hypotheses[]`

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | `h1`, `h2`, … |
| `text` | string | Cross-thread hypothesis (must reference 2+ threads) |
| `status` | string | `"supported"` or `"speculative"` |
| `groundingClaimIds` | array of strings | Claim IDs from multiple threads (e.g., `["t1-c2", "t3-c1"]`) |
| `falsifiableBy` | string | What observation would undermine this hypothesis |

### `scores`

| Field | Type | Description |
|-------|------|-------------|
| `evidenceStrength` | integer (0–10) | How well claims are backed by text across all threads |
| `threadCoverage` | integer (0–10) | Do threads cover all sub-problems? |
| `integrationCoherence` | integer (0–10) | How well threads fit together at interface points |
| `feasibility` | integer (0–10) | Practical implementability of the combined solution |
| `novelty` | integer (0–10) | Novelty of the combination vs existing approaches |
| `contradictionSeverity` | integer (0–10) | Damage from unresolved cross-thread conflicts (0 = none) |
| `notes` | string | Short rationale for scores |

### `structuralInterventions[]`

| Field | Type | Description |
|-------|------|-------------|
| `failureMode` | string | What could go wrong in the integration |
| `structuralChange` | string | Design-level change to prevent or fix it |

### `refinementNotes`

| Field | Type | Description |
|-------|------|-------------|
| `pass1` | string | Changes after compatibility analysis and blueprint construction |
| `pass2` | string | Changes after structural failure analysis |

---

## Example document (shape)

```json
{
  "createdAt": "2026-04-01T12:00:00.000Z",
  "skillVersion": "2.0",
  "inputQuestion": "Build a reliable financial database with automatic failover, outage tolerance, and availability during recovery",
  "problemDecomposition": {
    "statement": "Design a database system that guarantees automatic failover, tolerates partial cluster outages in deployment, and remains available during recovery — combining research from distributed systems subfields.",
    "domain": "Computer Science",
    "domainContext": "The problem is fundamentally about distributed systems reliability for database infrastructure.",
    "subProblems": [
      {
        "id": "sp1",
        "description": "Database must automatically failover without manual intervention",
        "requiredCapability": "Consensus algorithm for state-machine replication"
      },
      {
        "id": "sp2",
        "description": "Deployment must tolerate partial cluster outages without full quorum",
        "requiredCapability": "Quorum flexibility allowing fewer nodes for commits"
      },
      {
        "id": "sp3",
        "description": "System must remain available during and after node recovery",
        "requiredCapability": "Recovery protocol that does not block normal operations"
      }
    ]
  },
  "threads": [
    {
      "id": "t1",
      "label": "Viewstamped Replication",
      "subfield": "Distributed Computing / Consensus Protocols",
      "rationale": "Provides the base consensus protocol for state-machine replication with automatic leader election and failover.",
      "targetSubProblems": ["sp1"],
      "source": "user-supplied",
      "inferredFilters": {
        "search": "viewstamped replication consensus",
        "filter": "cited_by_count:>100,primary_topic.subfield.id:1705,type:article",
        "sort": "cited_by_count:desc",
        "per_page": 10
      },
      "shortlist": [
        {
          "openalexId": "https://openalex.org/W_EXAMPLE_1",
          "title": "Viewstamped Replication Revisited",
          "doi": "https://doi.org/10.example/vr-revisited",
          "year": 2012,
          "citedByCount": 450,
          "primaryTopic": {
            "id": "https://openalex.org/T10XXX",
            "displayName": "Distributed Consensus Protocols"
          }
        }
      ],
      "claims": [
        {
          "id": "t1-c1",
          "text": "VR provides automatic leader election and state transfer, enabling failover without manual intervention in replicated state machines.",
          "evidence": "Abstract-level description of the VR protocol's leader election mechanism.",
          "evidenceStrength": "medium",
          "workIds": ["https://openalex.org/W_EXAMPLE_1"]
        }
      ]
    },
    {
      "id": "t2",
      "label": "Flexible Quorums",
      "subfield": "Distributed Computing / Quorum Systems",
      "rationale": "Decouples read and write quorum sizes, allowing the system to commit with fewer nodes and tolerate more failures in deployment.",
      "targetSubProblems": ["sp2"],
      "source": "user-supplied",
      "inferredFilters": {
        "search": "flexible quorums consensus",
        "filter": "cited_by_count:>50,primary_topic.subfield.id:1705,type:article",
        "sort": "cited_by_count:desc",
        "per_page": 10
      },
      "shortlist": [],
      "claims": [
        {
          "id": "t2-c1",
          "text": "Flexible Paxos shows that the leader quorum and accept quorum need only intersect, not individually form majorities, enabling deployments with fewer nodes required for commits.",
          "evidence": "Title and abstract of Flexible Paxos paper.",
          "evidenceStrength": "medium",
          "workIds": ["https://openalex.org/W_EXAMPLE_2"]
        }
      ]
    },
    {
      "id": "t3",
      "label": "Protocol-Aware Recovery",
      "subfield": "Distributed Computing / Fault Recovery",
      "rationale": "Tailors the recovery protocol to the specific consensus protocol in use, avoiding unnecessary blocking during recovery.",
      "targetSubProblems": ["sp3"],
      "source": "user-supplied",
      "inferredFilters": {
        "search": "protocol aware recovery consensus",
        "filter": "cited_by_count:>50,primary_topic.subfield.id:1705,type:article",
        "sort": "cited_by_count:desc",
        "per_page": 10
      },
      "shortlist": [],
      "claims": [
        {
          "id": "t3-c1",
          "text": "Protocol-aware recovery exploits knowledge of the consensus protocol to recover state without blocking the critical path of normal operation.",
          "evidence": "Title-only inference.",
          "evidenceStrength": "low",
          "workIds": ["https://openalex.org/W_EXAMPLE_3"]
        }
      ]
    }
  ],
  "compatibilityAnalysis": {
    "pairwiseAssessments": [
      {
        "threadPair": ["t1", "t2"],
        "sharedAssumptions": ["Both assume a message-passing distributed system with crash-recovery failure model"],
        "conflicts": ["VR uses fixed majority quorums; Flexible Quorums requires parameterizing quorum sizes"],
        "feasibility": "conditionally_compatible",
        "integrationNotes": "VR's commit rule must be modified to accept variable quorum sizes per Flexible Quorums. The intersection property must be maintained."
      },
      {
        "threadPair": ["t1", "t3"],
        "sharedAssumptions": ["Both operate on replicated state machines with deterministic execution"],
        "conflicts": [],
        "feasibility": "compatible",
        "integrationNotes": "PAR directly targets the recovery phase of consensus protocols like VR. It replaces VR's default recovery with a protocol-specific optimized path."
      },
      {
        "threadPair": ["t2", "t3"],
        "sharedAssumptions": ["Both modify aspects of the consensus protocol without changing its safety guarantees"],
        "conflicts": ["Flexible quorum sizes may affect recovery: recovering node must know which quorum configuration was active"],
        "feasibility": "conditionally_compatible",
        "integrationNotes": "Recovery protocol must be aware of the flexible quorum configuration to correctly reconstruct state from the right set of replicas."
      }
    ],
    "globalRisks": [
      "All three modifications layer on top of VR — compounding changes may introduce subtle correctness bugs that only manifest under specific failure sequences."
    ],
    "feasibilityRating": "medium"
  },
  "integrationBlueprint": {
    "subProblemMap": [
      {
        "subProblemId": "sp1",
        "addressedByThreads": ["t1"],
        "mechanism": "VR provides leader election and state-machine replication for automatic failover (t1-c1).",
        "confidence": "strong"
      },
      {
        "subProblemId": "sp2",
        "addressedByThreads": ["t2"],
        "mechanism": "Flexible Quorums decouples quorum sizes so commits require fewer nodes, tolerating partial outages (t2-c1).",
        "confidence": "moderate"
      },
      {
        "subProblemId": "sp3",
        "addressedByThreads": ["t3"],
        "mechanism": "PAR replaces generic recovery with protocol-specific recovery that does not block normal operations (t3-c1).",
        "confidence": "moderate"
      }
    ],
    "interfacePoints": [
      {
        "between": ["t1", "t2"],
        "connection": "VR's fixed majority quorum in the commit rule is replaced by Flexible Quorums' parameterized intersection requirement.",
        "adaptationNeeded": "VR's prepare and commit phases must accept configurable quorum sizes while preserving the intersection property for safety.",
        "openQuestions": ["What is the optimal quorum configuration for a 5-node financial database cluster?"]
      },
      {
        "between": ["t1", "t3"],
        "connection": "VR's recovery sub-protocol is replaced by PAR's optimized recovery that leverages knowledge of VR's log structure.",
        "adaptationNeeded": "PAR must be implemented specifically for VR's log format and state-transfer mechanism.",
        "openQuestions": ["Does PAR's recovery maintain correctness under concurrent flexible quorum reconfigurations?"]
      }
    ],
    "unifiedSolution": {
      "summary": "The combined system uses Viewstamped Replication as the consensus backbone for automatic failover (sp1). The VR commit rule is modified per Flexible Quorums to allow commits with fewer replicas, tolerating partial cluster outages without losing availability (sp2). The recovery phase is replaced by Protocol-Aware Recovery, which exploits VR's log structure to recover nodes without blocking the consensus critical path (sp3). Together, this produces a database replication layer that fails over automatically, tolerates deployment-level outages beyond what standard majority quorums allow, and recovers crashed nodes without service interruption — properties that no individual research thread provides alone.",
      "noveltyOverExisting": "Standard VR requires majority quorums (limiting outage tolerance) and uses generic recovery (blocking during state transfer). The integration achieves flexible outage tolerance AND non-blocking recovery on top of the same consensus protocol — a combination not present in any single published system.",
      "limitations": [
        "Correctness of the three-way integration has not been formally verified.",
        "Flexible quorum reconfigurations during PAR recovery are an open research question.",
        "Performance impact of the combined modifications under high-throughput financial workloads is untested."
      ]
    }
  },
  "hypotheses": [
    {
      "id": "h1",
      "text": "Combining VR with Flexible Quorums and PAR enables a financial database to survive any single-node failure with zero downtime and recover crashed nodes without blocking transactions.",
      "status": "speculative",
      "groundingClaimIds": ["t1-c1", "t2-c1", "t3-c1"],
      "falsifiableBy": "Demonstrate a failure scenario where the three-way integration blocks transactions during recovery or loses committed data."
    }
  ],
  "scores": {
    "evidenceStrength": 5,
    "threadCoverage": 9,
    "integrationCoherence": 7,
    "feasibility": 6,
    "novelty": 8,
    "contradictionSeverity": 3,
    "notes": "Thread coverage is strong (each sub-problem has a dedicated thread). Integration coherence is good but two pairs are only conditionally compatible. Evidence is moderate — most claims are abstract-level. Novelty is high as this specific combination is not found in a single published work."
  },
  "structuralInterventions": [
    {
      "failureMode": "Flexible quorum reconfiguration during PAR recovery may violate safety",
      "structuralChange": "Freeze quorum configuration during recovery; require reconfiguration to wait until all recovering nodes have caught up."
    }
  ],
  "refinementNotes": {
    "pass1": "Identified conditional compatibility between t2 and t3 — added open question about concurrent reconfiguration.",
    "pass2": "Added structural intervention to freeze quorum config during recovery. Adjusted feasibility score from 7 to 6."
  },
  "finalSummary": "…",
  "mcpProvenance": {
    "openalex": ["openalex_search_works", "openalex_get_work"],
    "mongodb": ["insert-many"]
  }
}
```

Do **not** store secrets (connection strings, API keys) in `mcpProvenance`.
