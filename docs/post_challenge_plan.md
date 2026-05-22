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

## Etapa 2 - Tela Streamlit experimental e OCR

A branch tambem inclui uma tela experimental em `ui/app.py`. Ela nao substitui o
fluxo CLI e nao e iniciada por padrao com `docker compose up --build`.

Para rodar a tela:

```bash
docker compose up ui --build
```

Acesse:

```text
http://localhost:8501
```

Recursos da tela:

- visual em tema escuro corporativo proprio, sem copiar logos, fontes, imagens
  ou identidade visual de terceiros;
- upload de `.txt`, `.pdf`, `.docx`, `.png`, `.jpg` e `.jpeg`;
- uso de `agent.loaders.document_loader.load_document`;
- exibicao de nome, tipo, avisos e previa limitada do texto extraido;
- geracao de input temporario compativel com o agente;
- botao **Analisar documento** para executar o fluxo em `dry-run`;
- abas para Entrada, Texto extraido, Analise e Artefatos;
- cards de resumo com risco, revisao humana, documentos, clausulas e acoes;
- exibicao do `report.md`;
- downloads de `report.md`, `decisions.json` e `actions.json`;
- selecao de provider `mock` ou `gemini`, com `mock` como padrao.

OCR experimental:

- imagens `.png`, `.jpg` e `.jpeg` usam `pytesseract` + Pillow;
- PDFs continuam tentando extracao textual normal primeiro;
- se o PDF nao tiver texto extraivel, o loader tenta OCR com `pdf2image`,
  `pytesseract` e `poppler-utils`;
- se OCR nao estiver disponivel ou nao extrair texto, o loader retorna warning
  claro e nao quebra o fluxo.

Limites adicionais:

- nao envie contratos reais;
- nao envie dados pessoais reais;
- a interface nao pede nem salva chave de API;
- Gemini usa apenas `GEMINI_API_KEY` do ambiente e faz fallback para `mock`;
- nao ha banco de dados;
- nao ha autenticacao.

## Testes manuais realizados

A branch experimental `post-challenge-ui-docs` foi validada manualmente com os
seguintes cenarios:

- upload de arquivo `.txt` simulado;
- upload de PDF digital com texto selecionavel;
- upload de imagem para OCR experimental;
- geracao de relatorio na tela;
- download de `report.md`, `decisions.json` e `actions.json`;
- execucao preservada do fluxo CLI original com `data/sample_input.json`.

Limitacoes conhecidas:

- OCR e experimental;
- a qualidade do OCR depende da nitidez, contraste, orientacao e resolucao da
  imagem;
- documentos reais nao devem ser usados;
- contratos reais nao devem ser usados;
- dados pessoais reais nao devem ser enviados;
- o agente nao emite parecer juridico final;
- o agente nao aprova nem reprova contratos;
- todas as acoes continuam em `dry-run`;
- a versao oficial entregue no desafio continua na branch `main`.
