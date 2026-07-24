# Microsoft GraphRAG Indexing Pipeline — Full Explanation

**Author's note**: This document explains each workflow in the Microsoft GraphRAG indexing pipeline, using the Synthea FHIR healthcare demo as a running example.

**Prepared**: Monday, July 13, 2026 · Raleigh, NC

---

## Table of Contents

- [Overview](#overview)
- [The 10 Workflows in Order](#the-10-workflows-in-order)
  - [1. load_input_documents](#1-load_input_documents)
  - [2. create_base_text_units](#2-create_base_text_units)
  - [3. create_final_documents](#3-create_final_documents)
  - [4. extract_graph — The Big One](#4-extract_graph--the-big-one)
  - [5. finalize_graph](#5-finalize_graph)
  - [6. extract_covariates — Disabled in Your Config](#6-extract_covariates--disabled-in-your-config)
  - [7. create_communities](#7-create_communities)
  - [8. create_final_text_units](#8-create_final_text_units)
  - [9. create_community_reports — Second Big Cost](#9-create_community_reports--second-big-cost)
  - [10. generate_text_embeddings](#10-generate_text_embeddings)
- [Cost & Time Breakdown for a 100-Patient Run](#cost--time-breakdown-for-a-100-patient-run)
- [What Gets Written to Disk](#what-gets-written-to-disk)
- [How Workflows Feed Each Search Method](#how-workflows-feed-each-search-method)
- [End-to-End Example](#end-to-end-example)
- [Key Takeaways](#key-takeaways)

---

## Overview

GraphRAG is a **linear pipeline** where each workflow reads outputs from the previous one, transforms them, and passes them forward. Think of it like an ETL job that turns raw text into a queryable knowledge graph.

```text
Raw text files
     |
     v
[1] load_input_documents
     |
     v
[2] create_base_text_units
     |
     v
[3] create_final_documents
     |
     v
[4] extract_graph            <-- most expensive
     |
     v
[5] finalize_graph
     |
     v
[6] extract_covariates       <-- disabled for you
     |
     v
[7] create_communities
     |
     v
[8] create_final_text_units
     |
     v
[9] create_community_reports <-- second-most expensive
     |
     v
[10] generate_text_embeddings
     |
     v
Queryable GraphRAG index
```

---

## The 10 Workflows in Order

### 1. `load_input_documents`

**What it does**: Reads `.txt` files from `graphrag_workspace/input/`, parses each file's metadata (filename, size, encoding), and creates one Document record per file.

**Input**: `graphrag_workspace/input/patient_0000.txt` (and 99 more)

**Output**: A pandas DataFrame stored as `output/documents.parquet` with columns:

- `id` — unique document ID
- `title` — filename
- `text` — full text content
- `metadata` — any file-level metadata

| Aspect | Value |
|---|---|
| LLM calls | Zero |
| Cost impact | Free |
| Speed | Very fast — a few seconds for 100 files |

**Common failures**:

- Empty `input/` folder
- Unsupported file encoding
- Corrupted or unreadable files

---

### 2. `create_base_text_units`

**What it does**: Chunks each document into smaller, overlapping text pieces. Chunks are the fundamental unit of processing for the rest of the pipeline.

**Why chunking matters**:

- LLMs have context limits
- Smaller chunks give more granular citation and retrieval
- Smaller chunks mean each LLM call has fewer input tokens

**How it works**: Uses the `chunking:` config from `settings.yaml`:

```yaml
chunking:
  type: tokens
  size: 1200          # target chunk size in tokens
  overlap: 100        # overlap between adjacent chunks
  encoding_model: o200k_base   # tokenizer used
```

Each document is split into consecutive ~1200-token windows with 100-token overlap. Overlap ensures that entities/relationships spanning chunk boundaries aren't lost.

**Input**: `output/documents.parquet`

**Output**: `output/text_units.parquet` (base version)

- `id` — unique text unit ID
- `text` — the chunk content
- `document_ids` — which document it came from
- `n_tokens` — token count

For 100 patient docs of ~500 tokens each, expect **~100 text units** (one per patient since patients fit in <1200 tokens).

| Aspect | Value |
|---|---|
| LLM calls | Zero |
| Cost impact | Free |
| Speed | A few seconds |

---

### 3. `create_final_documents`

**What it does**: Updates document records with information about which text units they contain. Essentially links documents to text units in both directions.

**Input**: `documents.parquet` + `text_units.parquet` (base)

**Output**: `output/documents.parquet` (finalized) with added column:

- `text_unit_ids` — list of text unit IDs derived from this document

| Aspect | Value |
|---|---|
| LLM calls | Zero |
| Cost impact | Free |
| Speed | Milliseconds |

**Why it exists**: This bookkeeping step enables citation — later when GraphRAG answers a query, it can trace which text unit and which document contributed to the answer.

---

### 4. `extract_graph` — The Big One

**What it does**: For every text unit, sends it to the LLM with an entity extraction prompt. The LLM returns structured lists of **entities** and **relationships** found in that chunk.

**How it works**: For each text unit, GraphRAG sends a prompt like:

```text
System: You are an intelligent assistant. Extract entities of types:
patient, condition, medication, observation.
For each entity, provide type, name, and description.
Also extract relationships between these entities.

User: [text of patient_0042]
```

The LLM returns something like:

```text
("entity"|"PATIENT"|"John Smith"|"73-year-old male patient")
("entity"|"CONDITION"|"Hypertension"|"Elevated blood pressure diagnosis")
("entity"|"MEDICATION"|"Lisinopril"|"ACE inhibitor for blood pressure")
("relationship"|"John Smith"|"Hypertension"|"John Smith is diagnosed with Hypertension"|8)
("relationship"|"John Smith"|"Lisinopril"|"John Smith is prescribed Lisinopril"|8)
("relationship"|"Hypertension"|"Lisinopril"|"Lisinopril is used to treat Hypertension"|9)
```

GraphRAG then parses this into structured entity + relationship records.

**Gleaning**: If `max_gleanings: 1`, GraphRAG makes a second LLM call asking "Did you miss any entities?" — doubling the cost. Setting `max_gleanings: 0` skips this step.

**Input**: `text_units.parquet`

**Output**:

- `output/entities.parquet` — initial entities discovered
- `output/relationships.parquet` — initial relationships discovered
- `output/text_units.parquet` — updated with entity IDs found in each chunk

| Aspect | Value |
|---|---|
| LLM calls | 1 per text unit (with `max_gleanings=0`) |
| Cost impact | 60-70% of total cost |
| Speed | 5-15 minutes for 100 patient docs |

**Why so expensive**:

- Each call has a large system prompt (~2000 tokens)
- Each call generates lots of structured output (~500-1500 tokens)
- Output tokens cost 4-5x input tokens
- Gleanings (if enabled) double the call count

**Common failures**:

- Malformed LLM output (rare with modern models)
- Rate limiting (429 errors)
- Deployment quota exhausted

---

### 5. `finalize_graph`

**What it does**: Cleans up the raw extraction results:

1. **Deduplicates entities** — if "Hypertension" was extracted from 30 chunks, merge into one entity record with combined descriptions
2. **Merges relationships** — combines duplicate relationship pairs
3. **Computes graph metrics** — like degree centrality
4. **Assigns final IDs** and canonicalizes names

**Input**: Raw `entities.parquet` + `relationships.parquet`

**Output**: Cleaned versions with additional columns:

- `degree` — how many edges each entity has
- `frequency` — how many text units it appeared in
- Merged descriptions
- Canonical names

| Aspect | Value |
|---|---|
| LLM calls | Zero (pure data processing) |
| Cost impact | Free |
| Speed | Seconds |

**Why it matters**: Without this step, you'd have "Diabetes", "diabetes", "Type 2 Diabetes", and "T2DM" as four separate entities. This merges them into one.

> **Note**: The description merging later triggers `summarize_descriptions`, which IS an LLM step — technically a separate workflow but often runs alongside finalize.

---

### 6. `extract_covariates` — Disabled in Your Config

**What it does**: Extracts factual **claims** or **assertions** from text — things like "Metformin reduces A1C by 1-2%" or "Hypertension affects 30% of adults over 60".

Claims are supplementary metadata attached to entities and relationships, useful for advanced queries like "What claims are made about Metformin?"

**Input**: `text_units.parquet` + `entities.parquet`

**Output**: `output/covariates.parquet`

| Aspect | Value |
|---|---|
| LLM calls | 1 per text unit (with claim-extraction prompt) |
| Cost impact | Would add ~15-20% to total cost |
| Speed | 5-10 min for 100 patient docs |
| Status | Skipped (`extract_claims.enabled: false`) |

**When to enable**: For research applications, medical evidence mining, or when precise factual attribution matters. Not needed for demos.

---

### 7. `create_communities`

**What it does**: Runs the **Leiden clustering algorithm** on the knowledge graph to detect **communities** — groups of densely-interconnected entities.

For a healthcare graph, communities represent things like:

- **Diabetes management**: Diabetes + Metformin + A1C observation + Endocrinologist encounter
- **Cardiovascular disease**: Hypertension + Lisinopril + Blood pressure observation + Cardiology visit
- **Pediatric wellness**: Child patients + Immunizations + Growth observations

**How Leiden works**: Iteratively partitions the graph to maximize **modularity** (density inside communities vs sparsity between them). Produces a **hierarchical structure** — communities at multiple levels (small tight clusters up to large domain-level groups).

**Config that controls this**:

```yaml
cluster_graph:
  max_cluster_size: 15
```

**Input**: `entities.parquet` + `relationships.parquet`

**Output**: `output/communities.parquet` with columns:

- `community_id`
- `level` — hierarchy level (0 = broad, 1+ = more specific)
- `entity_ids` — which entities belong
- `relationship_ids` — which edges are inside
- `size`

For a 100-patient graph, expect **20-40 communities** across 2-3 hierarchy levels.

| Aspect | Value |
|---|---|
| LLM calls | Zero |
| Cost impact | Free |
| Speed | Seconds |

**Why it's magical**: This is what makes GraphRAG different from vector RAG. Communities give you **thematic understanding** of your data — you can ask "what are the major themes?" and get real answers.

---

### 8. `create_final_text_units`

**What it does**: Enriches text units with references to the entities, relationships, and communities they contributed to.

Adds columns like:

- `entity_ids` — entities extracted from this chunk
- `relationship_ids` — relationships extracted from this chunk
- `covariate_ids` — claims (if extracted)

**Input**: `text_units.parquet` (base) + all downstream outputs

**Output**: `output/text_units.parquet` (finalized)

| Aspect | Value |
|---|---|
| LLM calls | Zero |
| Cost impact | Free |
| Speed | Milliseconds |

**Why it matters**: This closes the citation loop. When a query result mentions an entity, GraphRAG can trace it back to the exact text unit and document that produced it — essential for verifiability.

---

### 9. `create_community_reports` — Second Big Cost

**What it does**: For each community, sends the LLM the entities + relationships + representative text and asks it to write a **natural language summary report** describing the community.

**Prompt structure**:

```text
System: You are a healthcare analyst. Below is a community of related
clinical entities. Write a summary report describing:
1. The theme of this community
2. Key entities and their roles
3. Notable relationships
4. Clinical significance

Community data:
- Entities: [Diabetes, Metformin, A1C observation, ...]
- Relationships: [...]
- Sample text: [...]
```

The LLM produces a structured report with:

- `title` (e.g., "Diabetes Management Cluster")
- `summary` (paragraph description)
- `rating` (impact rating 0-10)
- `findings` (key observations)
- `full_content` (formatted markdown)

**Input**: `communities.parquet` + `entities.parquet` + `relationships.parquet` + `text_units.parquet`

**Output**: `output/community_reports.parquet`

**Config controls**:

```yaml
community_reports:
  max_length: 800           # cap report length
  max_input_length: 6000    # cap input context
```

| Aspect | Value |
|---|---|
| LLM calls | 1 per community per hierarchy level (~60 calls for 30 communities x 2 levels) |
| Cost impact | 15-25% of total cost |
| Speed | 3-8 minutes |

**Why it matters**: Community reports are the "wow moment" of GraphRAG. When you do a `global` search query, GraphRAG maps your question against community reports first, then reduces the results. **Global search literally cannot work without community reports.**

---

### 10. `generate_text_embeddings`

**What it does**: Sends each entity description, relationship description, community summary, and text unit to the **embedding model** and gets back a numerical vector (1536 dimensions for `text-embedding-3-small`).

These vectors get stored in **LanceDB** (local vector store) so that at query time, GraphRAG can do fast semantic similarity search.

**What gets embedded**:

- Every entity description
- Every relationship description
- Every community summary
- Every text unit (for basic search)

For 100 patients you might have:

- ~500 entities
- ~1,500 relationships
- ~30 communities
- ~100 text units
- **Total: ~2,100 embedding calls, ~200K tokens**

**Input**: All parquet files from previous steps

**Output**: `output/lancedb/` folder (vector database)

| Aspect | Value |
|---|---|
| LLM calls | ~2,000 embedding calls (not chat calls) |
| Cost impact | ~$0.02-0.05 total (embeddings are cheap) |
| Speed | 1-3 minutes |

**Why it matters**: Query time uses these vectors for semantic search. Without them, `local` and `drift` search wouldn't work.

---

## Cost & Time Breakdown for a 100-Patient Run

| # | Workflow | LLM Type | Approx Cost | Approx Time |
|---|---|---|---|---|
| 1 | load_input_documents | None | Free | 5 sec |
| 2 | create_base_text_units | None | Free | 3 sec |
| 3 | create_final_documents | None | Free | 1 sec |
| **4** | **extract_graph** | **Chat** | **$0.10-0.15** | **4-8 min** |
| 5 | finalize_graph | None | Free | 5 sec |
| 6 | extract_covariates | Skipped | $0 | 0 sec |
| 7 | create_communities | None | Free | 15 sec |
| 8 | create_final_text_units | None | Free | 3 sec |
| **9** | **create_community_reports** | **Chat** | **$0.05-0.08** | **1-2 min** |
| 10 | generate_text_embeddings | Embedding | $0.02 | 30 sec |
| | **Total** | | **$0.17-0.25** | **7-10 min** |

---

## What Gets Written to Disk

After completion, `graphrag_workspace/output/` will contain:

```text
output/
  documents.parquet          <-- 100 documents
  text_units.parquet         <-- ~100 chunks
  entities.parquet           <-- ~500 clinical entities
  relationships.parquet      <-- ~1,500 relationships
  communities.parquet        <-- ~30 community records
  community_reports.parquet  <-- ~30 natural language summaries
  graph.graphml              <-- full graph for external tools
  lancedb/                   <-- vector store for search
    entity_descriptions/
    relationship_descriptions/
    community_reports/
    text_units/
  logs/                      <-- indexing logs
```

---

## How Workflows Feed Each Search Method

Understanding this helps you pick the right search method for each question.

### `local` search

**Uses**: `entities` + `relationships` + `text_units` + `text_unit_embeddings` + `entity_embeddings`

**Best for**: Specific facts about specific entities
**Example**: "Which medications does patient John Smith take?"

### `global` search

**Uses**: `community_reports` (map-reduce over them)

**Best for**: Population-level themes
**Example**: "What are the major clinical themes in this dataset?"

### `drift` search

**Uses**: `communities` + `entities` + `relationships` + `embeddings`

**Best for**: Multi-hop reasoning that combines global themes with local details
**Example**: "How are hypertension, medications, and observations connected across the population?"

### `basic` search

**Uses**: `text_units` + `text_unit_embeddings`

**Best for**: Traditional RAG-style keyword/semantic search
**Example**: "Find all mentions of Metformin dosing."

---

## End-to-End Example

Imagine text unit 42 contains this sentence:

> "John Smith, a 73-year-old male, has been diagnosed with Type 2 Diabetes and is prescribed Metformin. His last A1C was 7.2%."

The pipeline processes it like this:

1. **`load_input_documents`** - records the file exists
2. **`create_base_text_units`** - puts this sentence in text unit 42
3. **`create_final_documents`** - notes doc contains text unit 42
4. **`extract_graph`** - LLM identifies:
   - **Entities**: `John Smith`, `Type 2 Diabetes`, `Metformin`, `A1C`
   - **Relationships**: `John Smith -> has -> Type 2 Diabetes`, etc.
5. **`finalize_graph`** - merges `Type 2 Diabetes` with any other "diabetes" mentions from other patients
6. **`create_communities`** - groups Diabetes + Metformin + A1C into one community
7. **`create_final_text_units`** - links text unit 42 to those entities
8. **`create_community_reports`** - LLM writes a report titled "Type 2 Diabetes Management" summarizing the diabetes community
9. **`generate_text_embeddings`** - vectorizes descriptions for retrieval

Now at query time, if you ask "What is Metformin used for?":

- **Local search** finds the `Metformin` entity, follows its relationships, and pulls in text unit 42 for citation
- **Global search** finds the "Type 2 Diabetes Management" community report and synthesizes an answer

---

## Key Takeaways

1. **Only 3 workflows cost money**: `extract_graph`, `create_community_reports`, `generate_text_embeddings`
2. **`extract_graph` dominates** at 60-70% of cost
3. **Skipping `extract_covariates`** saves ~20% cost with minimal quality loss
4. **`create_communities`** is free but is what makes GraphRAG different from vector RAG
5. **Cache reuse works per workflow** - if you re-run with the same input + same prompts + same model, cached LLM responses are free
6. **Embeddings are dirt cheap** - never optimize by skipping embeddings
7. **Community reports enable global search** - without them, only local/basic search work

---

## References

- Microsoft GraphRAG documentation: https://microsoft.github.io/graphrag/
- GraphRAG GitHub repository: https://github.com/microsoft/graphrag
- Microsoft Research blog post: https://www.microsoft.com/en-us/research/blog/graphrag-unlocking-llm-discovery-on-narrative-private-data/

---

**Prepared for**: Synthea FHIR + Microsoft GraphRAG healthcare demo
**Environment**: Azure AI Foundry (East US 2)
**Model used**: `gpt-5-mini` for chat, `text-embedding-3-small` for embeddings
**Last updated**: July 13, 2026
