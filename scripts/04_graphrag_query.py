"""Query the Synthea FHIR GraphRAG index using local, global, or drift search."""

from pathlib import Path
import argparse
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = PROJECT_ROOT / "graphrag_workspace"


def main() -> None:
    parser = argparse.ArgumentParser(description="Query the Synthea FHIR GraphRAG index.")
    parser.add_argument(
        "--method",
        choices=["local", "global", "drift"],
        default="local",
        help="GraphRAG query method.",
    )
    parser.add_argument(
        "--query",
        required=True,
        help="Natural language question.",
    )
    args = parser.parse_args()

    try:
        subprocess.run(
            [
                "graphrag",
                "query",
                "--root",
                str(WORKSPACE),
                "--method",
                args.method,
                args.query,
            ],
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        print(f"graphrag query failed with exit code {exc.returncode}")
        sys.exit(exc.returncode)


if __name__ == "__main__":
    main()
