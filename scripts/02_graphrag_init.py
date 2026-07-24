"""Initialize GraphRAG workspace."""

from pathlib import Path
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = PROJECT_ROOT / "graphrag_workspace"


def main() -> None:
    WORKSPACE.mkdir(parents=True, exist_ok=True)

    print(f"Initializing GraphRAG workspace at: {WORKSPACE}")

    try:
        subprocess.run(
            ["graphrag", "init", "--root", str(WORKSPACE)],
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        print(f"graphrag init failed with exit code {exc.returncode}")
        sys.exit(exc.returncode)

    print("GraphRAG initialization complete.")
    print("Next steps:")
    print(f"  1. Edit {WORKSPACE / '.env'} and set GRAPHRAG_API_KEY.")
    print(f"  2. Review {WORKSPACE / 'settings.yaml'} for model configuration.")


if __name__ == "__main__":
    main()