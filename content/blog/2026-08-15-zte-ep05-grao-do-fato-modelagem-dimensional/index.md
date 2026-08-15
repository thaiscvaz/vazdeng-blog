---
title: "Zero to Expert Ep 05: O grão do fato. Errar a linha custa mais caro que errar a coluna"
slug: zte-ep05-grao-do-fato-modelagem-dimensional
date: 2026-08-15
publishDate: 2026-08-15
draft: false
description: "O que significa UMA linha da sua tabela fato? Se ninguém responde em uma frase, o modelo está em areia movediça."
tags: ["zero-to-expert", "engenharia-de-dados"]
images:
  - cover.png
---
A pergunta que eu mais gosto de fazer numa revisão de modelo de dados tem sete palavras: o que significa uma linha dessa tabela? Quando a resposta sai em uma frase, o modelo costuma estar são. Quando vem um "depende" ou um silêncio, achei o problema antes de abrir uma query. Essa resposta tem nome: é o grão da tabela fato, e é a decisão de modelagem que menos recebe atenção e mais cobra depois.

Grão é a declaração explícita do que uma linha representa. Ralph Kimball colocou essa declaração como o passo 2 do processo de design dimensional de 4 passos: primeiro o processo de negócio, depois o grão, e só então as dimensões e as métricas. E ele escreveu sem rodeio que o erro de design mais frequente é não declarar o grão no começo: sem isso, o design inteiro repousa em areia movediça. Repare na ordem. O grão vem antes de qualquer coluna. Errar coluna se conserta; errar o grão condena a tabela.

## A mesma nota, dois grãos

O exemplo que eu uso pra explicar é a nota fiscal eletrônica, porque toda empresa brasileira tem uma. A NF-e tem duas partes: o cabeçalho (total da nota, imposto, status de pagamento) e os itens (produto, quantidade, preço unitário). Cada parte é um grão possível da tabela fato. Uma linha por nota, ou uma linha por item da nota.

A aritmética é o argumento. Num cenário ilustrativo de 10 milhões de notas por mês com média de 8 itens por nota, a fato no grão do item tem 80 milhões de linhas por mês; no grão do cabeçalho, 10 milhões. Se o KPI da diretoria é receita total e status de pagamento, servir esse painel direto da fato de item escaneia 8x mais linhas do que o necessário, todo dia, em toda query. Volume é consequência do grão, não do dado.

![A mesma nota fiscal eletrônica modelada em dois grãos: à esquerda, o grão do cabeçalho, uma linha por nota, 10 milhões de linhas por mês, responde receita total, imposto e status; à direita, o grão do item, uma linha por item, 80 milhões de linhas por mês, responde margem por produto e categoria. A barra âmbar pede a declaração em uma frase: uma linha é igual a o quê?](images/01-mesma-nota-dois-graos.png)

## Por que errar a linha custa mais que errar a coluna

Coluna errada é um problema barato. O Delta Lake (e qualquer formato de tabela moderno) faz schema evolution: coluna nova entra sem reescrever o histórico. Grão errado é outra categoria de problema: não existe "evolução de grão". Mudar o que a linha significa é reescrever a tabela inteira e, pior, todo o downstream que aprendeu a somar aquela tabela: jobs, dashboards, contratos de dados. Na base de conhecimento da minha squad, tabela de consumo sem contrato documentado é anti-padrão exatamente por isso: consumidor quebra quando o significado muda. E o grão é a cláusula mais importante desse contrato.

O bug clássico do grão mal declarado é silencioso. Alguém guarda o frete, que é atributo do cabeçalho, repetido nas 8 linhas de item da nota. Meses depois um dashboard soma a coluna de frete e o número infla 8x. O valor é plausível, ninguém desconfia, e a decisão errada sobe pra diretoria com aparência de precisão. O erro inverso também existe e é mais cruel: agregar cedo demais. Se você só guardou o grão do cabeçalho e no trimestre seguinte o negócio pede margem por categoria de produto, o dado não existe. Não dá pra desagregar o que você nunca armazenou.

## A regra que resolve a tensão

Os dois erros têm a mesma cura, e ela mora na arquitetura em camadas: a camada curada (Silver) guarda o grão mais atômico que a fonte emite, o item; a camada de consumo (Gold) materializa o agregado no grão que o consumo pede, o cabeçalho pro KPI da diretoria. Os dois grãos declarados por escrito, cada um no contrato da sua tabela. O detalhe preserva o futuro; o agregado serve o presente sem escanear 8x mais linha do que precisa.

![A regra em fluxo: a fonte emite item; a camada Silver guarda o grão atômico do item, preservando perguntas futuras; a camada Gold materializa o agregado no grão do cabeçalho pro KPI. Ao lado, o alerta do anti-padrão: frete do cabeçalho repetido nas linhas de item e somado infla o número em 8x. A barra âmbar resume: Silver no grão mais atômico, Gold no grão do consumo, os dois declarados.](images/02-regra-silver-gold.png)

Três situações em que eu não desagregaria: quando a fonte só emite o cabeçalho (fabricar grão de item que a origem não tem é inventar dado); quando volume vezes retenção não paga o detalhe e o negócio assinou embaixo do agregado; e quando a "solução" vira proliferação, porque outro anti-padrão da minha base é criar 50 versões near-duplicadas do mesmo agregado, uma pra cada pedido de painel.

No Ep 04 desta série eu falei de particionamento, a decisão física do layout. O grão vem antes: é a decisão lógica que define o que a tabela É. A régua final cabe numa frase escrita no contrato: "uma linha desta tabela é um item de nota fiscal". Se a frase não sai, você não tem um modelo. Tem areia movediça com nome de tabela.
