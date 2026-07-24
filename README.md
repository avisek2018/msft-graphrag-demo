# 🏥 Synthea FHIR R4 to Microsoft GraphRAG Demo

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GraphRAG](https://img.shields.io/badge/GraphRAG-2.0+-green.svg)](https://github.com/microsoft/graphrag)

## 📋 Overview

Transform **Synthea synthetic healthcare data** (FHIR R4 format) into a **Microsoft GraphRAG-powered knowledge graph** for intelligent, contextual medical reasoning and analysis.

This repository provides a **production-ready pipeline** to:
- ✅ Extract FHIR R4 patient records from Synthea bundles
- ✅ Convert clinical data into narrative documents
- ✅ Build knowledge graphs with entity and relationship extraction
- ✅ Generate semantic embeddings and community summaries
- ✅ Query the knowledge graph using multiple search strategies
- ✅ Interact via an intuitive web interface

**Perfect for**: Healthcare copilots, clinical insight systems, FHIR-based AI accelerators, medical research, and knowledge graph demonstrations.

---

## 🎯 Key Features

| Feature | Description |
|---------|-------------|
| **FHIR R4 Ingestion** | Loads Synthea patient bundles with automatic resource filtering |
| **Smart Narrative Generation** | Converts structured FHIR data into GraphRAG-friendly text documents (capped at 8 KB per patient) |
| **Knowledge Graph Extraction** | Automatically extracts entities, relationships, and community clusters from medical records |
| **Multi-Method Search** | Query using Local, Global, Drift, or Basic search strategies |
| **Web UI** | Browser-based interface for intuitive exploration |
| **Fully Configurable** | Customize LLM models, embedding dimensions, batch sizes, and prompts |
| **Production-Ready** | Includes error handling, logging, batch processing, and optimization |

---

## 🏗️ Architecture

```
Synthea FHIR R4 Bundles (JSON)
          ↓
    FHIR Loader
    ├─ Parses bundle files
    ├─ Extracts FHIR resources
    └─ Filters low-value resources
          ↓
    Narrative Builder
    ├─ Converts to patient narratives
    ├─ Caps output at 8 KB/patient
    └─ Generates .txt documents
          ↓
    GraphRAG Input Documents
          ↓
    GraphRAG Indexing Pipeline
    ├─ Entity & relationship extraction (LLM-based)
    ├─ Community detection & clustering
    ├─ Report generation
    ├─ Vector embedding (dense retrieval)
    └─ Multi-index storage
          ↓
    Query Engine (Local/Global/Drift)
    ├─ Semantic search
    ├─ Context retrieval
    └─ LLM-powered responses
          ↓
    Web Interface & API
```

---

## 📁 Project Structure

```
synthea-graphrag-demo/
├── README.md                           # This file
├── requirements.txt                    # Python dependencies
├── SOLUTION_SUMMARY.md                 # Known issues and fixes
├── DEBUGGING_GUIDE.md                  # Troubleshooting reference
├── WEB_INTERFACE_README.md             # Web server documentation
├── web_server.py                       # Flask web interface
│
├── data/
│   └── raw/                           # Place Synthea *.json bundles here
│       ├── Afton574_Casper496_*.json
│       ├── Alena861_Alina705_*.json
│       └── ...
│
├── graphrag_workspace/
│   ├── settings.yaml                  # GraphRAG configuration (auto-created)
│   ├── .env                           # API keys & environment variables (auto-created)
│   ├── input/                         # Narrative documents (auto-created by script)
│   ├── output/                        # GraphRAG outputs (auto-created)
│   ├── cache/                         # LLM cache & extraction data
│   ├── logs/                          # Detailed pipeline logs
│   └── prompts/                       # LLM system prompts
│       ├── extract_graph.txt          # Default entity/relationship extraction
│       ├── extract_graph_medical.txt  # Medical-specific variant
│       ├── local_search_system_prompt.txt
│       ├── global_search_*.txt
│       └── ... (13 prompts total)
│
├── src/
│   ├── __init__.py
│   ├── fhir_loader.py                 # FHIR bundle loader
│   ├── fhir_utils.py                  # FHIR parsing utilities
│   └── narrative_builder.py           # Converts FHIR → narratives
│
├── scripts/
│   ├── __init__.py
│   ├── 01_prepare_documents.py        # Step 1: Load & convert FHIR bundles
│   ├── 02_graphrag_init.py            # Step 2: Initialize GraphRAG workspace
│   ├── 03_graphrag_index.py           # Step 3: Build knowledge graph
│   └── 04_graphrag_query.py           # Step 4: Query the graph
│
├── static/                            # CSS & JavaScript for web UI
├── templates/                         # HTML templates
│   └── index.html                     # Web interface
│
└── msftgrag/                          # Virtual environment (created locally)
```

---

## 📋 Prerequisites

- **Python**: 3.10, 3.11, or 3.12 (GraphRAG requirement)
- **API Access**: OpenAI or Azure OpenAI with:
  - Chat model (`gpt-4`, `gpt-4-turbo`, `gpt-4o`, etc.)
  - Embedding model (`text-embedding-3-small`, `text-embedding-3-large`)
- **Data**: Synthea 1,000 Patient FHIR R4 dataset ([download here](https://synthea.mitre.org/downloads))
- **Disk Space**: ~2-3 GB for full indexing (varies by patient count)

---

## ⚡ Quick Start

### 1. Clone & Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/synthea-graphrag-demo.git
cd synthea-graphrag-demo

# Create virtual environment
python -m venv msftgrag
source msftgrag/bin/activate  # macOS/Linux
# or
msftgrag\Scripts\activate  # Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
pip install graphrag  # Required for pipeline execution
```

### 3. Prepare Data

```bash
# Download Synthea 1,000 Patient dataset
# Extract to: data/raw/

# Verify structure
ls data/raw/  # Should show *.json files
```

### 4. Configure API Key

```bash
# Initialize GraphRAG workspace
python scripts/02_graphrag_init.py

# Edit the .env file
nano graphrag_workspace/.env
# or
code graphrag_workspace/.env

# Add your API key:
# GRAPHRAG_API_KEY=sk-... (OpenAI)
# or for Azure OpenAI, follow Azure setup instructions
```

### 5. Run the Pipeline

```bash
# Step 1: Convert FHIR bundles to narratives
python scripts/01_prepare_documents.py

# Step 2: Build the knowledge graph (⏱️ ~10-30 min depending on GPU/model)
python scripts/03_graphrag_index.py

# Step 3: Query the graph (interactive CLI)
python scripts/04_graphrag_query.py --method local --query "What conditions does this patient have?"
```

### 6. Launch Web Interface

```bash
# Make sure venv is activated
pip install flask

# Start the web server
python web_server.py

# Open browser: http://localhost:5000
```

---

## 🛠️ Detailed Setup Instructions

### macOS / Linux

```bash
mkdir synthea-graphrag-demo
cd synthea-graphrag-demo

# Clone or download source files into the project folder
# Create virtual environment
python3.11 -m venv msftgrag
source msftgrag/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install graphrag

# Download Synthea data to data/raw/
# Configure API key
python scripts/02_graphrag_init.py
# Edit graphrag_workspace/.env

# Run pipeline
python scripts/01_prepare_documents.py
python scripts/03_graphrag_index.py
```

### Windows (PowerShell)

```powershell
# Create project
mkdir synthea-graphrag-demo
cd synthea-graphrag-demo

# Create virtual environment
python -m venv msftgrag
.\msftgrag\Scripts\Activate.ps1

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install graphrag

# Download Synthea data to data\raw\
# Configure API key
python scripts/02_graphrag_init.py
# Edit graphrag_workspace\.env

# Run pipeline
python scripts/01_prepare_documents.py
python scripts/03_graphrag_index.py

# Launch web server
python web_server.py
# Navigate to http://localhost:5000
```

### Docker (Optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt && pip install graphrag flask

COPY . .

ENV GRAPHRAG_API_KEY=""
EXPOSE 5000

CMD ["python", "web_server.py"]
```

---

## 📚 Usage Guide

### Script-by-Script Breakdown

#### 1️⃣ `scripts/01_prepare_documents.py`
**Purpose**: Convert Synthea FHIR bundles into narrative documents

```bash
python scripts/01_prepare_documents.py
```

**What it does**:
- Scans `data/raw/` for FHIR JSON bundles
- Extracts FHIR resources (Patient, Condition, Medication, Procedure, Observation, etc.)
- Filters out low-value resources (DiagnosticReport, DocumentReference, Claim, insurance data)
- Generates narrative text (8 KB max per patient)
- Saves to `graphrag_workspace/input/`

**Output**:
```
graphrag_workspace/input/
├── Afton574_Casper496.txt
├── Alena861_Alina705.txt
├── Alexis664_Langworth352.txt
└── ... (one per patient)
```

---

#### 2️⃣ `scripts/02_graphrag_init.py`
**Purpose**: Initialize GraphRAG workspace with configuration files

```bash
python scripts/02_graphrag_init.py
```

**What it does**:
- Creates `graphrag_workspace/` directory
- Generates `settings.yaml` with LLM/embedding model config
- Generates `.env` template for API keys
- Sets up subdirectories (cache, logs, output, prompts)

**Next steps**:
1. Edit `graphrag_workspace/.env` and add `GRAPHRAG_API_KEY`
2. Review and adjust `graphrag_workspace/settings.yaml` if needed

---

#### 3️⃣ `scripts/03_graphrag_index.py`
**Purpose**: Build the complete knowledge graph

```bash
python scripts/03_graphrag_index.py
```

**What it does** (GraphRAG indexing pipeline):
1. **Extraction**: LLM extracts entities and relationships from narratives
2. **Graph Construction**: Builds knowledge graph from extracted entities
3. **Community Detection**: Clusters entities into semantic communities
4. **Embedding**: Generates vector embeddings for dense retrieval
5. **Summarization**: Creates summaries for each community
6. **Storage**: Saves all artifacts to `graphrag_workspace/output/`

**Outputs** (in `graphrag_workspace/output/`):
- `artifacts/`: ParquetDB stores (entities, relationships, communities)
- `embeddings/`: Vector embeddings
- `reports/`: Community summaries
- `graphml/`: GraphML file for visualization

**⏱️ Performance**: ~10-30 min (depends on GPU, model, patient count)

---

#### 4️⃣ `scripts/04_graphrag_query.py`
**Purpose**: Query the knowledge graph

```bash
# Local search (detailed, focused)
python scripts/04_graphrag_query.py --method local --query "What conditions does the patient have?"

# Global search (overview from all communities)
python scripts/04_graphrag_query.py --method global --query "What is the patient's medical history?"

# Drift search (advanced semantic search)
python scripts/04_graphrag_query.py --method drift --query "What cardiac procedures has the patient had?"
```

**Search Methods**:
| Method | Use Case | Response Speed | Coverage |
|--------|----------|----------------|----------|
| **local** | Specific entity/relationship lookups | Fast | Focused |
| **global** | Comprehensive overview | Slow | Full graph |
| **drift** | Semantic similarity + context | Medium | Context-aware |

---

### Web Interface

Launch the interactive web UI:

```bash
pip install flask
python web_server.py
```

**Features**:
- 🎯 Natural language query input
- 🔍 Multiple search method selection
- ⚡ Real-time markdown-formatted responses
- 📋 Query history (browser local storage)
- 💾 Copy/export results

**Example Queries**:
```
"What conditions does this patient have?"
"What medications is the patient taking and why?"
"What procedures has the patient undergone?"
"What are the patient's lab values?"
"What is the patient's medical history?"
"What immunizations has the patient received?"
"Compare the patient's observations over time"
```

---

## ⚙️ Configuration

### API Keys

Edit `graphrag_workspace/.env`:

**OpenAI**:
```env
GRAPHRAG_API_KEY=sk-...
OPENAI_API_KEY=sk-...
```

**Azure OpenAI**:
```env
GRAPHRAG_API_KEY=your-key
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_ENDPOINT=https://<instance>.openai.azure.com/
OPENAI_API_VERSION=2024-02-15-preview
```

### GraphRAG Settings

Edit `graphrag_workspace/settings.yaml` to customize:

```yaml
# LLM Configuration
llm:
  type: openai
  model: gpt-4o  # or gpt-4-turbo, gpt-4, etc.

# Embedding Configuration
embedding:
  type: openai
  model: text-embedding-3-small  # 1536 dimensions

# Entity/Relationship Extraction
extract_graph:
  prompt: "prompts/extract_graph.txt"  # or extract_graph_medical.txt

# Batch Processing
embed_text:
  batch_size: 4  # Reduce if memory issues
  batch_max_tokens: 4096

# Vector Store
vector_store:
  type: lancedb
  vector_size: 1536  # Must match embedding model dimensions
```

---

## 🔍 Example Queries & Expected Outputs

### Local Search
```bash
python scripts/04_graphrag_query.py --method local \
  --query "What conditions does the patient have?"
```

**Expected Output** (Markdown):
```
Based on the patient's medical records:

The patient has been diagnosed with:
- Hypertension (2010-01-15)
- Type 2 Diabetes Mellitus (2015-06-22)
- Hyperlipidemia (2016-03-10)
- Chronic Obstructive Pulmonary Disease (2019-08-05)

Each condition is documented with clinical status and onset date.
```

### Global Search
```bash
python scripts/04_graphrag_query.py --method global \
  --query "Summarize this patient's complete medical profile"
```

**Expected Output**:
- Comprehensive overview from all community clusters
- Aggregated entities and relationships
- Cross-community connections

---

## 🐛 Troubleshooting

### Common Issues & Solutions

| Problem | Cause | Solution |
|---------|-------|----------|
| `GRAPHRAG_API_KEY not found` | `.env` file missing or not loaded | Run `02_graphrag_init.py`, then edit `.env` |
| `ModuleNotFoundError: graphrag` | GraphRAG not installed | `pip install graphrag` |
| `No input documents found` | `01_prepare_documents.py` didn't run | Run step 1 first, verify `graphrag_workspace/input/` has .txt files |
| `Vector dimension mismatch` | Model mismatch in settings | Ensure `vector_size: 1536` for text-embedding-3-small |
| `CUDA out of memory` | GPU memory exhausted | Reduce `batch_size` in settings.yaml (8→4 or 4→2) |
| `Query timeout` | Global search too large | Try `local` or `drift` method instead |

### Checking Logs

```bash
# Indexing logs
tail -f graphrag_workspace/logs/indexing-engine.log

# Query logs
tail -f graphrag_workspace/logs/query.log

# Check cache
ls -la graphrag_workspace/cache/
```

### Detailed Debugging

See [DEBUGGING_GUIDE.md](DEBUGGING_GUIDE.md) for:
- LLM output inspection
- Batch processing diagnostics
- Community detection validation
- Embedding quality checks

---

## 📊 Project Features in Detail

### FHIR Resource Processing

**Supported Resources** (extracted from bundles):
- `Patient` → Demographics
- `Condition` → Medical conditions
- `MedicationRequest` → Prescriptions
- `Procedure` → Surgical/clinical procedures
- `Observation` → Lab values & measurements
- `Immunization` → Vaccines
- `CarePlan` → Treatment plans
- `Encounter` → Clinical encounters

**Filtered Resources** (low clinical value):
- DiagnosticReport (large)
- DocumentReference (base64 attachments)
- Claim (billing data)
- ExplanationOfBenefit
- Coverage
- SupplyDelivery

### Narrative Generation

Each patient narrative is formatted as:
```markdown
# Patient Record: [Name]

[Name] is a synthetic patient generated by Synthea in FHIR R4 format.

## Clinical Conditions
- [Condition 1] (onset: [date], status: [status])
- [Condition 2] (onset: [date], status: [status])

## Medications
- [Med 1] ([status], authored: [date])
- [Med 2] ([status], authored: [date])

## Procedures
- [Procedure 1] (status: [status], date: [date])
- [Procedure 2] (status: [status], date: [date])

## Observations
- [Lab 1]: [value] [unit] (date: [date])
- [Lab 2]: [value] [unit] (date: [date])

...
```

**Size optimization** (✨ **Important for cost management**):
- **Hard cap: 8 KB per patient** — Keeps LLM token consumption manageable
  - Full FHIR bundles for 1,000 patients can exceed 10 GB
  - Unfiltered narratives = 50-100+ KB per patient = massive token costs
  - 8 KB limit keeps costs ~80-90% lower while retaining all clinically relevant data
- **Resource limits**: max 20 items per section (conditions, meds, procedures, etc.)
- **Smart filtering**: Focus on clinically relevant data, skip bulk data (base64, billing)
- **Result**: ~100 documents × 8 KB ≈ 800 KB total vs. 1-10 GB unfiltered

---

## 🎓 Key Learnings & Best Practices

### From Production Deployment

1. **Prompt Format Matters**
   - Entity names in relationships MUST match exactly with extracted entity names
   - Use GraphRAG's default `extract_graph.txt` as baseline before customizing
   - Medical-specific prompts need careful validation

2. **Vector Dimensions**
   - `text-embedding-3-small` → 1536 dimensions
   - `text-embedding-3-large` → 3072 dimensions
   - Must match `settings.yaml` `vector_size` parameter

3. **Batch Size Sensitivity**
   - Start with batch_size: 4 for stability
   - Increase if memory allows, decrease if you hit errors
   - batch_max_tokens: 4096 works well for medical text

4. **💰 LLM Token Cost Optimization** ⭐ **CRITICAL**
   - **Problem**: Full FHIR bundles for large patient cohorts = massive token consumption
     - 1,000 unfiltered FHIR patients ≈ 10+ GB of raw data
     - Unfiltered narratives = 50-100+ KB per patient
     - Processing all documents through LLM extraction = $$$$$
   - **Solution**: Trim inputs to 8 KB max per patient
     - 8 KB cap reduces token costs by ~80-90% 💰
     - Smart filtering removes bulk data (base64, billing, insurance)
     - Resource limits (max 20 items per section) eliminate redundancy
     - Clinical signal is PRESERVED, cost is SLASHED
   - **Example Cost Savings**:
     - Unfiltered: 1,000 patients × 75 KB avg × $0.001/1K tokens ≈ $75
     - Trimmed: 1,000 patients × 8 KB avg × $0.001/1K tokens ≈ $8
     - **90% cost reduction** while maintaining clinical accuracy

5. **Data Quality**
   - Clean, structured narratives perform better than raw FHIR
   - 8 KB per document is ideal for knowledge graph extraction
   - Remove noise (billing, insurance, audit logs)

6. **Search Method Selection**
   - **Local**: 30% faster, good for specific lookups
   - **Global**: Comprehensive but slow, best for overview queries
   - **Drift**: Balanced approach, good default

---

## 📦 Dependencies

See `requirements.txt`:

```
graphrag>=2.0.0              # Microsoft GraphRAG framework
pandas>=2.2.0               # Data processing
networkx>=3.2               # Graph algorithms
python-dotenv>=1.0.0        # Environment variable loading
tqdm>=4.66.0                # Progress bars
pyyaml>=6.0.1               # YAML configuration
```

Plus:
- `flask` (for web interface)
- OpenAI or Azure OpenAI SDK (installed by graphrag)

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Areas for Contribution

- [ ] Support for additional healthcare data formats (HL7 v2, CDA)
- [ ] Custom medical entity types and relationship models
- [ ] Performance optimizations for large datasets
- [ ] Alternative embedding models (Hugging Face, local models)
- [ ] Additional query strategy implementations
- [ ] Enhanced web UI components

---

## 📝 Reference Documentation

- [Microsoft GraphRAG Docs](https://microsoft.github.io/graphrag)
- [FHIR R4 Specification](https://www.hl7.org/fhir/r4/)
- [Synthea Documentation](https://github.com/synthetichealth/synthea/wiki)
- [Knowledge Graph Extraction Patterns](https://github.com/microsoft/graphrag/tree/main/graphrag)

---

## 📖 Additional Resources

- [SOLUTION_SUMMARY.md](SOLUTION_SUMMARY.md) - Known issues & fixes
- [DEBUGGING_GUIDE.md](DEBUGGING_GUIDE.md) - Detailed troubleshooting
- [WEB_INTERFACE_README.md](WEB_INTERFACE_README.md) - Web UI specific docs

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Attribution**: Built on [Microsoft GraphRAG](https://github.com/microsoft/graphrag), [Synthea](https://github.com/synthetichealth/synthea), and [FHIR Standards](https://www.hl7.org/fhir/).

---

## 🙏 Acknowledgments

- **Microsoft GraphRAG** team for the knowledge graph framework
- **Synthea** project for synthetic healthcare data
- **HL7** for FHIR standards
- Contributors and community feedback

---

## 📞 Support

- 📧 Create an issue for bugs or feature requests
- 💬 Discussions for questions and ideas
- 📚 Check existing issues before opening new ones

---

## 🎯 Roadmap

- [ ] Support for Azure Cognitive Services embedding models
- [ ] GraphDB backend option (Neo4j integration)
- [ ] REST API with authentication
- [ ] Batch query processing
- [ ] Real-time streaming updates
- [ ] Mobile app companion
- [ ] Multi-patient cohort analysis

---

**Made with ❤️ for healthcare AI innovation**
python -m venv msftgrag
source msftgrag/bin/activate
```

Windows PowerShell:

```powershell
python -m venv msftgrag
msftgrag\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Place the Synthea dataset

Unzip your Synthea FHIR R4 archive and copy this JSON bundles into:

```text
data/raw/
```

Example contents:

```text
data/raw/Aaron697_Kunde533_5f2e6e8.json
data/raw/Abby321_Auer98_9e081d7.json
data/raw/...
```

Files such as `hospitalInformation1637345232350.json` and `practitionerInformation1637345232350.json` are ignored automatically by the loader.

---

## Step-by-Step Run Guide

### Step 1: Convert FHIR bundles to GraphRAG documents

```bash
python scripts/01_prepare_documents.py
```

Produces one narrative `.txt` file per patient in:

```text
graphrag_workspace/input/
```

Expecped output:

```text
Found 1000 FHIR bundle files in data/raw
Converting: 100%|##########| 1000/1000
Created 1000 GraphRAG documents in graphrag_workspace/input
```

---

### Step 2: Initialize the GraphRAG workspace

```bash
python scripts/02_graphrag_init.py
```

Creates:

```text
graphrag_workspace/.env
graphrag_workspace/settings.yaml
```

---

### Step 3: Configure your API keywand models

Open:

```text
graphrag_workspace/.env
```

Set your API key:

```env
GRAPHRAG_API_KEY=sk-your-openai-key-or-azure-key
```

Open:

```text
graphrag_workspace/settings.yaml
```

**Option A: OpenAI (Simplest)**

Leave the default OpenAI chat and embedding blocks in place. Only the API key in `.env` is required.

**Option B: Azure OpenAI**

Example configuration:

```yaml
completion_models:
  default_completion_model:
    model_provider: azure
    model: gpt-4.1
    azure_deployment_name: gpt-4.1
    api_base: https://<project-name>.services.ai.azure.com
    api_version: 2024-12-01-preview
    auth_method: api_key
    api_key: ${GRAPHRAG_API_KEY}
    retry:
      type: exponential_backoff

embedding_models:
  default_embedding_model:
    model_provider: azure
    model: text-embedding-3-small
    azure_deployment_name: text-embedding-3-small
    api_base: https://<project-name>.services.ai.azure.com
    api_version: 2024-12-01-preview
    auth_method: api_key
    api_key: ${GRAPHRAG_API_KEY}
    retry:
      type: exponential_backoff
```

If you use Azure Managed Identity, replace `auth_method: api_key` with:

```yaml
auth_method: azure_managed_identity
```

Then run `az login` before indexing.

---

### Step 4: Start small (recommended for the first run)

GraphRAG indexing can consume a lot of LLM tokens. Before indexing 1,000 patients, do a smoke test with 10 documents:

```bash
mkdir graphrag_workspace/input_full
mv graphrag_workspace/input/*.txt graphrag_workspace/input_full/
mv graphrag_workspace/input_full/patient_000*.txt graphrag_workspace/input/
```

Once you confirm indexing works, restore the full set:

```bash
mv graphrag_workspace/input_full/*.txt graphrag_workspace/input/
rmdir graphrag_workspace/input_full
```

---

### Step 5: Run the GraphRAG indexing pipeline

```bash
python scripts/03_graphrag_index.py
```

During indexing GraphRAG will:

- Chunk text into TextUnits
- Extract entities and relationships using the LLM
- Detect communities
- Generate community summaries
- Create vector embeddings

Output artifacts go to:

```text
graphrag_workspace/output/
```

Key files include:

```text
entities.parquet
relationships.parquet
communities.parquet
community_reports.parquet
text_units.parquet
```

Indexing time depends on dataset size and model speed. Expect minutes for a small test and hours for the full 1,000 patients.

---

### Step 6: Query the knowledge graph

**Local search (patient-level detail):**

```bash
python scripts/04_graphrag_query.py --method local --query "Which patients have diabetes and are treated with metformin?"
```

**Global search (population-level themes):**

```bash
python scripts/04_graphrag_query.py --method global --query "What are the major clinical themes across this synthetic patient population?"
```

**Drift search (multi-hop reasoning):**

```bash
python scripts/04_graphrag_query.py --method drift --query "How are hypertension, medications, and observations connected across the patient population?"
```

---

## Suggested Demo Questions

- Which conditions commonly appear together in this population?
- What medications are most often prescribed to patients with diabetes?
- Which observations are typically recorded for hypertensive patients?
- Summarize the major clinical communities discovered by GraphRAG.
- What is the relationship between encounters, conditions, and medications?
- Which patients have both cardiovascular conditions and respiratory conditions?

---

## Troubleshooting

**GraphRAG install fails**
Ensure Python is 3.10, 3.11, or 3.12. GraphRAG does not support 3.13+.

**No FHIR bundles found in `data/raw`**
Confirm your Synthea `.json` files are directly in `data/raw/` and not in a nested subfolder.

**Rate limit or 429 errors during indexing**
Reduce the input set, use a smaller or faster model, or increase throttling in `settings.yaml`.

**Indexing is too slow or too expensive**
Start with 10 to 20 documents to validate the pipeline before running the full 1,000.

**`graphrag: command not found`**
Ensure your virtual environment is activated and dependencies are installed.

---

## References

- Microsoft GraphRAG docs: https://microsoft.github.io/graphrag/
- Microsoft GraphRAG GitHub: https://github.com/microsoft/graphrag
- Synthea downloads: https://synthea.mitre.org/downloads
- Synthea GitHub: https://github.com/synthetichealth/synthea

---

## License

This demo project is provided for educational use. Synthea data is released free of cost and privacy restrictions by The MITRE Corporation. Microsoft GraphRAG is licensed under the MIT License.