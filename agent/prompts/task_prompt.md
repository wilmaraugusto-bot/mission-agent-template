# RegulaGuard Task Prompt

Analise a entrada simulada e produza decisoes estruturadas para cada item.

Para cada item, identificar:

- tipo do item;
- dados pessoais detectados;
- dados sensiveis detectados;
- dados mascarados;
- risco regulatorio: baixo, medio, alto ou critico;
- pendencias documentais;
- clausulas simuladas ausentes;
- necessidade de revisao humana;
- justificativa;
- confianca;
- acoes recomendadas em dry-run.

Categorias obrigatorias de risco:

- LGPD;
- confidencialidade;
- retencao e descarte;
- finalidade de tratamento;
- matriz de responsabilidades.

Limites:

- Nao usar contratos reais.
- Nao emitir parecer juridico final.
- Nao aprovar ou reprovar contrato automaticamente.
- Nao executar acao real fora de dry-run.
