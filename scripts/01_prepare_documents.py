"""
Convert Synthea FHIR R4 bundles into compact GraphRAG-ready narrative documents.
Self-contained — no dependencies on other project modules.
Guarantees output files stay under 10 KB per patient.
"""

from pathlib import Path
import json
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_DIR = PROJECT_ROOT / "graphrag_workspace" / "input"

# ---- Configuration -------------------------------------------------
MAX_OUTPUT_BYTES = 8000           # Hard cap: 8 KB per patient file
MAX_ITEMS_PER_SECTION = 20        # Cap on conditions/meds/observations/etc.
SKIP_LOW_VALUE_RESOURCES = {
    "DiagnosticReport",           # Contains base64-encoded notes (huge)
    "DocumentReference",          # Contains base64 attachments (huge)
    "Claim",                      # Billing detail (not clinically useful for GraphRAG)
    "ExplanationOfBenefit",       # Insurance detail (huge)
    "Coverage",                   # Insurance metadata
    "Provenance",                 # Audit trails
    "SupplyDelivery",             # Supply chain
    "ImagingStudy",               # Study metadata
}


# ---- FHIR helper functions -----------------------------------------

def display_code(concept):
    """Extract a human-readable label from a FHIR CodeableConcept."""
    if not concept or not isinstance(concept, dict):
        return None
    text = concept.get("text")
    if text:
        return str(text).strip()
    coding = concept.get("coding") or []
    if coding:
        first = coding[0] or {}
        return (first.get("display") or first.get("code") or "").strip() or None
    return None


def observation_value(resource):
    if "valueQuantity" in resource:
        q = resource["valueQuantity"] or {}
        v = q.get("value")
        u = q.get("unit") or q.get("code") or ""
        if v is not None:
            return f"{v} {u}".strip()
    if "valueCodeableConcept" in resource:
        label = display_code(resource["valueCodeableConcept"])
        if label:
            return label
    if "valueString" in resource:
        return str(resource["valueString"]).strip()[:100]
    return None


def patient_name(patient):
    names = patient.get("name") or []
    if not names:
        return "Unknown Patient"
    n = names[0] or {}
    given = " ".join(str(g) for g in (n.get("given") or []))
    family = str(n.get("family") or "")
    full = f"{given} {family}".strip()
    return full or "Unknown Patient"


# ---- Narrative builder ---------------------------------------------

def build_narrative(resources):
    patient = None
    buckets = {
        "Condition": [],
        "MedicationRequest": [],
        "Observation": [],
        "Procedure": [],
        "AllergyIntolerance": [],
        "Immunization": [],
    }

    for r in resources:
        rt = r.get("resourceType")
        if rt in SKIP_LOW_VALUE_RESOURCES:
            continue
        if rt == "Patient":
            patient = r
        elif rt in buckets:
            buckets[rt].append(r)

    if not patient:
        return ""

    name = patient_name(patient)
    gender = patient.get("gender") or "unknown"
    birth = patient.get("birthDate") or "unknown"

    lines = [
        f"Patient: {name}",
        f"Gender: {gender}. Born: {birth}.",
        "",
    ]

    # Conditions (deduplicated)
    if buckets["Condition"]:
        lines.append("Conditions:")
        seen = set()
        for c in buckets["Condition"]:
            label = display_code(c.get("code"))
            if label and label not in seen:
                seen.add(label)
                lines.append(f"- {name} has been diagnosed with {label}.")
            if len(seen) >= MAX_ITEMS_PER_SECTION:
                break
        lines.append("")

    # Medications (deduplicated)
    if buckets["MedicationRequest"]:
        lines.append("Medications:")
        seen = set()
        for m in buckets["MedicationRequest"]:
            label = display_code(m.get("medicationCodeableConcept"))
            if label and label not in seen:
                seen.add(label)
                lines.append(f"- {name} was prescribed {label}.")
            if len(seen) >= MAX_ITEMS_PER_SECTION:
                break
        lines.append("")

    # Observations (deduplicated, only meaningful ones)
    if buckets["Observation"]:
        lines.append("Observations:")
        seen = set()
        for o in buckets["Observation"]:
            label = display_code(o.get("code"))
            value = observation_value(o)
            if label and value and (label, value) not in seen:
                seen.add((label, value))
                lines.append(f"- {name} had {label} recorded as {value}.")
            if len(seen) >= MAX_ITEMS_PER_SECTION:
                break
        lines.append("")

    # Procedures
    if buckets["Procedure"]:
        lines.append("Procedures:")
        seen = set()
        for p in buckets["Procedure"]:
            label = display_code(p.get("code"))
            if label and label not in seen:
                seen.add(label)
                lines.append(f"- {name} underwent {label}.")
            if len(seen) >= MAX_ITEMS_PER_SECTION:
                break
        lines.append("")

    # Allergies
    if buckets["AllergyIntolerance"]:
        lines.append("Allergies:")
        seen = set()
        for a in buckets["AllergyIntolerance"]:
            label = display_code(a.get("code"))
            if label and label not in seen:
                seen.add(label)
                lines.append(f"- {name} has an allergy to {label}.")
            if len(seen) >= MAX_ITEMS_PER_SECTION:
                break
        lines.append("")

    # Immunizations
    if buckets["Immunization"]:
        lines.append("Immunizations:")
        seen = set()
        for imm in buckets["Immunization"]:
            label = display_code(imm.get("vaccineCode"))
            if label and label not in seen:
                seen.add(label)
                lines.append(f"- {name} received immunization {label}.")
            if len(seen) >= MAX_ITEMS_PER_SECTION:
                break
        lines.append("")

    # Cross-relationship sentences (helps GraphRAG entity linking)
    cond_names = []
    for c in buckets["Condition"][:5]:
        cn = display_code(c.get("code"))
        if cn:
            cond_names.append(cn)

    med_names = []
    for m in buckets["MedicationRequest"][:5]:
        mn = display_code(m.get("medicationCodeableConcept"))
        if mn:
            med_names.append(mn)

    if cond_names and med_names:
        lines.append("Clinical Relationships:")
        for cn in cond_names[:3]:
            for mn in med_names[:3]:
                lines.append(f"- {mn} may treat {cn} in {name}.")
        lines.append("")

    return "\n".join(lines).strip() + "\n"


# ---- Main ----------------------------------------------------------

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Find bundles, skip meta files
    bundle_files = []
    for f in sorted(RAW_DIR.rglob("*.json")):
        name_lower = f.name.lower()
        if name_lower.startswith("hospitalinformation"):
            continue
        if name_lower.startswith("practitionerinformation"):
            continue
        bundle_files.append(f)

    if not bundle_files:
        print(f"No FHIR bundles found in {RAW_DIR}")
        sys.exit(1)

    print(f"Found {len(bundle_files)} FHIR bundles in {RAW_DIR}")

    created = 0
    skipped = 0
    truncated = 0
    total_output_bytes = 0

    for i, path in enumerate(bundle_files):
        try:
            with open(path, "r", encoding="utf-8") as f:
                bundle = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"  Skipping {path.name}: {e}")
            skipped += 1
            continue

        if bundle.get("resourceType") != "Bundle":
            skipped += 1
            continue

        resources = []
        for entry in (bundle.get("entry") or []):
            if isinstance(entry, dict):
                r = entry.get("resource")
                if isinstance(r, dict):
                    resources.append(r)

        narrative = build_narrative(resources)

        if not narrative.strip():
            skipped += 1
            continue

        # Enforce size cap
        encoded = narrative.encode("utf-8")
        if len(encoded) > MAX_OUTPUT_BYTES:
            narrative = encoded[:MAX_OUTPUT_BYTES].decode("utf-8", errors="ignore")
            truncated += 1

        out_path = OUTPUT_DIR / f"patient_{i:04d}.txt"
        out_path.write_text(narrative, encoding="utf-8")
        total_output_bytes += len(narrative.encode("utf-8"))
        created += 1

        if (i + 1) % 100 == 0:
            print(f"  Processed {i + 1}/{len(bundle_files)}")

    print()
    print(f"Created  : {created} files in {OUTPUT_DIR}")
    print(f"Skipped  : {skipped}")
    print(f"Truncated: {truncated} (exceeded {MAX_OUTPUT_BYTES} bytes)")
    print(f"Total    : {total_output_bytes:,} bytes ({total_output_bytes / 1024:.1f} KB)")
    if created:
        print(f"Average  : {total_output_bytes / created:,.0f} bytes per file")


if __name__ == "__main__":
    main()