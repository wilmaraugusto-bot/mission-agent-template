# Plano de Adaptacao - RegulaGuard Agent

Este plano orienta a implementacao do projeto para o tema oficial do Dia 2:
**IA para Resolucao de Problemas Criticos em Setores Regulados**.

O objetivo e transformar a base atual no **RegulaGuard Agent**, mantendo o modo
padrao `mock`, execucao via Docker e ausencia de dados ou contratos reais.

## 1. Nome da solucao

**RegulaGuard Agent - Agente Autonomo de Triagem Regulatoria, LGPD e Riscos Contratuais Simulados**

O agente apoia equipes juridicas, administrativas, compliance, contratos e
governanca de dados em uma triagem inicial segura de demandas reguladas e
minutas contratuais simuladas de onboarding.

## 2. Problema escolhido

Setores regulados lidam com solicitacoes, documentos e minutas que podem conter
dados pessoais, dados sensiveis, clausulas incompletas e riscos de conformidade.
A triagem manual inicial pode ser lenta, inconsistente e vulneravel a falhas de
rastreabilidade.

O RegulaGuard resolve apenas a etapa de triagem inicial:

- identifica riscos simulados;
- mascara dados sensiveis;
- aponta pendencias;
- classifica risco;
- recomenda proximas acoes em `dry-run`;
- encaminha casos criticos para revisao humana.

Ele nao emite parecer juridico final, nao aprova contrato e nao reprova contrato.

## 3. Por que a solucao atende ao tema oficial

A solucao atende ao tema porque apoia processos criticos em setores regulados,
com foco em consistencia, protecao de dados, explicabilidade e apoio a decisao.

Alinhamento direto com o tema:

- setor regulado: juridico, compliance, contratos e governanca de dados;
- dados sensiveis: tratados apenas como dados simulados e mascarados;
- IA aplicada: triagem, classificacao, explicacao e recomendacao segura;
- auditabilidade: decisoes e acoes registradas em artefatos e relatorio;
- human-in-the-loop: casos criticos sempre exigem revisao humana;
- etica e conformidade: sem contratos reais, sem parecer final e sem automacao decisoria critica.

## 4. Como o agente coleta dados

O agente deve coletar dados apenas de arquivos locais simulados.

Fonte principal:

- `data/sample_input.json`

Tipos de dados simulados:

- identificador da demanda;
- titulo e descricao;
- setor regulado;
- tipo de solicitante;
- documentos enviados;
- tipo de documento;
- finalidade declarada;
- sinais de dados pessoais;
- sinais de dados sensiveis;
- resumo de minuta contratual simulada;
- clausulas presentes;
- clausulas ausentes;
- urgencia;
- contexto operacional.

Nao usar:

- contrato real;
- dado pessoal real;
- dado sensivel real;
- documento sigiloso;
- clausula proprietaria de terceiro;
- base externa obrigatoria.

## 5. Como o agente protege dados sensiveis

O agente deve tratar toda entrada como potencialmente sensivel, mesmo sendo
simulada.

Protecoes esperadas:

- minimizacao: analisar somente os campos necessarios;
- mascaramento: substituir nomes, emails, documentos e identificadores por marcadores;
- anonimização simulada: exibir exemplos como `[NOME_MASCARADO]`, `[EMAIL_MASCARADO]`, `[ID_MASCARADO]`;
- nao registrar segredo ou chave de API em logs;
- nao enviar dados sensiveis reais para LLM externa;
- manter `LLM_PROVIDER=mock` como padrao;
- permitir Gemini/OpenAI apenas como opcionais via `.env`, nunca obrigatorios.

O relatorio deve mostrar que dados foram protegidos, mas sem reproduzir dados
sensiveis completos.

## 6. Como o agente analisa minutas contratuais simuladas

A analise deve ser feita sobre resumos e clausulas ficticias, nunca contratos
reais.

O agente deve verificar:

- se a minuta simulada informa finalidade de tratamento de dados;
- se existe clausula de confidencialidade;
- se existe regra de retencao;
- se existe regra de descarte;
- se existe matriz de responsabilidades;
- se ha menção a operadores, controladores ou terceiros;
- se ha lacunas documentais;
- se o risco exige revisao humana.

A saida deve ser uma triagem de risco e pendencias, nao um parecer juridico.

## 7. Como o agente identifica riscos

O agente deve identificar riscos simulados nas seguintes categorias.

### LGPD

- presenca de dados pessoais;
- presenca de dados sensiveis;
- finalidade de tratamento ausente ou vaga;
- base de tratamento nao informada;
- compartilhamento com terceiros sem detalhe;
- falta de minimizacao.

### Confidencialidade

- clausula ausente;
- escopo de confidencialidade vago;
- ausencia de deveres de protecao;
- ausencia de regra para incidentes ou exposicao indevida.

### Retencao e descarte

- prazo de retencao ausente;
- criterio de descarte ausente;
- descarte dependente de acao manual sem responsavel;
- armazenamento indefinido sem justificativa.

### Finalidade de tratamento

- finalidade generica;
- finalidade incompatível com dados coletados;
- coleta excessiva para a finalidade declarada;
- ausencia de justificativa para dados sensiveis.

### Matriz de responsabilidades

- responsavel interno nao definido;
- papel de controlador ou operador indefinido;
- ausencia de aprovador humano;
- ausencia de area responsavel por mitigacao.

## 8. Como o agente toma decisoes

O agente deve tomar decisoes intermediarias, sempre explicaveis.

Decisoes esperadas:

- classificar a demanda por tipo;
- detectar se ha dados pessoais ou sensiveis simulados;
- definir nivel de risco: baixo, medio ou alto;
- apontar clausulas ou documentos ausentes;
- decidir se exige revisao humana;
- definir acoes seguras em `dry-run`;
- registrar justificativa e nivel de confianca.

Regras de decisao:

- risco alto sempre exige human-in-the-loop;
- baixa confianca sempre exige revisao humana;
- ausencia de clausulas criticas exige revisao juridica/compliance;
- dados sensiveis exigem postura conservadora;
- nenhuma decisao deve aprovar ou reprovar contrato automaticamente.

## 9. Como o agente executa acoes em dry-run

As acoes devem ser simuladas e registradas, sem efeito externo real.

Acoes permitidas:

- criar registro de triagem simulado;
- marcar dados como mascarados;
- gerar checklist de conformidade;
- apontar pendencias documentais;
- apontar clausulas simuladas ausentes;
- classificar risco;
- encaminhar para fila simulada de revisao humana;
- gerar relatorio auditavel.

Acoes proibidas:

- aprovar contrato;
- reprovar contrato;
- emitir parecer juridico final;
- enviar dados reais para sistemas externos;
- alterar contratos reais;
- remover logs;
- executar qualquer acao fora do `dry-run`.

## 10. Como o agente garante human-in-the-loop

O agente deve tratar revisao humana como parte obrigatoria do fluxo em casos
criticos.

Enviar para revisao humana quando:

- risco for alto;
- confianca for baixa;
- houver dados sensiveis;
- faltar finalidade de tratamento;
- faltar confidencialidade;
- faltar retencao ou descarte;
- faltar matriz de responsabilidades;
- houver conflito ou ambiguidade;
- a acao impactar direitos, obrigacoes ou conformidade.

O relatorio deve indicar:

- motivo da revisao;
- area sugerida: juridico, compliance, DPO, contratos ou governanca;
- itens que o humano deve verificar;
- limites do agente.

## 11. Como o relatorio sera auditavel

O relatorio deve permitir entender o que aconteceu sem depender de conversa.

Deve conter:

- identificador da execucao;
- resumo do objetivo;
- entrada analisada;
- sinais de dados pessoais e sensiveis;
- dados mascarados ou categorias mascaradas;
- riscos identificados;
- decisoes tomadas;
- justificativas;
- confianca;
- acoes em `dry-run`;
- status da politica de seguranca;
- necessidade de revisao humana;
- limites: sem contrato real, sem parecer final, sem aprovacao ou reprovacao automatica.

Os arquivos em `runs/<timestamp>/` devem permitir auditoria:

- `decisions.json`;
- `actions.json`;
- `report.md`.

## 12. Quais arquivos devem ser alterados na implementacao

Alterar somente quando necessario para implementar o RegulaGuard.

- `docs/theme.md`: manter tema, recorte e limites atualizados.
- `data/sample_input.json`: criar entrada simulada de onboarding regulatorio.
- `agent/llm/mock_provider.py`: gerar decisoes mockadas alinhadas a LGPD e riscos contratuais simulados.
- `agent/tools/mock_actions.py`: gerar acoes em `dry-run` de triagem, mascaramento, checklist e revisao humana.
- `agent/core/report.py`: melhorar relatorio auditavel para o tema.
- `agent/models/schemas.py`: alterar somente se os modelos atuais forem insuficientes.
- `README.md`: atualizar explicacao, caso de teste e artefatos quando a implementacao for feita.
- `tests/`: adicionar ou ajustar testes sem remover os existentes.

Observacao: este plano nao altera esses arquivos agora. Ele apenas define o que
devera ser considerado na etapa de implementacao.

## 13. Quais arquivos nao devem ser alterados

Nao alterar sem necessidade forte:

- `Dockerfile`;
- `docker-compose.yml`;
- `.env`;
- `.env.example`;
- `scripts/acceptance_check.py`;
- testes existentes apenas para ocultar falhas;
- providers opcionais de LLM se o modo `mock` ja atender a entrega;
- arquivos em `runs/` que sejam apenas historico de execucao.

Obrigatorio manter:

- `.env` funcional sem segredos reais;
- `LLM_PROVIDER=mock` como padrao;
- `docker compose up --build` como caminho principal de teste;
- README com caso de teste explicito.

## 14. Riscos de desclassificacao

- Usar contrato real.
- Usar dados pessoais ou sensiveis reais.
- Emitir parecer juridico final.
- Aprovar contrato automaticamente.
- Reprovar contrato automaticamente.
- Depender obrigatoriamente de Gemini/OpenAI.
- Remover `LLM_PROVIDER=mock` como padrao.
- Quebrar `docker compose up --build`.
- Versionar chave real em `.env`, README, docs, testes ou logs.
- Remover `scripts/acceptance_check.py`.
- Remover testes existentes para esconder falhas.
- Entregar uma solucao que pareca chatbot, sem fluxo end-to-end.
- Nao gerar relatorio auditavel.
- Fugir do tema oficial de setores regulados.
- Usar propriedade intelectual indevida de terceiros.

## 15. Checklist de validacao

Antes de considerar a implementacao pronta, validar:

- `LLM_PROVIDER=mock` continua padrao.
- `.env` funciona sem chave real.
- Gemini/OpenAI continuam opcionais via `.env`.
- `data/sample_input.json` usa apenas dados e minutas simuladas.
- O agente coleta dados.
- O agente analisa contexto regulatorio.
- O agente identifica riscos de LGPD.
- O agente identifica confidencialidade, retencao/descarte, finalidade e matriz de responsabilidades.
- O agente toma decisoes explicaveis.
- O agente executa apenas acoes em `dry-run`.
- O agente encaminha casos criticos para revisao humana.
- O relatorio e auditavel.
- O README contem caso de teste explicito.
- `docker compose up --build` passa.
- `docker compose run --rm agent python -m pytest` passa.
- `docker compose run --rm agent python scripts/acceptance_check.py` passa.
- Nenhuma chave real aparece em `git diff`.

## 16. Roteiro para finalizar ate 18:00

### 00:01 - 01:00

- Confirmar tema oficial em `docs/theme.md`.
- Validar que RegulaGuard continua alinhado ao tema.
- Fechar o escopo: triagem regulatoria e minutas simuladas de onboarding.

### 01:00 - 03:00

- Adaptar `data/sample_input.json` com casos simulados.
- Definir categorias de risco e criterios de decisao.
- Confirmar que nenhum contrato real sera usado.

### 03:00 - 07:00

- Adaptar mock decisions e mock actions.
- Garantir mascaramento e revisao humana.
- Manter todas as acoes em `dry-run`.

### 07:00 - 10:00

- Melhorar relatorio auditavel.
- Atualizar README com caso de teste e descricao da solucao.
- Adicionar testes necessarios sem remover testes existentes.

### 10:00 - 13:00

- Rodar testes no Docker.
- Corrigir falhas.
- Verificar que o modo `mock` funciona sem internet e sem chave.

### 13:00 - 15:00

- Rodar `docker compose up --build`.
- Abrir o relatorio mais recente.
- Conferir se a entrega mostra coleta, analise, decisao, acao e relatorio.

### 15:00 - 16:30

- Rodar pytest e acceptance check.
- Revisar `git diff`.
- Procurar chaves reais, dados reais e uso indevido de conteudo de terceiros.

### 16:30 - 18:00

- Congelar escopo.
- Fazer apenas correcoes criticas.
- Preparar submissao final.
- Conferir checklist de validacao.
