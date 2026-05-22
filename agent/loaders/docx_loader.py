from __future__ import annotations

from pathlib import Path
from zipfile import BadZipFile, ZipFile
import xml.etree.ElementTree as ET


WORD_NAMESPACE = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def load_docx(path: Path) -> tuple[str, list[str]]:
    warnings: list[str] = []
    try:
        with ZipFile(path) as archive:
            document_xml = archive.read("word/document.xml")
    except (BadZipFile, KeyError):
        return "", ["Arquivo DOCX invalido ou sem word/document.xml."]

    try:
        root = ET.fromstring(document_xml)
    except ET.ParseError:
        return "", ["Arquivo DOCX contem XML invalido."]

    paragraphs: list[str] = []
    for paragraph in root.iter(f"{WORD_NAMESPACE}p"):
        parts = [node.text or "" for node in paragraph.iter(f"{WORD_NAMESPACE}t")]
        text = "".join(parts).strip()
        if text:
            paragraphs.append(text)

    extracted_text = "\n".join(paragraphs)
    if not extracted_text.strip():
        warnings.append("Arquivo DOCX sem paragrafos de texto extraiveis.")

    return extracted_text, warnings
