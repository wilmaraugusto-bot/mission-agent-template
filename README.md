# RegulaGuard Agent

Solucao de IA baseada em agente controlado para triagem regulatoria, LGPD e
riscos contratuais simulados no Dia 2 da Missao IA + Open Challenge Dev.

## Descricao

O RegulaGuard Agent apoia processos criticos em setores regulados, com foco em
triagem regulatoria, juridica, compliance e analise de riscos contratuais
simulados em minutas ficticias de onboarding. O projeto nao usa dados reais,
nao usa contratos reais, nao aprova contrato, nao reprova contrato e nao emite
parecer juridico final.

## O desafio

Tema oficial: IA para Resolucao de Problemas Criticos em Setores Regulados.

O desafio pede uma solucao de IA capaz de melhorar consistencia, precisao,
protecao de dados sensiveis, auditabilidade e apoio a decisao em contextos como
Juridico, Saude ou Financas.

Os cinco pilares considerados nesta implementacao sao:

- conformidade regulatoria;
- auditabilidade e explicabilidade;
- protecao de dados sensiveis;
- human-in-the-loop;
- robustez.

## A solucao

O RegulaGuard automatiza a triagem inicial e apoia a tomada de decisao, mas
preserva revisao humana nos pontos criticos. Ele executa um fluxo end-to-end:

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
- Sem frontend e sem banco de dados para manter a entrega reproduzivel e robusta.

## Conformidade regulatoria

O RegulaGuard faz triagem inicial controlada e nao substitui profissionais juridicos,
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
- Evitar que a solucao pareca chatbot em vez de um fluxo controlado end-to-end.

## Melhorias futuras e caminho de refatoração para produção

Para evoluir esta prova de conceito para um uso produtivo, seriam necessarios:

- matriz de risco configuravel por setor regulado, aprovada por juridico, compliance e DPO;
- biblioteca de clausulas ficticias para testes mais amplos, sem usar contratos proprietarios;
- revisao humana simulada com feedback estruturado;
- exportacao de trilha de auditoria para sistemas internos;
- conectores seguros e autorizados para fontes reais;
- armazenamento persistente dos logs de auditoria;
- politica de retencao e descarte;
- criptografia de dados sensiveis em repouso e em transito;
- monitoramento de taxa de fallback, baixa confianca e revisao humana;
- validacao formal dos prompts, criterios e guardrails por areas responsaveis.

## Como demonstrar o funcionamento

A entrada analisada esta em `data/sample_input.json`. Esse arquivo contem casos
simulados de solicitacoes regulatorias e minutas contratuais ficticias. O projeto
nao usa dados reais nem contratos reais.

Ao rodar:

```bash
docker compose up --build
```

o agente le esse JSON, executa a triagem em modo `dry-run` e gera o resultado em:

```text
runs/<timestamp>/
```

Os principais arquivos gerados sao:

- `decisions.json`: decisoes estruturadas do agente;
- `actions.json`: acoes simuladas em `dry-run`;
- `report.md`: relatorio legivel para revisao humana.

O avaliador pode abrir o `report.md` mais recente para ver a analise. Exemplos
incluidos na entrada simulada:

- `case-002`: minuta contratual simulada sem clausula de confidencialidade;
- `case-003`: minuta simulada sem retencao/descarte;
- `case-005`: caso critico com dado sensivel simulado;
- `case-006`: caso de baixa confianca encaminhado para revisao humana.

Limites da demonstracao:

- o agente nao aprova nem reprova contratos;
- o agente nao emite parecer juridico final;
- todas as acoes sao `dry-run`;
- Gemini e opcional;
- `mock` e o padrao para rodar first try.

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

O caminho principal e validado e Docker.

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

Esta execucao e opcional. Em Windows ou ambientes sem Python configurado, use o
caminho validado com Docker descrito acima.

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
GEMINI_MODEL=gemini-3.5-flash
OPENAI_API_KEY=
DRY_RUN=true
```

Providers opcionais:

```text
LLM_PROVIDER=gemini
GEMINI_API_KEY=sua_chave_local
GEMINI_MODEL=gemini-3.5-flash
```

Com `LLM_PROVIDER=gemini`, o agente faz uma chamada real opcional ao Gemini para
gerar as decisoes. Se `GEMINI_API_KEY` estiver vazia, se o modelo configurado em
`GEMINI_MODEL` nao estiver disponivel, ou se a chamada falhar por rede/API, o
fluxo usa `mock` automaticamente. Esse fallback e esperado e seguro. Nao coloque
chaves reais no repositorio.

As respostas do Gemini sao normalizadas defensivamente e validadas pelos schemas
Pydantic antes de qualquer acao em `dry-run`.

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
