---
title: "Iceberg em producao: 3 anti-padroes que matam seu data lake em 3 meses"
slug: iceberg-3-antipatterns-producao
date: 2026-07-14
publishDate: 2026-07-14
draft: false
description: "---"
tags: ["engenharia-de-dados"]
images:
  - cover.png
---
---
title: "Iceberg em produção: 3 anti-padrões que matam seu data lake em 3 meses"
subtitle: "Particionamento ingênuo, manifesto que engorda e compaction esquecida. E como isso vira 100 mil GET requests numa query que devia custar centavos."
publish_date: 2026-07-14
track: DE
num: "015"
slug: iceberg-3-antipatterns-producao
tags:
  - iceberg
  - data-lake
  - performance
  - anti-patterns
---

Iceberg tem uma virtude que também é armadilha: ele funciona antes de você aprender a usar. Você cria a tabela, o job de ingestão sobe, o query rodou. Aparentemente está tudo bem. Três meses depois, sem que nada tenha "quebrado", uma query que devia levar 200 milissegundos passa a levar 45 segundos, e a fatura de object storage explodiu porque o mesmo dado agora custa 500 vezes mais para ler.

Eu já vi esse padrão em pipeline de finanças em produção. E vi de novo em contextos completamente diferentes, com times técnicos sólidos. Os anti-padrões são sempre os mesmos três. Nenhum deles é bug. Todos são decisões de arquitetura que pareciam razoáveis no dia 1.

![Os três anti-padrões de Iceberg em produção, cada um com sintoma e correção: particionar por hour(ts) gera 8.760 partições de poucos MB por ano e se corrige com baixa cardinalidade mais SORT ou Z-order; manifest bloat aparece quando se grava a cada 40s sem expirar snapshots e se corrige com expire_snapshots e rewrite_manifests agendados; compaction adiada acumula milhões de small files em streaming e se corrige com rewrite_data_files e remove_orphan_files noturno. Nenhum é bug, todos são manutenção adiada.](images/01-tres-antipadroes.png)

## O primeiro: particionar por campo que não tem estatística de acesso

O erro clássico é particionar por `hour(event_timestamp)`. Faz sentido no papel: dados temporais, granularidade fina, queries por período. Só que se sua tabela recebe 50MB por hora, no fim do ano você tem 8.760 partições cada uma com alguns megabytes. Segundo o [LakeOps](https://lakeops.dev/blog/iceberg-partitioning-best-practices), esse é o cenário de fragmentação garantida.

O tamanho alvo de arquivo Parquet para OLAP fica entre 128MB e 512MB. Abaixo disso o query planner gasta mais tempo abrindo metadata do que lendo dado. E o Iceberg abre metadata de todo arquivo potencialmente relevante para fazer partition pruning e column statistics, mesmo antes de decidir o que ler.

O caminho certo é particionar por baixa cardinalidade (data, região, talvez uma categoria de negócio), e usar `SORT BY` ou Z-order dentro da partição para acelerar seek por chave. Nunca particione por ID, timestamp granular ou qualquer campo com milhões de valores distintos.

## O segundo: manifest bloat e o vacuum tardio

Toda escrita em Iceberg gera um snapshot novo, e o snapshot referencia um manifesto que lista quais data files pertencem a ele. Se você grava a cada 40 segundos porque a stream é contínua, o manifesto cresce rápido. Ninguém rodou `expire_snapshots` porque ninguém sentiu dor ainda. Em algumas semanas o metadata sozinho consome gigabytes, e o planejamento de query lê tudo isso para descobrir o que precisa ler de verdade.

Segundo a [Starburst](https://www.starburst.io/blog/apache-iceberg-files/), 100 mil arquivos pequenos com metadata inflado transformam 200ms de planejamento em 45 segundos. E o custo em object storage vira 100 mil GET requests independentes. É o mesmo volume de dado. É o mesmo query. É 500 vezes mais caro. Não porque o Iceberg é ruim, mas porque você deixou a operação de manutenção pra depois.

![Comparação de custo da mesma query em dois estados da tabela. Fragmentada, sem manutenção: 100.000 arquivos pequenos com metadata inflado levam o planejamento da query a 45 segundos e geram 100.000 GET requests de object storage. Compactada com job noturno de rewrite_data_files e expire_snapshots, em arquivos de 128 a 512 MB: o mesmo planejamento cai para 200 milissegundos e poucos GET requests. Mesmo dado, mesma query, 500x mais caro.](images/02-mesma-query-500x.png)

Quando o time acorda e roda `expire_snapshots` de uma vez em 50 mil snapshots acumulados, o job de manutenção sozinho leva horas e reprocessa metadata de meses. Aí quebra a mesma noite em que era pra dormir tranquilo.

## O terceiro: compaction como coisa de fim de sprint

Compaction (`rewrite_data_files`) é a operação que consolida vários arquivos pequenos em poucos arquivos grandes. Não é opcional em ingestão streaming. E não pode andar sozinha: precisa vir acompanhada de `rewrite_manifests`, `expire_snapshots` e `remove_orphan_files`, senão você acumula lixo em outra dimensão. A [Dremio](https://www.dremio.com/blog/compaction-in-apache-iceberg-fine-tuning-your-iceberg-tables-data-files/) documenta esses quatro como um conjunto que roda junto, não escolha entre eles.

A regra que eu sigo: compaction é orçado como custo de infra, não como projeto do trimestre que vem. Um Spark job noturno consumindo alguns dólares de compute todo dia é infinitamente mais barato que refatorar particionamento com dado histórico já espalhado em milhões de arquivos. O custo é pequeno na frente e enorme atrás.

## Por que isso importa no Brasil

BACEN e LGPD adicionam camada dupla: exigem retenção auditável (mínimo 5 anos de rastro para instituições financeiras) e apagamento seletivo por finalidade. Iceberg entrega os dois nativamente via time travel e delete files, mas só se o metadata não estiver podre. Manifesto de 5 terabytes em cima de 50 de dado não é problema técnico apenas, é risco de auditoria: você não consegue provar rapidamente qual snapshot continha o dado do titular X no dia Y.

## O que eu mudaria se estivesse começando hoje

Três coisas simples, na ordem:

1. Particionar apenas por campo de baixa cardinalidade e usar `hidden partitioning` para não amarrar a query ao layout físico.
2. Agendar `rewrite_data_files` + `rewrite_manifests` + `expire_snapshots` + `remove_orphan_files` como job noturno desde o primeiro dia.
3. Alertar quando o número de data files por partição passar de N. Métrica barata, previne dor cara.

Data lake não quebra em um dia. Ele acumula silêncio até o dia que o custo passa do teto ou o SLA quebra na demonstração pro board. As três decisões acima custam pouco no começo e valem a fatura inteira.
