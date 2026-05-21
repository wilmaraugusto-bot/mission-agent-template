# Regras do Desafio Missão IA + Open Challenge Dev

Este arquivo e a fonte de verdade das regras do desafio para este projeto. Use-o
para orientar o Codex no dia do desafio, revisar a entrega e evitar mudanças que
quebrem os criterios obrigatorios.

## 1. Regras obrigatórias

- `README.md` completo na raiz.
- `Dockerfile` na raiz.
- `docker-compose.yml` na raiz.
- `.env` funcional na raiz, sem segredos reais.
- `.env.example` na raiz.
- Caso de teste explicito no `README.md`.
- `docker compose up --build` precisa funcionar first try.
- O projeto precisa ser um agente autonomo end-to-end, nao chatbot.
- O agente precisa coletar dados, analisar contexto, tomar decisoes, executar acoes e gerar relatorio.
- O modo basico precisa funcionar sem API externa paga.
- `LLM_PROVIDER=mock` deve ser o padrao.
- Gemini/OpenAI podem existir apenas como opcionais via `.env`.
- Nunca versionar chaves reais.
- Nao usar propriedade intelectual indevida de terceiros.
- Nao fugir do tema oficial.

## 2. Critérios de avaliação

- Inovacao e Criatividade: 25%.
- Qualidade Tecnica e Uso de IA: 25%.
- Impacto e Relevancia: 15%.
- Viabilidade Tecnica para Producao: 15%.
- Clareza da Entrega: 15%.
- Experiencia do Usuario: 5%.

## 3. Critérios eliminatórios

- Projeto nao subir via `docker compose` conforme `README.md`.
- Entrega sem `.env` funcional.
- `README.md` sem caso de teste.
- Projeto que nao rode first try.
- Solucao que seja chatbot em vez de agente autonomo.
- Entrega fora do prazo.
- Uso indevido de propriedade intelectual.
- Vazamento de chave real.

## 4. Checklist final antes da entrega

- Conferir se o tema oficial esta refletido no `README.md`, em `docs/theme.md`, na entrada de dados, nas decisoes, nas acoes e no relatorio.
- Confirmar que `README.md` explica o projeto, o problema escolhido, as variaveis de ambiente e o caso de teste.
- Confirmar que `Dockerfile`, `docker-compose.yml`, `.env` e `.env.example` existem na raiz.
- Confirmar que `.env` funciona sem segredos reais.
- Confirmar que `LLM_PROVIDER=mock` continua sendo o padrao.
- Confirmar que Gemini/OpenAI, se existirem, sao opcionais via `.env`.
- Rodar `docker compose up --build` e verificar que funciona na primeira tentativa.
- Rodar `docker compose run --rm agent python -m pytest`.
- Rodar `docker compose run --rm agent python scripts/acceptance_check.py`.
- Abrir o relatorio gerado em `runs/<timestamp>/report.md`.
- Verificar que o agente mostra fluxo end-to-end: coleta, analise, decisao, execucao e relatorio.
- Verificar que a solucao nao se apresenta como chatbot.
- Revisar `git diff` para garantir que nenhuma chave real, token ou segredo foi versionado.
- Revisar se nao ha uso indevido de marcas, textos, imagens, datasets ou propriedade intelectual de terceiros.
- Confirmar que a entrega esta dentro do tema oficial e nao resolve um problema fora do escopo.
