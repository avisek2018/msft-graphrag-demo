"""Load Synthea FHIR R4 bundles from disk."""

from pathlib import Path
from typing import Any, Dict, Iterable, List
import json


def load_bundle(path: Path) -> Dict[str, Any]:
    """Load a single FHIR JSON bundle from disk."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_resources(bundle: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return the list of FHIR resources contained in a Bundle."""
    if not isinstance(bundle, dict):
        return []

    if bundle.get("resourceType") != "Bundle":
        # Some Synthea exports include single-resource files
        return [bundle] if bundle.get("resourceType") else []

    resources: List[Dict[str, Any]] = []
    for entry in bundle.get("entry", []) or []:
        resource = (entry or {}).get("resource")
        if isinstance(resource, dict):
            resources.append(resource)

    return resources


def iter_bundle_files(raw_dir: Path) -> Iterable[Path]:
    """Yield every FHIR bundle JSON file in a directory (recursively)."""
    if not raw_dir.exists():
        raise FileNotFoundError(f"Raw FHIR directory not found: {raw_dir}")

    for path in sorted(raw_dir.rglob("*.json")):
        # Skip Synthea metadata files
        name = path.name.lower()
        if name.startswith("hospitalinformation") or name.startswith("practitionerinformation"):
            continue
        yield path