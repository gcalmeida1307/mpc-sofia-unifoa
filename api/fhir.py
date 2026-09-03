from __future__ import annotations

import json
import re
import sqlite3
import uuid
from datetime import UTC, datetime
from typing import Any

from .auth import DATABASE_PATH

FHIR_RELEASE = "4.0.1"
FHIR_RESOURCE_TYPES = {
    "Patient",
    "Observation",
    "Condition",
    "Encounter",
    "MedicationRequest",
    "CarePlan",
    "DiagnosticReport",
    "AllergyIntolerance",
    "Practitioner",
    "Bundle",
}
_RESOURCE_ID = re.compile(r"^[A-Za-z0-9.-]{1,64}$")


def _connection() -> sqlite3.Connection:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_fhir_store() -> None:
    with _connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS fhir_resources (
                resource_type TEXT NOT NULL,
                resource_id TEXT NOT NULL,
                resource_json TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (resource_type, resource_id)
            )
            """
        )
        connection.commit()


def _check_type(resource_type: str) -> None:
    if resource_type not in FHIR_RESOURCE_TYPES:
        raise ValueError(f"Tipo FHIR não habilitado: {resource_type}")


def validate_resource(resource_type: str, resource: dict[str, Any]) -> dict[str, Any]:
    _check_type(resource_type)
    if resource.get("resourceType") != resource_type:
        raise ValueError("resourceType não corresponde à rota FHIR")
    resource = json.loads(json.dumps(resource, ensure_ascii=False))
    resource_id = str(resource.get("id") or uuid.uuid4().hex)
    if not _RESOURCE_ID.fullmatch(resource_id):
        raise ValueError("id FHIR inválido")
    resource["id"] = resource_id
    if resource_type == "Observation":
        if resource.get("status") not in {"registered", "preliminary", "final", "amended", "corrected", "cancelled", "entered-in-error", "unknown"}:
            raise ValueError("Observation exige um status FHIR válido")
        if not resource.get("code"):
            raise ValueError("Observation exige code")
    return resource


def save_resource(resource_type: str, resource: dict[str, Any]) -> dict[str, Any]:
    resource = validate_resource(resource_type, resource)
    resource.setdefault("meta", {})["lastUpdated"] = datetime.now(UTC).isoformat()
    with _connection() as connection:
        connection.execute(
            "INSERT INTO fhir_resources (resource_type, resource_id, resource_json, updated_at) VALUES (?, ?, ?, ?) ON CONFLICT(resource_type, resource_id) DO UPDATE SET resource_json=excluded.resource_json, updated_at=excluded.updated_at",
            (resource_type, resource["id"], json.dumps(resource, ensure_ascii=False), resource["meta"]["lastUpdated"]),
        )
        connection.commit()
    return resource


def get_resource(resource_type: str, resource_id: str) -> dict[str, Any] | None:
    _check_type(resource_type)
    with _connection() as connection:
        row = connection.execute("SELECT resource_json FROM fhir_resources WHERE resource_type = ? AND resource_id = ?", (resource_type, resource_id)).fetchone()
    return json.loads(row["resource_json"]) if row else None


def _contains_patient(resource: dict[str, Any], patient_id: str) -> bool:
    references = []
    for key in ("subject", "patient", "individual", "beneficiary"):
        value = resource.get(key)
        if isinstance(value, dict) and isinstance(value.get("reference"), str):
            references.append(value["reference"])
    return any(reference.rstrip("/").endswith(f"Patient/{patient_id}") for reference in references)


def _contains_code(resource: dict[str, Any], code: str) -> bool:
    serialized = json.dumps(resource.get("code", {}), ensure_ascii=False).casefold()
    return code.casefold() in serialized


def search_resources(resource_type: str, patient_id: str | None = None, code: str | None = None, count: int = 50) -> dict[str, Any]:
    _check_type(resource_type)
    count = max(1, min(count, 200))
    with _connection() as connection:
        rows = connection.execute("SELECT resource_json FROM fhir_resources WHERE resource_type = ? ORDER BY updated_at DESC", (resource_type,)).fetchall()
    resources = [json.loads(row["resource_json"]) for row in rows]
    if patient_id:
        resources = [resource for resource in resources if _contains_patient(resource, patient_id)]
    if code:
        resources = [resource for resource in resources if _contains_code(resource, code)]
    resources = resources[:count]
    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": len(resources),
        "entry": [{"fullUrl": f"/fhir/{resource['resourceType']}/{resource['id']}", "resource": resource} for resource in resources],
    }


def patient_context(patient_id: str) -> dict[str, Any]:
    resources: list[dict[str, Any]] = []
    patient = get_resource("Patient", patient_id)
    if patient:
        resources.append(patient)
    for resource_type in ("Observation", "Condition", "Encounter", "DiagnosticReport", "AllergyIntolerance", "CarePlan", "MedicationRequest"):
        resources.extend(search_resources(resource_type, patient_id=patient_id, count=200).get("entry", []))
    return {
        "resourceType": "Bundle",
        "type": "collection",
        "total": len(resources),
        "entry": [{"resource": item.get("resource", item)} for item in resources],
    }


def capability_statement() -> dict[str, Any]:
    return {
        "resourceType": "CapabilityStatement",
        "status": "active",
        "kind": "instance",
        "fhirVersion": FHIR_RELEASE,
        "format": ["json"],
        "implementation": {"description": "Sofia local FHIR store"},
        "rest": [{"mode": "server", "resource": [{"type": resource_type, "interaction": [{"code": "read"}, {"code": "search-type"}, {"code": "create"}, {"code": "update"}]} for resource_type in sorted(FHIR_RESOURCE_TYPES)]}],
    }
