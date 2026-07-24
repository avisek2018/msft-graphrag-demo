"""Run the GraphRAG indexing pipeline on the prepared documents."""

from pathlib import Path
import subprocess
import sys
import warnings

warnings.filterwarnings("ignore", message=".*botocore.*")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = PROJECT_ROOT / "graphrag_workspace"
INPUT_DIR = WORKSPACE / "input"


def main() -> None:
    if not INPUT_DIR.exists() or not list(INPUT_DIR.glob("*.txt")):
        print(f"No .txt files found in {INPUT_DIR}")
        print("Run scripts/01_prepare_documents.py first.")
        sys.exit(1)

    print(f"Running GraphRAG index against workspace: {WORKSPACE}")

    try:
        # subprocess.run(
        #     ["graphrag", "index", "--root", str(WORKSPACE)],
        #     check=True,
        # )
        subprocess.run(
                ["graphrag", "index", "--root", str(WORKSPACE), "--skip-validation"],
                    check=True,
                )
    except subprocess.CalledProcessError as exc:
        print(f"graphrag index failed with exit code {exc.returncode}")
        sys.exit(exc.returncode)

    print("GraphRAG indexing complete.")
    print(f"Output artifacts are under: {WORKSPACE / 'output'}")


if __name__ == "__main__":
    main()