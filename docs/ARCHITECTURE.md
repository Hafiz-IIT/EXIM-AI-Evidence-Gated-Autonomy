# Evidence-Gated Autonomy — Architecture

The core research object is an **action authorization gate**, not an autonomous customs system.

```mermaid
flowchart TD
    A[Documents / observations] --> B[Extraction]
    B --> C[Cross-source consistency]
    C --> D[Evidence quality]
    D --> E{Action-conditioned gate}
    E -->|sufficient evidence| F[ACT]
    E -->|verification needed| G[VERIFY]
    E -->|missing evidence| H[REQUEST EVIDENCE]
    E -->|uncertainty remains| I[DEFER]
    E -->|high-risk / unresolved conflict| J[ESCALATE]
```

Evidence quality considers provenance, freshness, source independence, conflicts and verification state.

## Boundary

This diagram describes the implemented research abstraction. It does not imply production customs automation, physical scanner integration, regulatory approval, human-subject validation or deployment.
