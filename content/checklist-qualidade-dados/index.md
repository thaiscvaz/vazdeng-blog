---
title: "Checklist de qualidade de dados antes de subir pipeline"
description: "As perguntas que eu faço antes de colocar qualquer pipeline em produção: contrato, idempotência, grão, partição, dado atrasado, observabilidade e LGPD."
type: default
---

Pipeline que cai é sorte: alguém percebe. O prejuízo vem do pipeline que não cai, roda verde e entrega número errado. Este checklist junta numa página as perguntas que eu faço antes de subir qualquer pipeline. Cada bloco aponta para o post onde a decisão está explicada com o caso real.

Use assim: se você não consegue responder um item em uma frase, ele ainda não está resolvido.

## 1. Contrato com quem produz o dado

- [ ] Existe um contrato versionado (não um DDL perdido num wiki) com schema, tipos e nulos de cada coluna?
- [ ] A semântica está escrita? O que `valor` significa: bruto ou líquido, com ou sem taxa, em qual moeda?
- [ ] Tem dono com nome: time e pessoa, não "a tabela"?
- [ ] Freshness e volume esperado estão declarados, com alarme fora da faixa?
- [ ] Mudança que quebra consumidor sobe a versão maior e avisa antes?

Por quê: [o produtor renomeou uma coluna e ninguém avisou]({{< relref "blog/2026-06-23-contrato-de-dados-schema-quebra-silencioso" >}}).

## 2. Idempotência

- [ ] Se eu rodar isso duas vezes seguidas, a tabela final continua igual?
- [ ] Consigo nomear a chave natural em uma frase?
- [ ] A carga é MERGE (upsert), não INSERT puro na tabela de destino?
- [ ] Um backfill de correção retroativa mantém os números certos?

Por quê: [rodar o pipeline duas vezes não pode mudar o resultado]({{< relref "blog/2026-06-27-idempotencia-reprocessar-sem-duplicar-zte-ep03" >}}).

## 3. O grão da tabela fato

- [ ] Alguém do time responde, em uma frase, o que significa uma linha da tabela fato?
- [ ] Todas as métricas da tabela estão no mesmo grão, sem somar coisas de níveis diferentes?

Por quê: [errar a linha custa mais caro que errar a coluna]({{< relref "blog/2026-08-15-zte-ep05-grao-do-fato-modelagem-dimensional" >}}).

## 4. Partição

- [ ] A tabela é grande o bastante para precisar de partição? Abaixo de 1 TB quase nunca precisa.
- [ ] A coluna de partição é a que as consultas de fato filtram?
- [ ] Não é coluna de alta cardinalidade (CPF, ID, timestamp ao segundo)?
- [ ] Cada partição fica perto de 1 GB ou mais, e o total fica bem abaixo de 10 mil partições?
- [ ] Quando a resposta é "depende", considerei clustering em vez de chutar uma coluna?

Por quê: [particionar errado custa mais caro que não particionar]({{< relref "blog/2026-07-04-particionar-errado-custa-mais-que-nao-particionar-zte-ep04" >}}).

## 5. Dado que chega atrasado

- [ ] O pipeline distingue o momento do evento do momento da chegada?
- [ ] Existe uma regra explícita de quanto tempo esperar por dado atrasado (watermark)?
- [ ] Está combinado o que acontece com o número de um período já fechado quando chega dado novo dele?

Por quê: [o dado que chega atrasado vai quebrar seu número]({{< relref "blog/2026-08-23-zte-ep06-late-arriving-data-watermark" >}}).

## 6. Observabilidade

- [ ] O log é estruturado (campos, não frases soltas)?
- [ ] Toda execução carrega um identificador de correlação que liga início, etapas e fim?
- [ ] Às 3h da manhã, consigo reconstruir o que aconteceu só pelo log, sem abrir o código?

Por quê: [dashboard bonito não te salva às 3h]({{< relref "blog/2026-09-05-zte-ep07-observability-log-estruturado" >}}).

## 7. SLA real do consumidor

- [ ] Sei o SLA que o consumidor de fato precisa, e não o que eu imagino?
- [ ] Fiz a conta de custo de batch e de streaming nesse volume antes de escolher?

Por quê: [SLA, não moda: quando batch, quando streaming, quando ambos]({{< relref "blog/2026-05-30-sla-nao-moda-batch-streaming" >}}).

## 8. LGPD desde a entrada

- [ ] Só entra no pipeline o dado pessoal que tem finalidade declarada?
- [ ] Dado pessoal é pseudonimizado na entrada, e não só no destino?
- [ ] Sei de onde cada dado pessoal veio e para onde foi (lineage)?
- [ ] A retenção é definida por finalidade, e não por tabela?

Por quê: [LGPD na ingestão de dados: 4 princípios que mudam sua arquitetura]({{< relref "blog/2026-04-16-lgpd-ingestao-de-dados" >}}).

---

Este checklist cresce junto com o blog. Toda semana sai um post novo, e a newsletter chega aos sábados. [Assinar no Substack](https://vazdeng.substack.com/subscribe?utm_source=blog&utm_medium=checklist&utm_campaign=fase1).
