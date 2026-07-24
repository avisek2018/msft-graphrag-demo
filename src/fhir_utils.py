"""Helper utilities for extracting values from FHIR R4 resources."""

from typing import Any, Dict, List, Optional


def display_code(concept: Optional[Dict[str, Any]]) -> str:
    """Return a human-readable label from a FHIR CodeableConcept."""
    if not concept or not isinstance(concept, dict):
        return "unknown"

    text = concept.get("text")
    if text:
        return str(text).strip()

    coding = concept.get("coding") or []
    if coding and isinstance(coding, list):
        first = coding[0] or {}
        return str(
            first.get("display")
            or first.get("code")
            or "unknown"
        ).strip()

    return "unknown"


def display_code_list(concepts: Optional[List[Dict[str, Any]]]) -> str:
    """Return a comma-separated label from a list of CodeableConcepts."""
    if not concepts or not isinstance(concepts, list):
        return "unknown"

    labels = [display_code(c) for c in concepts if isinstance(c, dict)]
    return ", ".join(labels) if labels else "unknown"


def observation_value(resource: Dict[str, Any]) -> str:
    """Extract a human-readable value from a FHIR Observation resource."""
    if "valueQuantity" in resource:
        q = resource["valueQuantity"] or {}
        value = q.get("value")
        unit = q.get("unit") or q.get("code") or ""
        if value is not None:
            return f"{value} {unit}".strip()

    if "valueCodeableConcept" in resource:
        return display_code(resource["valueCodeableConcept"])

    if "valueString" in resource:
        return str(resource["valueString"]).strip()

    if "valueBoolean" in resource:
        return str(resource["valueBoolean"])

    if "valueInteger" in resource:
        return str(resource["valueInteger"])

    return "unknown"


def patient_display_name(patient: Dict[str, Any]) -> str:
    """Extract a readable name from a FHIR Patient resource."""
    names = patient.get("name") or []
    if not names:
        return "Unknown Patient"

    first = names[0] or {}
    given_parts = first.get("given") or []
    given = " ".join(str(g) for g in given_parts).strip()
    family = str(first.get("family") or "").strip()

    full_name = f"{given} {family}".strip()
    return full_name or "Unknown Patient"


def patient_demographics(patient: Dict[str, Any]) -> Dict[str, str]:
    """Extract common demographic fields from a Patient resource."""
    gender = str(patient.get("gender") or "unknown")
    birth_date = str(patient.get("birthDate") or "unknown")

    city = state = country = "unknown"
    addresses = patient.get("address") or []
    if addresses:
        addr = addresses[0] or {}
        city = str(addr.get("city") or "unknown")
        state = str(addr.get("state") or "unknown")
        country = str(addr.get("country") or "unknown")

    return {
        "gender": gender,
        "birth_date": birth_date,
        "city": city,
        "state": state,
        "country": country,
    }


def get_date(resource: Dict[str, Any], *keys: str) -> str:
    """Return the first non-empty date field found on a resource."""
    for key in keys:
        value = resource.get(key)
        if value:
            return str(value)

    period = resource.get("period") or {}
    start = period.get("start")
    if start:
        return str(start)

    performed = resource.get("performedPeriod") or {}
    performed_start = performed.get("start")
    if performed_start:
        return str(performed_start)

    return "unknown date"