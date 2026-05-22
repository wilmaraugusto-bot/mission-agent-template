from __future__ import annotations

from pathlib import Path


def load_image_ocr(path: Path) -> tuple[str, list[str]]:
    warnings: list[str] = []
    try:
        from PIL import Image, UnidentifiedImageError
        import pytesseract
    except ImportError:
        return "", ["OCR nao disponivel: instale Pillow e pytesseract."]

    try:
        with Image.open(path) as image:
            text = pytesseract.image_to_string(image, lang="por+eng")
    except UnidentifiedImageError:
        return "", ["Imagem invalida ou ilegivel para OCR."]
    except pytesseract.TesseractNotFoundError:
        return "", ["OCR nao disponivel: binario tesseract nao encontrado."]
    except Exception:
        return "", ["Falha ao executar OCR na imagem."]

    if not text.strip():
        warnings.append("OCR executado, mas nenhum texto foi extraido da imagem.")

    return text, warnings


def load_pdf_ocr(path: Path) -> tuple[str, list[str]]:
    warnings: list[str] = []
    try:
        from pdf2image import convert_from_path
        import pytesseract
    except ImportError:
        return "", ["OCR de PDF nao disponivel: instale pdf2image, Pillow e pytesseract."]

    try:
        pages = convert_from_path(str(path), dpi=200)
    except Exception:
        return "", ["OCR de PDF nao disponivel ou PDF ilegivel; verifique poppler-utils."]

    page_texts: list[str] = []
    for index, page in enumerate(pages, start=1):
        try:
            text = pytesseract.image_to_string(page, lang="por+eng")
        except pytesseract.TesseractNotFoundError:
            return "", ["OCR nao disponivel: binario tesseract nao encontrado."]
        except Exception:
            warnings.append(f"Falha ao executar OCR na pagina {index} do PDF.")
            continue
        if text.strip():
            page_texts.append(text.strip())

    extracted_text = "\n\n".join(page_texts)
    if not extracted_text.strip():
        warnings.append("OCR executado no PDF, mas nenhum texto foi extraido.")

    return extracted_text, warnings
