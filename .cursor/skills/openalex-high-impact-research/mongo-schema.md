# MongoDB document: `research_agent.research_runs`

One document per completed workflow run. Insert via MongoDB MCP `insert-many` with a single-element `documents` array.

## Field glossary

| Field | Type | Description |
|--------|------|-------------|
| `createdAt` | string (ISO 8601) | UTC timestamp when the run finished |
| `skillVersion` | string | e.g. `1.0` — bump when this schema changes |
| `inputQuestion` | string | Raw user question |
| `researchQuery` | object | `statement`, `inclusions`, `exclusions` — clarified retrieval intent |
| `inferredFilters` | object | OpenAlex `filter`, `search`, `sort`, `per_page` actually used |
| `shortlist` | array | Summaries: `openalexId`, `title`, `doi`, `year`, `citedByCount`, `primaryTopic` |
| `claims` | array | Atomic claims with `text`, `evidence`, `evidenceStrength`, `workIds[]` |
| `hypotheses` | array | `text`, `status` (`supported` \| `speculative`), `groundingClaimIds` |
| `contradictions` | array | `id`, `type`, `summary`, `claimOrHypothesisRefs[]` |
| `scores` | object | Rubric outputs; see main skill |
| `structuralInterventions` | array | Design-level fixes for failure modes |
| `refinementNotes` | object | `pass1`, `pass2` — what changed and why |
| `finalSummary` | string | Markdown or plain-text executive summary |
| `mcpProvenance` | object | Safe summary of tool names + non-secret parameters |

## Example document (shape)

```json
{
  "createdAt": "2026-03-29T12:00:00.000Z",
  "skillVersion": "1.0",
  "inputQuestion": "How does dynamic thermal management interact with multicore scheduling?",
  "researchQuery": {
    "statement": "Peer-reviewed works on DTM/throttling and multicore thermal or power management with strong citation impact.",
    "inclusions": ["microprocessors/SoCs", "thermal or power caps", "multicore or CMP"],
    "exclusions": ["pure datacenter cooling infrastructure", "unrelated GPU-only papers unless clearly about chip DTM"]
  },
  "inferredFilters": {
    "search": "dynamic thermal management multicore",
    "filter": "cited_by_count:>100,primary_topic.subfield.id:1708,type:article",
    "sort": "cited_by_count:desc",
    "per_page": 15
  },
  "shortlist": [
    {
      "openalexId": "https://openalex.org/W2098228187",
      "title": "Dynamic thermal management for high-performance microprocessors",
      "doi": "https://doi.org/10.1109/hpca.2001.903261",
      "year": 2002,
      "citedByCount": 882,
      "primaryTopic": {
        "id": "https://openalex.org/T10054",
        "displayName": "Parallel Computing and Optimization Techniques"
      }
    }
  ],
  "claims": [
    {
      "id": "c1",
      "text": "Hardware/software can reduce temperature hotspots by adapting performance or scheduling under thermal constraints.",
      "evidence": "Title and abstract-level framing of DTM for microprocessors.",
      "evidenceStrength": "medium",
      "workIds": ["https://openalex.org/W2098228187"]
    }
  ],
  "hypotheses": [
    {
      "id": "h1",
      "text": "Workload migration reduces peak temperature more than uniform frequency scaling for similar throughput.",
      "status": "speculative",
      "groundingClaimIds": ["c1"]
    }
  ],
  "contradictions": [],
  "scores": {
    "evidenceStrength": 6,
    "specificity": 5,
    "reproducibility": 4,
    "topicFit": 8,
    "contradictionSeverity": 0,
    "notes": "Scores are 0–10; rationale belongs in refinement or final summary."
  },
  "structuralInterventions": [
    {
      "failureMode": "Ambiguous boundary between power vs thermal limiting",
      "structuralChange": "Separate experiments with fixed power budget vs fixed junction-temperature ceiling."
    }
  ],
  "refinementNotes": {
    "pass1": "Merged duplicate claims; flagged low-confidence abstract-only statements.",
    "pass2": "Adjusted hypothesis h1 after structural intervention note on measurement confounds."
  },
  "finalSummary": "…",
  "mcpProvenance": {
    "openalex": ["openalex_search_works", "openalex_get_work"],
    "mongodb": ["insert-many"]
  }
}
```

Do **not** store secrets (connection strings, API keys) in `mcpProvenance`.
