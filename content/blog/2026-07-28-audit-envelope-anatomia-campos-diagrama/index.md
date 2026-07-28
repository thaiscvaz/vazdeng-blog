---
title: "Audit Envelope, campo a campo: a anatomia do header que transforma auditoria em query"
slug: audit-envelope-anatomia-campos-diagrama
date: 2026-07-28
publishDate: 2026-07-28
draft: false
description: "Por que input_hash é SHA-256, por que output_hash só entra no fim, e o caminho do envelope até virar SQL no catálogo."
tags: ["engenharia-de-dados"]
images:
  - cover.png
---
Quando publiquei o post sobre lineage retroativo, um engenheiro de dados deixou um comentário que me fez parar: "cadê o diagrama geral dessa arquitetura?". Ele tinha razão. Eu mostrei o envelope e mostrei o resultado, mas não abri o motivo de cada campo existir. Este aqui fecha essa dívida.

A tese continua a mesma, agora dita sem rodeio: lineage não é um componente que você instala. É efeito colateral de o dado carregar o próprio contexto de decisão. O envelope é só o veículo desse contexto, e cada campo dele existe pra responder uma pergunta específica de auditoria.

O envelope que uso hoje:

```yaml
audit:
  job_id: ingestion_transacoes_pix
  run_id: "{{ run_id }}"
  timestamp_utc: "{{ ts }}"
  input_hash: "sha256:{{ hash_do_arquivo_fonte }}"
  output_hash: null  # preenchido no fim
  prompt_version: null  # só pra jobs com LLM
  parent_invocation: "{{ dag_id }}/{{ task_id }}"
```

![Anatomia do Audit Envelope campo a campo: job_id e run_id identificam a execução; input_hash SHA-256 amarra o conteúdo exato do input; output_hash nasce nulo e é selado no fim sobre o conteúdo sem o envelope; prompt_version só existe em jobs com LLM porque prompt muda sem deploy; parent_invocation liga cada execução à invocação que a disparou e transforma eventos soltos em grafo.](images/01-anatomia-envelope.png)

## input_hash: por que hash, e não caminho

O instinto é registrar o caminho do arquivo fonte. Caminho é ponteiro, e ponteiro aponta pra coisa que muda. O `clientes.parquet` de hoje não é o de seis meses atrás, e o caminho é o mesmo. O hash amarra o conteúdo exato: qualquer byte alterado produz um hash completamente diferente, e é computacionalmente inviável fabricar outro input com o mesmo hash. Quando a auditoria perguntar contra qual input a transformação rodou, a resposta não é "provavelmente este arquivo". É "exatamente este conteúdo, prova em anexo".

Git não te dá isso de graça. Git versiona o resultado, mas não amarra input e output da execução. O commit sabe o que mudou no código. Não sabe qual dado passou por ele naquela rodada.

## output_hash: por que nasce nulo

Dois motivos, um óbvio e um sutil. O óbvio: quando o job começa, o output não existe. O sutil: o hash do output é calculado sobre o conteúdo sem o envelope. Se o envelope entrasse no cálculo, o hash mudaria o arquivo que contém o próprio hash, que mudaria o hash de novo. Recursão sem saída. Então a ordem é rígida: gera o conteúdo, calcula o hash, preenche o campo, sela o arquivo. Depois disso, qualquer edição retroativa quebra a verificação. E é exatamente esse o objetivo: output reescrito depois pra ficar bonito deixa de bater com o hash registrado, e a trilha denuncia.

## prompt_version: por que só em jobs com LLM

Job determinístico tem um eixo de mudança: o código, e o git SHA resolve. Job que chama LLM tem dois eixos: o código e o prompt. Prompt muda sem deploy, às vezes sem pull request, editado direto num arquivo de configuração numa tarde qualquer. Se você não registra a versão do prompt no momento da execução, seis meses depois você sabe qual código rodou mas não sabe qual instrução o modelo recebeu. Metade da explicação evaporou. Em job sem LLM, o campo fica nulo e não custa nada.

## parent_invocation: de eventos soltos a grafo

Depois de "de onde vem esse dado", a pergunta de auditoria mais comum é "quem mandou rodar isso". Sem esse campo você tem uma pilha de eventos soltos, cada um correto e nenhum conectado. Com ele, cada execução aponta pra invocação que a disparou, e a pilha vira grafo navegável. É o campo que separa o envelope de um log glorificado.

## A jornada: do job à query

![Jornada do Audit Envelope pelo Medallion: o envelope nasce no job de ingestão, viaja anexado ao dado por Bronze, Silver e Gold, o catálogo indexa os campos como metadata consultável e a auditoria vira uma query SQL. No caso real do post anterior, a resposta que custava 4 engenheiros por 2 semanas caiu pra 45 minutos.](images/02-jornada-envelope.png)

O envelope nasce no job de ingestão, viaja junto com o dado por Bronze, Silver e Gold, e o catálogo indexa os campos como colunas de metadata. A auditoria deixa de ser reunião e vira SELECT. Fiz essa conta na prática no caso que contei no post anterior: a pergunta que custava 4 engenheiros por 2 semanas, em cima de 47 jobs e 12 modelos dbt, caiu pra uma query respondida em 45 minutos.

## A honestidade que devo ao nome

"Audit Envelope" é nome que eu dei pro padrão. Não procure por ele em spec de indústria, porque não vai achar. Os guarda-chuvas reais são data provenance e, se você já roda OpenLineage, custom facets: a spec permite anexar metadata própria com prefixo do seu projeto e um `_schemaURL` apontando pro schema, sem pedir permissão a ninguém. O envelope inteiro cabe num custom run facet.

O gancho brasileiro é direto. A LGPD, no Art. 20, dá ao titular o direito de pedir revisão de decisão tomada só por tratamento automatizado, e o parágrafo primeiro obriga o controlador a fornecer informações claras sobre os critérios e procedimentos usados. "O modelo aprovou" não responde isso. O envelope responde, campo a campo.

E quando não vale a pena: protótipo e projeto pessoal. Ali, git com commit descritivo cobre. O envelope começa a se pagar no dia em que alguém de fora pode te perguntar "por quê" com consequência. Nesse dia, ou a resposta já está escrita no dado, ou ela vai custar um trimestre.
