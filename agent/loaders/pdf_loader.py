from __future__ import annotations

import re
from pathlib import Path


def load_pdf(path: Path) -> tuple[str, list[str]]:
    warnings: list[str] = []
    try:
        from pypdf import PdfReader
    except ImportError:
        fallback_text = _extract_uncompressed_literal_text(path)
        if fallback_text.strip():
            return fallback_text, warnings
        return "", ["Dependencia pypdf nao esta instalada; nao foi possivel ler PDF."]

    try:
        reader = PdfReader(str(path))
    except Exception:
        fallback_text = _extract_uncompressed_literal_text(path)
        if fallback_text.strip():
            return fallback_text, warnings
        return "", ["Arquivo PDF invalido ou corrompido."]

    pages_text: list[str] = []
    for index, page in enumerate(reader.pages, start=1):
        try:
            page_text = page.extract_text() or ""
        except Exception:
            warnings.append(f"Falha ao extrair texto da pagina {index} do PDF.")
            page_text = ""
        if page_text.strip():
            pages_text.append(page_text.strip())

    extracted_text = "\n\n".join(pages_text)
    if not extracted_text.strip():
        extracted_text = _extract_uncompressed_literal_text(path)

    if not extracted_text.strip():
        warnings.append("PDF sem texto selecionavel extraivel; OCR ainda nao e suportado.")

    return extracted_text, warnings


def _extract_uncompressed_literal_text(path: Path) -> str:
    """Best-effort fallback for simple digital PDFs with uncompressed text operators."""
    try:
        content = path.read_bytes()
    except OSError:
        return ""

    snippets: list[str] = []
    for raw_text in re.findall(rb"\((.*?)\)\s*Tj", content, flags=re.DOTALL):
        snippets.append(_decode_pdf_literal(raw_text))

    return "\n".join(snippet for snippet in snippets if snippet.strip())


def _decode_pdf_literal(raw_text: bytes) -> str:
    text = raw_text.decode("latin-1", errors="replace")
    replacements = {
        r"\(": "(",
        r"\)": ")",
        r"\\": "\\",
        r"\n": "\n",
        r"\r": "\r",
        r"\t": "\t",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    return text
