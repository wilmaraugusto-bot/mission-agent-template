# Mission Agent Template

Base minima em Python para um agente autonomo de IA em modo `dry-run`, adaptavel a diferentes temas do desafio Missao IA + Open Challenge Dev.

## O que esta base faz

- Le `data/sample_input.json`.
- Gera decisoes mockadas.
- Gera acoes mockadas.
- Aplica uma politica simples de seguranca.
- Salva os artefatos em `runs/<timestamp>/`.

O provedor padrao de LLM e `mock`. Gemini/OpenAI ainda nao foram implementados.

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
DRY_RUN=true
```
