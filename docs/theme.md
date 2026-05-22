# Tema oficial do Dia 2

## Tema oficial

- Nome do tema: IA para Resolução de Problemas Críticos em Setores Regulados

- Texto oficial do enunciado:
Crie uma solução de IA que apoie ou automatize processos relevantes em setores que lidam com muitas regras e informações sensíveis — como Saúde, Jurídico ou Finanças. O foco é usar IA para melhorar a consistência e precisão das análises, proteger dados sensíveis e ajudar na tomada de decisões importantes, sempre respeitando as leis e a ética.

- Restrições explícitas:
  - Considerar conformidade regulatória.
  - Considerar LGPD para dados pessoais e dados sensíveis.
  - Garantir auditabilidade e explicabilidade.
  - Proteger dados sensíveis com anonimização, mascaramento e minimização.
  - Usar human-in-the-loop em pontos críticos.
  - Tratar alucinação com guardrails, verificação de saída e comportamento previsível.
  - Manter o projeto executável via Docker.
  - Manter .env funcional sem segredos reais.
  - Garantir caso de teste explícito no README.

- Entregáveis obrigatórios:
  - README.md completo na raiz.
  - Dockerfile na raiz.
  - docker-compose.yml na raiz.
  - .env funcional na raiz, sem segredos reais.
  - .env.example na raiz.
  - Caso de teste explícito e executável no README.
  - Execução com docker compose up --build.
  - Relatório final gerado automaticamente.

## Recorte do dia

- Público-alvo:
Equipes jurídicas, administrativas, compliance, contratos e governança de dados que precisam triar solicitações ou documentos com dados sensíveis em setores regulados.

- Cenário de uso:
Triagem inicial de demandas regulatórias, solicitações administrativas e minutas contratuais simuladas de onboarding, contendo dados pessoais, riscos de LGPD, cláusulas ausentes, documentos incompletos e necessidade de revisão humana.

- Escopo incluído:
  - Leitura de solicitações simuladas em JSON.
  - Leitura de resumos de minutas contratuais simuladas de onboarding.
  - Detecção de dados pessoais e sensíveis.
  - Mascaramento/anonimização antes de qualquer decisão crítica.
  - Classificação de risco regulatório.
  - Identificação de pendências documentais.
  - Identificação de riscos contratuais simulados, como ausência de cláusula de confidencialidade, retenção/descarte, finalidade de tratamento de dados e matriz de responsabilidades.
  - Decisão de encaminhamento para revisão humana quando necessário.
  - Geração de relatório auditável em Markdown.

- Escopo fora:
  - Não tomar decisão jurídica final.
  - Não aprovar ou reprovar contrato.
  - Não emitir parecer jurídico definitivo.
  - Não substituir profissional jurídico, compliance ou DPO.
  - Não usar contratos reais de clientes.
  - Não processar dados reais de clientes, cidadãos, pacientes ou partes processuais.
  - Não executar ações reais em sistemas externos no modo padrão.
  - Não depender de chave externa de IA para rodar.

- Hipóteses assumidas:
  - Os dados de entrada são simulados.
  - Contratos e cláusulas usados no projeto são fictícios.
  - O modo padrão é dry-run.
  - O LLM_PROVIDER padrão é mock.
  - Gemini/OpenAI são opcionais e não obrigatórios.
  - Todo caso crítico deve ser encaminhado para revisão humana.

## Problema escolhido

- Problema:
Setores regulados recebem solicitações, documentos e minutas contratuais com dados pessoais, informações sensíveis, cláusulas incompletas e riscos de conformidade. A triagem manual pode ser lenta, inconsistente e sujeita a exposição indevida de dados.

- Por que isso importa:
Erros em setores regulados podem gerar risco jurídico, vazamento de dados, decisões inconsistentes, falhas de conformidade, ausência de rastreabilidade e exposição indevida de informações sensíveis.

- Como o agente reduz esforço, risco ou tempo:
O agente automatiza a triagem inicial, mascara dados sensíveis, identifica pendências, classifica risco, aponta cláusulas ou requisitos ausentes, recomenda ações seguras e gera relatório auditável.

- Limites da autonomia do agente:
O agente não toma decisão final em casos críticos, não aprova contratos e não emite parecer jurídico definitivo. Ele encaminha casos de alto risco para revisão humana e registra a justificativa.

## Entrada de dados do agente

- Campos obrigatórios:
  - id
  - title
  - description
  - sector
  - requester_type
  - submitted_documents

- Campos opcionais:
  - document_type
  - personal_data
  - sensitive_data
  - urgency
  - previous_case_id
  - declared_purpose
  - contract_clauses
  - missing_clauses

- Exemplo de uma tarefa:
Uma minuta contratual simulada de onboarding menciona tratamento de dados pessoais de cidadãos e servidores, mas não apresenta cláusula clara de confidencialidade, retenção, descarte e matriz de responsabilidades. O agente deve mascarar dados, classificar risco, apontar pendências e encaminhar para revisão jurídica/compliance.

- Fonte dos dados:
Arquivo local data/sample_input.json com dados simulados.

- Dados sensíveis que não devem ser usados:
Dados reais de clientes, cidadãos, pacientes, servidores, partes processuais, contratos reais, valores comerciais reais, cláusulas proprietárias ou documentos sigilosos.

## Decisões que o agente deve tomar

- Decisões por tarefa:
  - identificar tipo de solicitação ou documento;
  - detectar dados pessoais e sensíveis;
  - mascarar dados antes da análise crítica;
  - decidir o nível de risco regulatório;
  - verificar se faltam documentos;
  - verificar se faltam cláusulas contratuais simuladas relevantes;
  - decidir se exige revisão humana;
  - definir ações seguras em dry-run.

- Critérios usados para decidir:
  - presença de dados pessoais;
  - presença de dados sensíveis;
  - ausência de cláusulas de LGPD;
  - ausência de cláusula de confidencialidade;
  - ausência de retenção e descarte;
  - ausência de matriz de responsabilidades;
  - completude documental;
  - urgência;
  - risco de exposição;
  - impacto da decisão;
  - confiança da classificação.

- Nível de confiança esperado:
  - Casos de baixa confiança devem ser encaminhados para revisão humana.
  - Casos com dados sensíveis devem ter ação conservadora.
  - Casos contratuais com cláusulas críticas ausentes devem exigir revisão jurídica/compliance.

- Quando o agente deve recusar ou pedir revisão humana:
  - dados sensíveis em excesso;
  - documentos insuficientes;
  - baixa confiança;
  - risco regulatório alto;
  - ausência de cláusulas críticas;
  - possível decisão crítica que afete direitos, obrigações ou conformidade.

## Ações que o agente deve executar

- Ações permitidas em dry-run:
  - mascarar dados sensíveis;
  - classificar risco;
  - registrar decisão;
  - solicitar complemento documental;
  - apontar cláusulas simuladas ausentes;
  - marcar revisão humana;
  - gerar checklist de conformidade;
  - gerar relatório auditável.

- Ações bloqueadas:
  - aprovar decisão final;
  - reprovar contrato;
  - emitir parecer jurídico definitivo;
  - negar direito ou solicitação;
  - enviar dados sensíveis para API externa obrigatória;
  - executar ação real fora do dry-run;
  - remover logs de auditoria.

- Ferramentas ou sistemas simulados:
  - fila de revisão humana;
  - sistema de protocolo;
  - registro de auditoria;
  - checklist de conformidade;
  - relatório de risco contratual/regulatório.

- Evidências que cada ação deve gerar:
  - item analisado;
  - decisão tomada;
  - justificativa;
  - risco identificado;
  - dados mascarados;
  - cláusulas ou documentos ausentes;
  - ação recomendada;
  - necessidade ou não de revisão humana.

## Relatório esperado

- Resumo do objetivo:
Demonstrar que o agente executou triagem regulatória segura com proteção de dados, análise de risco contratual simulado e auditabilidade.

- Decisões tomadas:
Classificação de risco, identificação de dados sensíveis, pendências documentais, cláusulas ausentes e necessidade de revisão humana.

- Ações planejadas:
Mascaramento, solicitação de documentos, apontamento de cláusulas ausentes, encaminhamento para revisão e registro de auditoria.

- Resultado da política de segurança:
Casos críticos, incertos ou com cláusulas essenciais ausentes devem ser bloqueados para decisão automática e enviados para revisão humana.

- Alertas, riscos e próximos passos:
Listar limitações, casos de baixa confiança, recomendações para produção e pontos que exigem validação jurídica/compliance.

## Critérios de aceite específicos do tema

- O agente processa a entrada do tema sem erro.
- As decisões são relevantes para setores regulados.
- O agente identifica e mascara dados sensíveis simulados.
- O agente identifica pendências documentais e contratuais simuladas.
- O agente encaminha casos críticos para revisão humana.
- As ações respeitam o modo dry-run.
- O relatório explica decisões, justificativas, riscos, dados mascarados e limites.
- Não há dependência obrigatória de internet ou chave externa.
- O projeto roda com docker compose up --build.

## Riscos de desclassificação relacionados ao tema

- Prometer decisão jurídica, médica ou financeira final.
- Aprovar ou reprovar contrato automaticamente.
- Usar contratos reais ou cláusulas proprietárias.
- Enviar dados sensíveis reais para LLM.
- Não mascarar dados pessoais/sensíveis.
- Não gerar justificativa auditável.
- Não prever human-in-the-loop.
- Depender obrigatoriamente de Gemini/OpenAI.
- Quebrar docker compose up --build.
- README sem caso de teste explícito.