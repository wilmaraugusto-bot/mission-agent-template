from __future__ import annotations

from zipfile import ZipFile

from ui.app import _safe_upload_name, build_temporary_mission_input, create_analysis_zip


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


def test_create_analysis_zip_includes_available_artifacts(tmp_path):
    (tmp_path / "report.md").write_text("# Relatorio", encoding="utf-8")
    (tmp_path / "decisions.json").write_text("[]", encoding="utf-8")
    (tmp_path / "actions.json").write_text("[]", encoding="utf-8")
    (tmp_path / "temporary_upload.txt").write_text("nao incluir", encoding="utf-8")

    package = create_analysis_zip(tmp_path)
    zip_path = tmp_path / "analysis.zip"
    zip_path.write_bytes(package)

    with ZipFile(zip_path) as zip_file:
        assert sorted(zip_file.namelist()) == ["actions.json", "decisions.json", "report.md"]
        assert zip_file.read("report.md").decode("utf-8") == "# Relatorio"
