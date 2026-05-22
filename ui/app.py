from __future__ import annotations

import json
import re
import uuid
import unicodedata
from pathlib import Path
from typing import Any

from agent.config import load_settings
from agent.core.runner import AgentRunner
from agent.loaders.document_loader import load_document


UPLOADS_DIR = Path("uploads")
PREVIEW_LIMIT = 4000
DESCRIPTION_LIMIT = 1200
ESSENTIAL_TERMS = [
    "confidencialidade",
    "retencao",
    "descarte",
    "finalidade",
    "responsabilidades",
    "incidente",
]


def build_temporary_mission_input(
    extracted_text: str,
    source_file: str,
) -> dict[str, Any]:
    normalized_text = _normalize_text(extracted_text)
    present_terms = [term for term in ESSENTIAL_TERMS if term in normalized_text]
    missing_terms = [term for term in ESSENTIAL_TERMS if term not in normalized_text]
    description = _truncate_text(extracted_text.strip(), DESCRIPTION_LIMIT)
    if not description:
        description = "Documento enviado sem texto extraivel para analise experimental."

    task_id = f"upload-{uuid.uuid4().hex[:8]}"
    return {
        "theme": "RegulaGuard Agent Web - triagem experimental de documento simulado",
        "goal": (
            "Executar triagem regulatoria simulada em dry-run a partir de documento enviado "
            "experimentalmente, sem usar contratos reais."
        ),
        "context": {
            "source": "streamlit_experimental_ui",
            "source_file": source_file,
            "constraints": [
                "dry-run only",
                "sem dados reais",
                "sem contratos reais",
                "sem parecer juridico final",
                "sem aprovacao ou reprovacao automatica",
                "sem OCR nesta etapa",
            ],
        },
        "tasks": [
            {
                "id": task_id,
                "title": "Triagem experimental de documento enviado",
                "description": description,
                "priority": "high" if missing_terms else "medium",
                "sector": "juridico_compliance",
                "requester_type": "upload_experimental",
                "submitted_documents": [source_file],
                "document_type": "documento_enviado_simulado",
                "personal_data": [],
                "sensitive_data": [],
                "urgency": "medium",
                "declared_purpose": "Triagem experimental de documento simulado enviado pela interface web.",
                "contract_clauses": present_terms,
                "missing_clauses": missing_terms,
                "missing_documents": [],
                "confidence_hint": 0.72 if missing_terms else 0.84,
            }
        ],
    }


def _normalize_text(text: str) -> str:
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return ascii_text.lower()


def _truncate_text(text: str, limit: int) -> str:
    collapsed = re.sub(r"\s+", " ", text).strip()
    if len(collapsed) <= limit:
        return collapsed
    return f"{collapsed[:limit].rstrip()}..."


def _safe_upload_name(filename: str) -> str:
    stem = Path(filename).stem or "documento"
    suffix = Path(filename).suffix.lower()
    safe_stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", stem).strip("._") or "documento"
    return f"{uuid.uuid4().hex}_{safe_stem}{suffix}"


def _write_temporary_input(payload: dict[str, Any]) -> Path:
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    path = UPLOADS_DIR / f"mission_input_{uuid.uuid4().hex}.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def main() -> None:
    import streamlit as st

    st.set_page_config(page_title="RegulaGuard Agent Web", layout="wide")
    st.title("RegulaGuard Agent Web")

    st.warning(
        "Nao envie contratos reais. Nao envie dados pessoais reais. O modo e dry-run. "
        "O agente nao aprova/reprova contrato e nao emite parecer juridico final."
    )

    provider = st.selectbox("Provider", ["mock", "gemini"], index=0)
    uploaded_file = st.file_uploader(
        "Envie um documento simulado",
        type=["txt", "pdf", "docx"],
    )

    if uploaded_file is None:
        st.info("Envie um arquivo .txt, .pdf digital ou .docx para iniciar a triagem experimental.")
        return

    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    upload_path = UPLOADS_DIR / _safe_upload_name(uploaded_file.name)
    upload_path.write_bytes(uploaded_file.getbuffer())

    result = load_document(str(upload_path))

    st.subheader("Resultado da extracao")
    st.write(f"**Arquivo:** {Path(result['source_file']).name}")
    st.write(f"**Tipo:** {result['file_type']}")

    warnings = result.get("warnings", [])
    if warnings:
        for warning in warnings:
            st.warning(warning)
    else:
        st.success("Texto extraido sem avisos.")

    extracted_text = result.get("extracted_text", "")
    preview = _truncate_text(extracted_text, PREVIEW_LIMIT)
    st.text_area("Previa do texto extraido", preview, height=220)

    mission_input = build_temporary_mission_input(
        extracted_text=extracted_text,
        source_file=Path(result["source_file"]).name,
    )

    with st.expander("Input temporario gerado para o agente"):
        st.json(mission_input)

    if st.button("Analisar documento", type="primary"):
        input_path = _write_temporary_input(mission_input)
        settings = load_settings().model_copy(
            update={
                "llm_provider": provider,
                "input_path": input_path,
                "dry_run": True,
            }
        )
        run_dir = AgentRunner(settings).run()
        st.success(f"Execucao gerada em: {run_dir}")

        report_path = run_dir / "report.md"
        decisions_path = run_dir / "decisions.json"
        actions_path = run_dir / "actions.json"

        report_content = report_path.read_text(encoding="utf-8")
        st.subheader("Relatorio")
        st.markdown(report_content)

        st.download_button(
            "Baixar report.md",
            report_content,
            file_name="report.md",
            mime="text/markdown",
        )
        st.download_button(
            "Baixar decisions.json",
            decisions_path.read_text(encoding="utf-8"),
            file_name="decisions.json",
            mime="application/json",
        )
        st.download_button(
            "Baixar actions.json",
            actions_path.read_text(encoding="utf-8"),
            file_name="actions.json",
            mime="application/json",
        )


if __name__ == "__main__":
    main()
