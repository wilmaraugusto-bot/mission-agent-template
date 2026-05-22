from __future__ import annotations

from zipfile import ZipFile

from agent.loaders.document_loader import load_document


def test_load_document_valid_txt(tmp_path):
    path = tmp_path / "minuta.txt"
    path.write_text("Minuta simulada com clausula de confidencialidade.", encoding="utf-8")

    result = load_document(str(path))

    assert result["source_file"] == str(path)
    assert result["file_type"] == "txt"
    assert "Minuta simulada" in result["extracted_text"]
    assert result["warnings"] == []


def test_load_document_unsupported_extension(tmp_path):
    path = tmp_path / "minuta.rtf"
    path.write_text("conteudo", encoding="utf-8")

    result = load_document(str(path))

    assert result["file_type"] == "rtf"
    assert result["extracted_text"] == ""
    assert "nao suportada" in result["warnings"][0]


def test_load_document_missing_file(tmp_path):
    path = tmp_path / "ausente.txt"

    result = load_document(str(path))

    assert result["file_type"] == "txt"
    assert result["extracted_text"] == ""
    assert result["warnings"] == ["Arquivo inexistente."]


def test_load_document_empty_txt(tmp_path):
    path = tmp_path / "vazio.txt"
    path.write_text("   \n", encoding="utf-8")

    result = load_document(str(path))

    assert result["extracted_text"].strip() == ""
    assert "vazio" in result["warnings"][0]


def test_load_document_simple_docx(tmp_path):
    path = tmp_path / "minuta.docx"
    document_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p><w:r><w:t>Primeiro paragrafo simulado.</w:t></w:r></w:p>
    <w:p><w:r><w:t>Segundo paragrafo simulado.</w:t></w:r></w:p>
  </w:body>
</w:document>
"""
    with ZipFile(path, "w") as archive:
        archive.writestr("word/document.xml", document_xml)

    result = load_document(str(path))

    assert result["file_type"] == "docx"
    assert "Primeiro paragrafo simulado." in result["extracted_text"]
    assert "Segundo paragrafo simulado." in result["extracted_text"]
    assert result["warnings"] == []


def test_load_document_simple_pdf(tmp_path):
    path = tmp_path / "minuta.pdf"
    pdf_bytes = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 4 0 R >> >> /MediaBox [0 0 612 792] /Contents 5 0 R >>
endobj
4 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
5 0 obj
<< /Length 77 >>
stream
BT
/F1 24 Tf
100 700 Td
(Minuta simulada em PDF digital) Tj
ET
endstream
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000241 00000 n 
0000000311 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
438
%%EOF
"""
    path.write_bytes(pdf_bytes)

    result = load_document(str(path))

    assert result["file_type"] == "pdf"
    assert "Minuta simulada em PDF digital" in result["extracted_text"]


def test_load_document_blank_png_uses_ocr_with_warning(tmp_path):
    from PIL import Image

    path = tmp_path / "imagem.png"
    Image.new("RGB", (120, 60), "white").save(path)

    result = load_document(str(path))

    assert result["file_type"] == "png"
    assert result["extracted_text"].strip() == ""
    assert result["warnings"]
