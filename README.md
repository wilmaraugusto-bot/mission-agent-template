# RegulaGuard Agent

Agente autonomo de triagem regulatoria, LGPD e riscos contratuais simulados para
o Dia 2 da Missao IA + Open Challenge Dev.

## Descricao

O RegulaGuard Agent apoia processos criticos em setores regulados, com foco em
triagem juridica/administrativa e analise de minutas contratuais simuladas de
onboarding. O projeto nao usa dados reais, nao usa contratos reais e nao emite
parecer juridico final.

## O desafio

Tema oficial: IA para Resolucao de Problemas Criticos em Setores Regulados.

O desafio pede uma solucao de IA capaz de melhorar consistencia, precisao,
protecao de dados sensiveis, auditabilidade e apoio a decisao em contextos como
Juridico, Saude ou Financas.

## A solucao

O agente executa um fluxo end-to-end:

- coleta dados simulados em `data/sample_input.json`;
- analisa contexto regulatorio, LGPD e riscos contratuais simulados;
- toma decisoes estruturadas com validacao Pydantic;
- executa acoes simuladas em `dry-run`;
- aplica guardrails de seguranca;
- gera artefatos auditaveis em `runs/<timestamp>/`.

As acoes simuladas incluem mascaramento, classificacao de risco, solicitacao de
documentos, sinalizacao de clausulas ausentes, checklist de conformidade,
roteamento para revisao humana, registro de auditoria e relatorio.

## Justificativa das escolhas tecnicas

- Python simples para reduzir atrito de execucao.
- Docker Compose como caminho principal de teste.
- Pydantic para validar entradas, decisoes, acoes e artefatos.
- Provider `mock` como padrao para funcionar sem internet e sem API paga.
- Gemini/OpenAI apenas opcionais via `.env`, com fallback seguro para `mock`.
- Sem frontend e sem banco de dados para manter a entrega reproduzivel.

## Conformidade regulatoria

O RegulaGuard faz triagem inicial e nao substitui profissionais juridicos,
compliance, DPO ou areas reguladas. Casos de alto risco, risco critico, baixa
confianca, dados sensiveis ou clausulas criticas ausentes sao encaminhados para
human-in-the-loop.

## LGPD e protecao de dados

O projeto usa apenas dados ficticios e contratos simulados. Dados pessoais e
sensiveis simulados sao mascarados no fluxo de decisao e no relatorio. O agente
aplica minimizacao, postura conservadora e bloqueia qualquer acao real fora do
`dry-run`.

## Auditabilidade e explicabilidade

Cada execucao gera:

```text
runs/<timestamp>/decisions.json
runs/<timestamp>/actions.json
runs/<timestamp>/report.md
```

O relatorio inclui resumo executivo, itens analisados, dados detectados por
categoria, dados mascarados, risco regulatorio, pendencias, justificativas,
acoes em `dry-run`, revisao humana, trilha de auditoria, limites e melhorias
futuras.

## Human-in-the-loop

O agente encaminha para revisao humana quando:

- risco regulatorio e alto ou critico;
- ha baixa confianca;
- existem dados sensiveis simulados;
- faltam clausulas criticas, como confidencialidade, retencao/descarte,
  finalidade de tratamento ou matriz de responsabilidades;
- a decisao pode impactar direitos, obrigacoes ou conformidade.

O agente nao aprova contrato, nao reprova contrato e nao emite parecer juridico
final.

## Uso de IA e fallback mock

O provedor padrao de LLM e `mock`, e esse modo deve funcionar sem internet e sem
chave de API. Gemini e OpenAI sao opcionais e ficam atras de variaveis de ambiente;
se a chave estiver vazia ou o provider falhar, o agente registra um warning e volta
automaticamente para `mock`.

## Pontos aprendidos

- Setores regulados exigem explicabilidade e auditoria, nao apenas resposta em texto.
- Fallback `mock` torna a entrega reproduzivel e segura.
- Human-in-the-loop e parte do desenho, nao um detalhe posterior.
- Dados simulados reduzem risco de exposicao durante demonstracoes.

## Dificuldades

- Equilibrar autonomia com limites eticos e juridicos.
- Representar riscos de LGPD sem usar dados reais.
- Manter o projeto simples e executavel via Docker.
- Evitar que o agente pareca chatbot em vez de fluxo autonomo.

## Melhorias futuras

- Matriz de risco configuravel por setor regulado.
- Biblioteca de clausulas ficticias para testes mais amplos.
- Revisao humana simulada com feedback estruturado.
- Exportacao de trilha de auditoria para sistemas internos.

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

O relatorio deve mostrar que o agente coletou dados, analisou contexto, tomou
decisoes, executou acoes em `dry-run` e registrou trilha auditavel.

## Tutorial de como testar

1. Confira que `.env` existe e mantem `LLM_PROVIDER=mock`.
2. Rode:

```bash
docker compose up --build
```

3. Rode os testes:

```bash
docker compose run --rm agent python -m pytest
```

4. Rode o acceptance check:

```bash
docker compose run --rm agent python scripts/acceptance_check.py
```

5. Abra o relatorio mais recente em `runs/<timestamp>/report.md`.

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
GEMINI_API_KEY=sua_chave_local
```

Com `LLM_PROVIDER=gemini`, o agente faz uma chamada real opcional ao Gemini para
gerar as decisoes. Se `GEMINI_API_KEY` estiver vazia ou a chamada falhar, o fluxo
usa `mock` automaticamente. Nao coloque chaves reais no repositorio.

```text
LLM_PROVIDER=openai
OPENAI_API_KEY=
```

OpenAI permanece opcional e sem chamada real nesta versao. O fluxo principal
continua validando as decisoes pelos modelos Pydantic antes de gerar acoes.

## Importante

- Nao use dados reais.
- Nao use contratos reais.
- Nao coloque chaves reais no repositorio.
- O modo basico deve continuar funcionando com `LLM_PROVIDER=mock`.
