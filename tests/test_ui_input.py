from __future__ import annotations

from ui.app import _safe_upload_name, build_temporary_mission_input


def test_build_temporary_mission_input_infers_missing_clauses():
    payload = build_temporary_mission_input(
        extracted_text="Minuta simulada com confidencialidade e finalidade declarada.",
        source_file="minuta_simulada.txt",
    )

    [task] = payload["tasks"]

    assert task["document_type"] == "documento_enviado_simulado"
    assert task["sector"] == "juridico_compliance"
    assert task["requester_type"] == "upload_experimental"
    assert task["personal_data"] == []
    assert task["sensitive_data"] == []
    assert "confidencialidade" in task["contract_clauses"]
    assert "finalidade" in task["contract_clauses"]
    assert "retencao" in task["missing_clauses"]
    assert "descarte" in task["missing_clauses"]
    assert "responsabilidades" in task["missing_clauses"]
    assert "incidente" in task["missing_clauses"]


def test_build_temporary_mission_input_truncates_description():
    payload = build_temporary_mission_input(
        extracted_text="texto " * 400,
        source_file="longo.txt",
    )

    description = payload["tasks"][0]["description"]

    assert len(description) <= 1203
    assert description.endswith("...")


def test_safe_upload_name_prevents_path_traversal():
    safe_name = _safe_upload_name("../../contrato real.pdf")

    assert "/" not in safe_name
    assert "\\" not in safe_name
    assert safe_name.endswith(".pdf")
    assert "contrato_real" in safe_name
