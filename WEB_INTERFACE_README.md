# GraphRAG Web Interface

A simple web interface for querying the GraphRAG medical knowledge graph from a browser.

## Setup

### 1. Install Flask (if not already installed)

```powershell
.\msftgrag\Scripts\Activate.ps1
pip install flask
```

### 2. Set API Key in Environment

The server will automatically load the API key from `graphrag_workspace/.env`. Make sure it exists with:

```
GRAPHRAG_API_KEY=your_key_here
```

### 3. Start the Web Server

```powershell
# Activate virtual environment
.\msftgrag\Scripts\Activate.ps1

# Start the server
python web_server.py
```

### 4. Open in Browser

Navigate to: **http://localhost:5000**

## Features

- **Simple Query Interface**: Enter natural language questions about patient medical records
- **Multiple Search Methods**:
  - **Local**: Detailed, focused results on specific entities
  - **Global**: Comprehensive overview using all communities
  - **Drift**: Advanced semantic search with dynamic community selection
  - **Basic**: Fast keyword-based search
  
- **Example Queries**: Quick-start buttons for common questions
- **Real-time Results**: Immediate display of formatted responses

## Usage

1. Enter your question in the text area (e.g., "What conditions does this patient have?")
2. Select a search method from the dropdown
3. Click "Send Query" or press Ctrl+Enter
4. View results in formatted markdown below

## Example Queries

```
"What conditions does this patient have?"
"What medications is the patient taking and what conditions do they treat?"
"What procedures has the patient undergone?"
"What are the patient's lab values and observations?"
"What is the patient's medical history?"
"What cardiac-related conditions does the patient have?"
```

## API Endpoint

You can also call the API directly:

```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What conditions does this patient have?",
    "method": "local"
  }'
```

Response format:
```json
{
  "success": true,
  "response": "...",
  "method": "local",
  "query": "What conditions does this patient have?"
}
```

## Troubleshooting

**Port Already in Use**:
```powershell
# Change port in web_server.py:
# app.run(debug=True, host="0.0.0.0", port=5001)
```

**API Key Not Found**:
Make sure `graphrag_workspace/.env` contains `GRAPHRAG_API_KEY=...`

**Query Timeout**:
Queries timeout after 2 minutes. Increase in `web_server.py` if needed:
```python
timeout=120,  # Change this value (in seconds)
```

**Flask Not Installed**:
```powershell
pip install flask python-dotenv
```

## Files

- `web_server.py` - Flask backend server
- `templates/index.html` - Web interface (HTML/CSS/JS)
- `graphrag_workspace/.env` - API key configuration
