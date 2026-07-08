---
title: "Lineage retroativo é dívida técnica. Documenta no momento da decisão ou perde."
slug: evidence-as-byproduct-auditoria-multi-agente
date: 2026-06-20
publishDate: 2026-06-20
draft: false
description: "O Audit Envelope Pattern que aprendi a custo caro: instrumentar depois sempre sai mais caro do que instrumentar antes."
tags: ["engenharia-de-dados"]
images:
  - cover.png
---
Fim do trimestre. Auditoria batendo na porta. 47 jobs no Airflow, 12 modelos dbt, aproximadamente 200 transformações encadeadas.

Pergunta simples: de onde vêm esses dados de transação?

Resposta esperada: consulta SQL num catálogo, resposta em segundos.

O que aconteceu de verdade: 4 engenheiros, 2 semanas, tentando reconstruir à mão o que deveria estar documentado. Entrevistando quem escreveu cada job. Lendo código de 18 meses atrás. Descobrindo que metade dos comentários estava errada ou desatualizada.

Eu estava nesse time. E aprendi a custo caro que lineage retroativo não existe. Só existe lineage instrumentado no momento da decisão.

## Por que "adicionar lineage depois" não funciona

O problema não é técnico. É cognitivo.

Quando você reconstrói lineage depois que o pipeline rodou, você não está documentando o que aconteceu. Está documentando o que acha que aconteceu, com base em código que pode ter mudado, comentários que podem estar errados, e memória de quem escreveu aquilo meses atrás.

Em produção real, jobs mudam. Parâmetros mudam. A fonte de "clientes" hoje pode não ser a mesma de 6 meses atrás. Sem instrumentação no momento da execução, você perde o "quando" e o "com quê exatamente".

Ferramentas como OpenLineage e Unity Catalog Lineage ajudam. Mas elas capturam estrutura, não contexto de decisão. Elas sabem que job A leu da tabela B. Não sabem por que esse job rodou nesse dia com esses parâmetros específicos.

## O Audit Envelope Pattern

O que uso hoje é um padrão simples que chamo de Audit Envelope. Cada job, cada execução de modelo dbt, cada chamada de LLM em pipeline, emite um header YAML antes de rodar:

```yaml
audit:
  job_id: ingestion_transacoes_pix
  run_id: "{{ run_id }}"
  timestamp_utc: "{{ ts }}"
  input_hash: "sha256:{{ hash_do_arquivo_fonte }}"
  output_hash: null  # preenchido no fim
  prompt_version: null  # só pra LLM jobs
  parent_invocation: "{{ dag_id }}/{{ task_id }}"
```

Esse envelope vai junto com o dado. Quando o dado chega em Silver ou Gold, o envelope chega junto. O catálogo indexa. A auditoria vira query SQL.

Resultado prático: quando a auditoria chegou de novo 6 meses depois, a resposta levou 45 minutos. 4 engenheiros não foram necessários. Uma query foi.

## Por que LGPD e governança de modelo vão forçar isso

LGPD Art. 20 dá ao titular o direito de pedir revisão de decisão tomada só com base em tratamento automatizado, e de receber informação clara sobre os critérios usados. "O modelo aprovou esse crédito" não é resposta suficiente. "O modelo versão 2.3, com features Y, rodou com esses parâmetros nesse momento, contra esse input exato" é.

A direção não é só brasileira. Em abril de 2026, Fed, FDIC e OCC substituíram a SR 11-7 por uma guidance de model risk mais baseada em princípios. IA generativa e agêntica ficaram formalmente fora do escopo dessa guidance, mas os princípios já vêm sendo aplicados a esses sistemas por analogia. A leitura que rodou no mercado resume bem o espírito: evidência tem que ser subproduto de como o modelo é construído, não reconstruída depois.

Lineage retroativo não satisfaz nenhum dos dois. Audit Envelope satisfaz como consequência natural da instrumentação.

A diferença entre compliance como dívida técnica e compliance como byproduct de boa engenharia é quando você instrumenta. Antes é gratuito. Depois é caro.

Hoje instrumento qualquer pipeline novo com Audit Envelope desde o primeiro job. O custo é uma função Python que emite o header e um campo a mais no schema de destino.

O custo de não fazer isso é 2 semanas de 4 engenheiros num fim de trimestre que todo mundo já está no limite.

Faço a conta uma vez e nunca mais preciso fazer.
