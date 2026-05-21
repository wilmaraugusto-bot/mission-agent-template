# Mission Agent Template

Base minima em Python para um agente autonomo de IA em modo `dry-run`, adaptavel a diferentes temas do desafio Missao IA + Open Challenge Dev.

## O que esta base faz

- Le `data/sample_input.json`.
- Gera decisoes mockadas.
- Gera acoes mockadas.
- Aplica uma politica simples de seguranca.
- Salva os artefatos em `runs/<timestamp>/`.

O provedor padrao de LLM e `mock`, e esse modo deve funcionar sem internet e sem
chave de API. Gemini e OpenAI sao opcionais e ficam atras de variaveis de ambiente;
se a chave estiver vazia ou o provider falhar, o agente registra um warning e volta
automaticamente para `mock`.

## Caso de teste obrigatorio

Execute:

```bash
docker compose up --build
```

Ao final, devem existir arquivos como:

```text
runs/<timestamp>/decisions.json
runs/<timestamp>/actions.json
runs/<timestamp>/report.md
```

## Execucao local opcional

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m agent.main
```

## Variaveis de ambiente

Veja `.env.example`. A configuracao padrao usa:

```text
LLM_PROVIDER=mock
LLM_FALLBACK_PROVIDER=mock
GEMINI_API_KEY=
OPENAI_API_KEY=
DRY_RUN=true
```

Providers opcionais:

```text
LLM_PROVIDER=gemini
GEMINI_API_KEY=
```

```text
LLM_PROVIDER=openai
OPENAI_API_KEY=
```

Nesta versao, Gemini/OpenAI sao stubs seguros: nao adicionam dependencia
obrigatoria de SDK externo nem fazem chamadas reais complexas. O fluxo principal
continua validando as decisoes pelos modelos Pydantic antes de gerar acoes.
