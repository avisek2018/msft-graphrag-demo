"""Flask web server for GraphRAG medical queries."""

import os
import subprocess
import json
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Load environment
PROJECT_ROOT = Path(__file__).resolve().parent
WORKSPACE = PROJECT_ROOT / "graphrag_workspace"
ENV_FILE = WORKSPACE / ".env"

# Load API key
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)

api_key = os.getenv("GRAPHRAG_API_KEY")
if not api_key:
    print("WARNING: GRAPHRAG_API_KEY not found in environment")

# Set environment variable for subprocess
os.environ["GRAPHRAG_API_KEY"] = api_key

app = Flask(__name__, template_folder="templates", static_folder="static")


@app.route("/")
def index():
    """Serve the main page."""
    return render_template("index.html")


@app.route("/api/query", methods=["POST"])
def query():
    """Execute a GraphRAG query."""
    try:
        data = request.json
        query_text = data.get("query", "").strip()
        method = data.get("method", "local")

        if not query_text:
            return jsonify({"error": "Query cannot be empty"}), 400

        if method not in ["local", "global", "drift", "basic"]:
            return jsonify({"error": f"Invalid method: {method}"}), 400

        # Run GraphRAG query
        result = subprocess.run(
            [
                "graphrag",
                "query",
                "--root",
                str(WORKSPACE),
                "--method",
                method,
                query_text,
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode != 0:
            return jsonify(
                {
                    "error": f"Query failed: {result.stderr}",
                    "stderr": result.stderr,
                }
            ), 500

        return jsonify({
            "success": True,
            "response": result.stdout,
            "method": method,
            "query": query_text,
        })

    except subprocess.TimeoutExpired:
        return jsonify({"error": "Query timed out (took more than 2 minutes)"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "workspace": str(WORKSPACE),
        "has_api_key": bool(api_key),
    })


if __name__ == "__main__":
    print(f"Starting GraphRAG Web Interface")
    print(f"Workspace: {WORKSPACE}")
    print(f"API Key loaded: {bool(api_key)}")
    print(f"Open http://localhost:5000 in your browser")
    app.run(debug=True, host="0.0.0.0", port=5000)
