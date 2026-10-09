# Architecture — brain-store

## Architecture Overview

```mermaid
flowchart TB
    Store["AlphaStore<br/>(OptionsStore alias)"]
    DB["OptionsDatabase"]
    PG[("PostgreSQL<br/>9 tables")]
    Files["JSON + CSV<br/>Offline Fallback"]

    Store -->|relational persistence| DB
    DB -->|psycopg_pool| PG
    Store -->|offline file fallback| Files
```

`OptionsDatabase` handles all SQL statements, transaction rollbacks, and connection pooling.
`AlphaStore` is the unified facade providing transparent fallback to local disk storage when `DATABASE_URL` is unavailable.
