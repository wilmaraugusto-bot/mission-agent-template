# Plano Experimental Pos-Desafio

Esta branch experimental adiciona loaders de documentos simulados ao
RegulaGuard Agent sem alterar o fluxo entregue na `main`.

## Escopo da Etapa 1

- Carregar arquivos `.txt`, `.pdf` digital com texto selecionavel e `.docx`.
- Retornar texto extraido e warnings por meio de uma funcao unica:

```python
load_document(path: str) -> dict
```

- Manter `data/sample_input.json`, CLI atual, `docker compose up --build`,
  pytest e `scripts/acceptance_check.py`.
- Nao enviar texto extraido automaticamente ao Gemini.
- Nao implementar frontend.
- Nao implementar OCR.

## Uso experimental

Coloque arquivos simulados em `uploads/` somente no ambiente local. O diretorio
esta ignorado pelo Git para evitar versionar uploads ou documentos enviados.

Exemplo:

```python
from agent.loaders.document_loader import load_document

result = load_document("uploads/minuta_simulada.txt")
```

Retorno esperado:

```python
{
    "source_file": "uploads/minuta_simulada.txt",
    "file_type": "txt",
    "extracted_text": "...",
    "warnings": [],
}
```

## Limites

- Use apenas documentos simulados.
- Nao use contratos reais.
- Nao use dados reais.
- Nao ha OCR nesta etapa.
- PDFs escaneados ou sem texto selecionavel retornam warning.
- O conteudo extraido nao deve ser salvo em logs.
- Todas as acoes do agente continuam em `dry-run`.
