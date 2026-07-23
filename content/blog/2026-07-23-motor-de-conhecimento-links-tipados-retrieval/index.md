---
title: "Por que seu RAG mente com confiança (e as 3 peças que consertam)"
slug: motor-de-conhecimento-links-tipados-retrieval
date: 2026-07-23
publishDate: 2026-07-23
draft: false
description: "Terça eu mostrei por que minerar vale mais que acumular. Aqui está a britadeira por dentro: 111 conexões tipadas, fusão de rankings e um nó de avaliação que..."
tags: ["segundo-cerebro", "ia"]
series: ["segundo-cerebro"]
episode: 2
images:
  - cover.png
---
Na terça eu contei que a IA virou a britadeira do meu segundo cérebro. Hoje eu abro a britadeira.

A maioria das pessoas pluga um banco vetorial em cima das notas, chama de RAG e acha que resolveu. O sistema então responde com toda a confiança do mundo sobre a nota errada. O motor que eu construí tem três peças que quase todo tutorial pula, e é o conjunto delas que faz a mineração funcionar em vez de alucinar.

![O fluxo do motor: fonte bruta, link tipado, RRF que funde buscas, e o nó grade que evita resposta confiante sobre lixo.](images/00-motor-fluxo.png)

## 1. Link tipado, não wikilink solto

Um wikilink diz que duas notas se tocam. Ele não diz como.

O meu analyzer não propõe só "conecta A e B". Ele propõe conexões **tipadas e ponderadas**: `builds_on`, `cites`, `contradicts`, `authored_by`. Foram 111 aplicadas só no domínio de engenharia de IA.

A diferença parece sutil e não é. Um retrieval que sabe que "A refuta B" não pode tratar isso igual a "A cita B". Quando você pergunta algo e o sistema puxa contexto, o tipo da aresta muda o peso da informação. Nota que contradiz a sua tese vale ouro. Nota que só menciona de passagem, nem tanto. Wikilink cru achata tudo no mesmo plano.

![A seção de conexões de um mapa do meu vault. Cada aresta declara o tipo da relação e a razão dela, não só que duas notas se tocam.](images/01-conexoes-tipadas.png)

## 2. RRF: não confie num ranking só

Reciprocal Rank Fusion. Nome feio, ideia simples.

Você não tem uma forma de buscar, tem várias. Busca lexical acha o termo exato. Busca semântica acha o parente que usa outras palavras. Busca por grafo acha o vizinho conectado. Cada uma devolve um ranking, e cada uma erra de um jeito diferente.

RRF funde os rankings. Uma nota que aparece bem colocada em três buscas diferentes ganha da nota que ficou em primeiro lugar em uma só, por sorte. É o oposto de apostar todas as fichas num único método de recuperação e rezar. Você combina os pontos de vista e deixa o consenso subir.

## 3. O nó grade: o que evita resposta confiante sobre lixo

Essa é a peça que ninguém coloca, e é a mais importante.

Existe um padrão que eu tirei de um paper chamado COMPILOT: o LLM propõe, um motor determinístico verifica e mede, e o resultado alimenta o loop de volta. Aplicado ao retrieval, isso vira um **nó grade**: antes de deixar o modelo responder, um passo lê o contexto recuperado e pergunta "isso é relevante pra pergunta que foi feita?".

Se o contexto não passa, o sistema busca de novo ou admite que não sabe. Não empurra uma resposta bonita construída sobre a nota errada.

É exatamente aqui que mora a diferença entre um RAG de demo e um sistema que você confia no dia a dia. Sem o grade, o modelo sempre acha algo pra dizer. Com o grade, ele tem permissão pra dizer "não achei". Um segundo cérebro que mente com confiança é pior que não ter segundo cérebro nenhum.

## Quando você não precisa de nada disso

Vou ser honesta, porque isso importa mais que o hype.

Se o teu vault tem algumas centenas de notas, você não precisa desse motor. `grep` mais o contexto do modelo resolve. Buscar na mão resolve. Montar link tipado, fusão de ranking e nó de avaliação pra uma base pequena é engenharia sobre um problema que você não tem.

O motor só começa a compensar quando o volume passa do ponto em que você não acha mais na mão, e quando a base cruza domínios diferentes o suficiente pra que a busca ingênua traga lixo. Pra chegar nesse ponto, foram 17 issues codadas e testadas, mergeadas na main. Não é script de fim de semana. É a diferença entre um brinquedo e uma ferramenta.

## O que vem no sábado

O motor é a britadeira. Ele minera.

Sábado eu mostro o que ele achou quando cruzou os cinco domínios do meu segundo cérebro de uma vez: 130 pontes entre áreas que eu nunca teria conectado à mão. O ativo, no fim, não são as notas. São as arestas.
