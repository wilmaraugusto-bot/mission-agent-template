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


def apply_custom_css() -> None:
    import streamlit as st

    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at 15% 10%, rgba(78, 70, 229, 0.22), transparent 26%),
                radial-gradient(circle at 85% 0%, rgba(219, 39, 119, 0.16), transparent 28%),
                linear-gradient(135deg, #080b14 0%, #101827 48%, #090b12 100%);
            color: #e5e7eb;
        }
        .block-container {
            padding-top: 2.25rem;
            max-width: 1180px;
        }
        h1, h2, h3 {
            color: #f8fafc;
            letter-spacing: 0;
        }
        div[data-testid="stTabs"] button {
            color: #cbd5e1;
            background: rgba(15, 23, 42, 0.72);
            border-radius: 6px 6px 0 0;
        }
        div[data-testid="stTabs"] button[aria-selected="true"] {
            color: #ffffff;
            border-bottom-color: #a855f7;
        }
        .rg-card {
            padding: 1rem;
            border: 1px solid rgba(148, 163, 184, 0.24);
            border-radius: 8px;
            background: rgba(15, 23, 42, 0.76);
            box-shadow: 0 18px 60px rgba(0, 0, 0, 0.18);
            min-height: 106px;
        }
        .rg-card-label {
            font-size: 0.78rem;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.35rem;
        }
        .rg-card-value {
            color: #f8fafc;
            font-size: 1.2rem;
            font-weight: 700;
            line-height: 1.25;
        }
        .rg-badge {
            display: inline-flex;
            align-items: center;
            padding: 0.22rem 0.58rem;
            border-radius: 999px;
            font-weight: 700;
            font-size: 0.82rem;
            border: 1px solid rgba(255, 255, 255, 0.14);
        }
        .risk-baixo { background: rgba(16, 185, 129, 0.18); color: #6ee7b7; }
        .risk-medio { background: rgba(59, 130, 246, 0.20); color: #93c5fd; }
        .risk-alto { background: rgba(245, 158, 11, 0.20); color: #fcd34d; }
        .risk-critico { background: rgba(244, 63, 94, 0.22); color: #fda4af; }
        .rg-hero {
            padding: 1rem 1.1rem;
            border: 1px solid rgba(168, 85, 247, 0.28);
            border-radius: 8px;
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(17, 24, 39, 0.82));
            margin-bottom: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


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
                "OCR experimental apenas quando necessario",
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


def _risk_badge(risk: str) -> str:
    risk_value = risk or "baixo"
    return f'<span class="rg-badge risk-{risk_value}">{risk_value.upper()}</span>'


def _card(label: str, value: str) -> str:
    return (
        '<div class="rg-card">'
        f'<div class="rg-card-label">{label}</div>'
        f'<div class="rg-card-value">{value}</div>'
        "</div>"
    )


def _analysis_summary(run_dir: Path) -> dict[str, Any]:
    decisions = json.loads((run_dir / "decisions.json").read_text(encoding="utf-8"))
    actions = json.loads((run_dir / "actions.json").read_text(encoding="utf-8"))
    first_decision = decisions[0] if decisions else {}
    missing_documents = first_decision.get("missing_documents", [])
    missing_clauses = first_decision.get("missing_contract_clauses", [])
    return {
        "risk": first_decision.get("regulatory_risk", "baixo"),
        "human_review": "sim" if first_decision.get("requires_human_review", False) else "nao",
        "missing_documents": ", ".join(missing_documents) if missing_documents else "nenhum",
        "missing_clauses": ", ".join(missing_clauses) if missing_clauses else "nenhuma",
        "dry_run_actions": str(len(actions)),
    }


def _render_summary_cards(run_dir: Path) -> None:
    import streamlit as st

    summary = _analysis_summary(run_dir)
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.markdown(_card("Risco regulatorio", _risk_badge(summary["risk"])), unsafe_allow_html=True)
    col2.markdown(_card("Revisao humana", summary["human_review"]), unsafe_allow_html=True)
    col3.markdown(_card("Documentos ausentes", summary["missing_documents"]), unsafe_allow_html=True)
    col4.markdown(_card("Clausulas ausentes", summary["missing_clauses"]), unsafe_allow_html=True)
    col5.markdown(_card("Acoes em dry-run", summary["dry_run_actions"]), unsafe_allow_html=True)


def main() -> None:
    import streamlit as st

    st.set_page_config(page_title="RegulaGuard Agent Web", layout="wide")
    apply_custom_css()
    st.title("RegulaGuard Agent Web")
    st.markdown(
        '<div class="rg-hero">Triagem experimental de documentos simulados para LGPD, '
        "compliance e riscos contratuais. Interface propria em tema escuro corporativo, "
        "sem uso de assets ou identidade visual de terceiros.</div>",
        unsafe_allow_html=True,
    )

    st.warning(
        "Nao envie contratos reais. Nao envie dados pessoais reais. O modo e dry-run. "
        "O agente nao aprova/reprova contrato e nao emite parecer juridico final."
    )

    if "document_result" not in st.session_state:
        st.session_state.document_result = None
    if "mission_input" not in st.session_state:
        st.session_state.mission_input = None
    if "run_dir" not in st.session_state:
        st.session_state.run_dir = None

    tab_input, tab_text, tab_analysis, tab_artifacts = st.tabs(
        ["Entrada", "Texto extraido", "Analise", "Artefatos"]
    )

    with tab_input:
        provider = st.selectbox("Provider", ["mock", "gemini"], index=0)
        uploaded_file = st.file_uploader(
            "Envie um documento simulado",
            type=["txt", "pdf", "docx", "png", "jpg", "jpeg"],
        )
        st.caption("OCR experimental esta disponivel para imagens e PDFs sem texto selecionavel.")

        if uploaded_file is not None:
            UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
            upload_path = UPLOADS_DIR / _safe_upload_name(uploaded_file.name)
            upload_path.write_bytes(uploaded_file.getbuffer())

            result = load_document(str(upload_path))
            extracted_text = result.get("extracted_text", "")
            mission_input = build_temporary_mission_input(
                extracted_text=extracted_text,
                source_file=Path(result["source_file"]).name,
            )
            st.session_state.document_result = result
            st.session_state.mission_input = mission_input
            st.session_state.provider = provider
            st.success("Documento carregado para triagem experimental.")
        else:
            st.info("Envie um arquivo .txt, .pdf, .docx, .png, .jpg ou .jpeg para iniciar.")

    with tab_text:
        result = st.session_state.document_result
        if result is None:
            st.info("Nenhum documento carregado ainda.")
        else:
            st.subheader("Resultado da extracao")
            st.write(f"**Arquivo:** {Path(result['source_file']).name}")
            st.write(f"**Tipo:** {result['file_type']}")

            warnings = result.get("warnings", [])
            if warnings:
                for warning in warnings:
                    st.warning(warning)
            else:
                st.success("Texto extraido sem avisos.")

            preview = _truncate_text(result.get("extracted_text", ""), PREVIEW_LIMIT)
            st.text_area("Previa do texto extraido", preview, height=260)

            with st.expander("Input temporario gerado para o agente"):
                st.json(st.session_state.mission_input)

    with tab_analysis:
        mission_input = st.session_state.mission_input
        provider = st.session_state.get("provider", "mock")
        st.write(f"Provider selecionado: `{provider}`")

        if st.button("Analisar documento", type="primary", disabled=mission_input is None):
            input_path = _write_temporary_input(mission_input)
            settings = load_settings().model_copy(
                update={
                    "llm_provider": provider,
                    "input_path": input_path,
                    "dry_run": True,
                }
            )
            run_dir = AgentRunner(settings).run()
            st.session_state.run_dir = run_dir
            st.success(f"Execucao gerada em: {run_dir}")

        if st.session_state.run_dir is not None:
            _render_summary_cards(Path(st.session_state.run_dir))
            report_path = Path(st.session_state.run_dir) / "report.md"
            st.subheader("Relatorio")
            st.markdown(report_path.read_text(encoding="utf-8"))
        elif mission_input is None:
            st.info("Carregue um documento na aba Entrada antes de analisar.")

    with tab_artifacts:
        run_dir = st.session_state.run_dir
        if run_dir is None:
            st.info("Nenhuma execucao gerada ainda.")
            return

        run_dir = Path(run_dir)
        report_path = run_dir / "report.md"
        decisions_path = run_dir / "decisions.json"
        actions_path = run_dir / "actions.json"

        report_content = report_path.read_text(encoding="utf-8")
        st.write(f"Execucao: `{run_dir}`")

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
