# Architecture

```mermaid
flowchart LR
  S[Seeded synthetic source] --> E[Edge replay and SQLite]
  E --> F[Shared 12-feature extractor]
  F --> M[Local MLP inference]
  M --> D[Auditable decision policy]
  D --> U[React research console]
  U --> B[Manual feedback]
  B --> E
  C1[client-a process] --> A[Validated sample-weighted FedAvg]
  C2[client-b process] --> A
  C3[client-c process] --> A
  A --> G[Versioned safe tensor model]
  C1 --> P1[Persistent Opacus ledger]
  C2 --> P2[Persistent Opacus ledger]
  C3 --> P3[Persistent Opacus ledger]
```

Each client worker reads only its assigned five-subject synthetic partition. The experiment coordinator supplies identical safe-tensor weights, launches three separate Python processes, validates parameter keys/shapes/dtypes/finite values, and computes sample-weighted FedAvg. The browser reads edge history and aggregate experiment manifests from loopback APIs.
