# Roteiro Operacional do Dia 22/05/2026

Use este arquivo quando o tema oficial da Missao IA + Open Challenge Dev sair.
O objetivo e adaptar o projeto com segurança, sem quebrar Docker, testes ou o
modo padrao `mock`.

## 1. O que fazer às 00:01 quando o tema aparecer

- Copie o texto oficial do tema exatamente como foi publicado.
- Salve o link, print ou referencia da fonte oficial.
- Leia o tema uma vez sem editar nada.
- Identifique palavras-chave: publico, problema, restricoes, formato esperado e criterios.
- Nao comece alterando codigo. Primeiro organize o entendimento do tema.
- Abra `docs/theme.md` e prepare o preenchimento.

## 2. O que copiar para docs/theme.md

Cole em `docs/theme.md`:

- texto oficial completo do tema;
- regras especificas citadas no enunciado;
- restricoes do desafio;
- entregaveis obrigatorios;
- ideias iniciais de recorte;
- problema escolhido;
- entradas que o agente deve receber;
- decisoes que o agente deve tomar;
- acoes que o agente deve executar;
- relatorio esperado.

Nao cole:

- chaves de API;
- dados pessoais;
- dados privados;
- conteudo protegido de terceiros sem permissao;
- informacoes que nao possam aparecer na entrega.

## 3. Como pedir uma análise do tema no ChatGPT

Use um prompt simples:

```text
Analise este tema oficial do desafio. Explique em linguagem simples:
1. qual e o problema central;
2. quais solucoes de agente autonomo fazem sentido;
3. quais riscos de fugir do tema;
4. quais entradas, decisoes, acoes e relatorio o agente deveria ter.

Tema oficial:
[cole aqui o tema]
```

Depois peça um recorte:

```text
Sugira 3 recortes viaveis para implementar em poucas horas. Cada recorte deve funcionar como agente autonomo end-to-end, nao chatbot, e precisa rodar com mock sem API paga.
```

Escolha o recorte mais simples que ainda pareça relevante e alinhado ao tema.

## 4. Quais arquivos poderão ser adaptados

Adapte somente o necessario.

- `docs/theme.md`: registrar tema, recorte, problema e criterio especifico.
- `data/sample_input.json`: mudar a entrada de exemplo para o tema oficial.
- `agent/prompts/system_prompt.md`: ajustar instrucoes gerais do agente, se o arquivo existir.
- `agent/prompts/task_prompt.md`: ajustar prompt de tarefa, se o arquivo existir.
- `agent/models/decision.py`: alterar somente se o tema exigir novos campos.
- `agent/core/runner.py` ou `planner/executor`: alterar somente se o fluxo atual nao atender o tema.
- `README.md`: explicar o tema, como rodar, caso de teste e resultado esperado.

Antes de alterar algo mais complexo, peça ao Codex:

```text
Leia docs/theme.md e diga quais arquivos realmente precisam mudar para adaptar o projeto ao tema. Nao altere nada ainda.
```

## 5. O que não mexer sem necessidade

Nao mexa sem uma razao forte:

- `Dockerfile`;
- `docker-compose.yml`;
- `.env`;
- `.env.example`;
- `scripts/acceptance_check.py`;
- testes ja existentes.

Se algum teste falhar, corrija o comportamento ou atualize o teste com cuidado.
Nao remova testes existentes apenas para passar mais rapido.

## 6. Comandos obrigatórios de validação

Rode estes comandos antes da entrega:

```bash
docker compose up --build
```

```bash
docker compose run --rm agent python -m pytest
```

```bash
docker compose run --rm agent python scripts/acceptance_check.py
```

Resultado esperado:

- o Docker sobe na primeira tentativa;
- os testes passam;
- o acceptance check passa;
- uma pasta nova aparece em `runs/<timestamp>/`;
- o relatorio fala do tema oficial.

## 7. Checklist para saber se a solução é agente autônomo

A solucao precisa mostrar que o agente:

- coleta dados;
- analisa contexto;
- toma decisao;
- executa acoes;
- gera relatorio.

Se a solucao apenas responde perguntas em conversa, ela parece chatbot. Ajuste o
fluxo para mostrar entrada, decisao, acao planejada e artefatos finais.

## 8. Riscos de desclassificação

- `docker compose up --build` nao funcionar.
- README sem caso de teste claro.
- `.env` ausente ou com chave real.
- Projeto depender de API paga no modo basico.
- `LLM_PROVIDER=mock` deixar de ser o padrao.
- Solucao parecer chatbot em vez de agente autonomo.
- Tema oficial mal representado ou ignorado.
- Entrega fora do prazo.
- Uso indevido de propriedade intelectual de terceiros.
- Vazamento de chave, token ou segredo em arquivo, log ou print.

## 9. Plano de horários para finalizar até 18:00

### 00:01 - 00:30

- Copiar tema oficial.
- Preencher `docs/theme.md`.
- Pedir analise do tema no ChatGPT.
- Escolher um recorte simples.

### 00:30 - 02:00

- Ajustar `data/sample_input.json`.
- Definir entradas, decisoes, acoes e relatorio esperado.
- Pedir ao Codex um plano de arquivos a alterar.

### 02:00 - 06:00

- Adaptar prompts, mock, planner ou runner somente se necessario.
- Manter `mock` como padrao.
- Rodar testes pequenos durante as alteracoes.

### 06:00 - 10:00

- Atualizar README.
- Gerar uma execucao real com Docker.
- Abrir o relatorio em `runs/<timestamp>/report.md`.
- Confirmar que o relatorio esta alinhado ao tema.

### 10:00 - 14:00

- Corrigir falhas.
- Melhorar clareza do relatorio e do README.
- Revisar riscos de desclassificacao.

### 14:00 - 16:00

- Rodar os tres comandos obrigatorios.
- Revisar `git diff`.
- Procurar chaves reais e informacoes sensiveis.

### 16:00 - 18:00

- Congelar escopo.
- Fazer apenas correcoes criticas.
- Preparar submissao final.
- Conferir checklist final.

## 10. Checklist final de submissão

- Tema oficial esta em `docs/theme.md`.
- Recorte escolhido esta claro.
- `data/sample_input.json` representa o tema.
- A solucao coleta dados, analisa contexto, toma decisao, executa acoes e gera relatorio.
- `README.md` explica como rodar.
- `README.md` contem caso de teste explicito.
- `LLM_PROVIDER=mock` continua padrao.
- O modo basico nao exige API paga.
- Gemini/OpenAI, se usados, sao opcionais via `.env`.
- Nenhuma chave real foi versionada.
- `Dockerfile` e `docker-compose.yml` nao foram alterados sem necessidade.
- `scripts/acceptance_check.py` continua no projeto.
- Testes existentes nao foram removidos.
- `docker compose up --build` passou.
- `docker compose run --rm agent python -m pytest` passou.
- `docker compose run --rm agent python scripts/acceptance_check.py` passou.
- Relatorio final foi gerado em `runs/<timestamp>/report.md`.
- A entrega esta dentro do tema oficial.
- A submissao foi feita antes das 18:00.
