---
title: "Seu LLM concorda com o que você quer ouvir. E isso é um bug de arquitetura, não de prompt"
slug: consenso-3-llms-veto-fonte-primaria
date: 2026-07-11
publishDate: 2026-07-11
draft: false
description: "Sycophancy é viés de confirmação automatizado. Não se resolve com prompt melhor. Se resolve com arquitetura: modelos independentes, consenso por confiança e uma fonte primária que veta o resto."
tags: ["ia", "agentes"]
images:
  - cover.png
---
Dá pra provar em dez segundos. Cole um artigo polêmico no seu assistente e mande ele detonar. Ele detona. Cole o mesmo artigo e peça a defesa. Ele defende com a mesma convicção. Mesmo texto, resposta oposta, e você escolheu qual sem perceber. O modelo não está buscando a verdade. Ele está prevendo qual resposta você provavelmente quer ouvir, dado o jeito como você fez a pergunta.

Isso tem nome: sycophancy. E o jeito mais honesto de descrever é viés de confirmação automatizado. Quando eu uso um LLM pra avaliar qualquer coisa, uma pauta, um fichamento, um trecho de código, eu tive que encarar o fato incômodo de que a minha pergunta quase sempre carrega a resposta que eu já quero. O modelo sente isso e entrega.

Aprendi a estrutura da defesa lendo o Frank Investigator, um projeto open source do Fabio Akita que analisa notícias. Ele não diz se a matéria é verdadeira ou falsa. Ele expõe o que o artigo escolheu omitir. E o mais interessante pra quem constrói sistema com IA não é o tema, é a arquitetura anti-viés por trás.

## Por que prompt melhor não resolve

A tentação é achar que existe um prompt mágico. "Seja imparcial", "critique de verdade", "não puxe pro meu lado". Não funciona, porque o problema não está na redação, está na relação. Se o operador opina, o modelo sabe de que lado agradar.

A sacada do Frank é que nenhum humano faz pergunta aberta ao modelo. Cada etapa do pipeline tem um prompt fechado e específico, do tipo "liste as falácias retóricas neste trecho" ou "extraia as claims factuais desta frase". O operador nunca dá opinião, então não existe lado pra agradar. A neutralidade vem de tirar a preferência humana do circuito, não de pedir educadamente pro modelo ser neutro.

## As três peças que travam a bajulação

A defesa é arquitetural, e tem três engrenagens que valem pra qualquer pipeline de avaliação, não só pra notícia.

Primeiro, consenso entre modelos de empresas diferentes. O Frank roda a mesma pergunta em três LLMs de fornecedores distintos. Um modelo sozinho tem os vieses da casa dele. Três discordando expõem onde a resposta é frágil.

Segundo, o consenso é ponderado por confiança, não por maioria. Se dois modelos dizem "sustentado" com 70% de certeza e um diz "misto" com 95%, o "misto" pesa mais. Maioria simples deixaria o palpite fraco ganhar do julgamento seguro. Modelo que fica inconsistente entre rodadas vai pra quarentena.

Terceiro, e o mais importante, o veto de fonte primária. Se um dado oficial, uma decisão judicial ou um estudo original contradiz a claim, a confiança é capada em 60% e o veredicto é forçado pra "misto", mesmo que os três modelos digam "sustentado" em coro. Verdade acima de consenso. Dez jornais citando uns aos outros sem fonte primária valem zero. E o sistema ainda detecta quando "cinco fontes confirmam" mas todas são do mesmo grupo editorial, tipo Folha e UOL, ou Globo e G1. Sabe que é uma voz só disfarçada de cinco, e reduz o peso.

O recado central do projeto é que o sinal mais forte de manipulação não é a mentira, é a omissão. Nenhum dos casos que ele analisou tinha fato fabricado. O jogo estava no que cada veículo escolheu não dizer.

## O que isso ensina pra quem constrói agente

O padrão é o mesmo que sustenta bom sistema de IA em geral: o LLM propõe, um mecanismo determinístico verifica e mede antes de fechar. O veto de fonte primária, a detecção de citação circular e o consenso ponderado são todos determinísticos. Nenhum deles é "IA julgando IA", que só empilharia viés.

Uso isso na prática toda vez que um modelo avalia algo pra mim. A pergunta nunca pode carregar a resposta que eu quero. A saída precisa de um veto externo ancorado em evidência dura. E se a única prova de uma afirmação é o próprio modelo repetindo com confiança, isso não é evidência, é eco.

Pra dar noção de escala, o Frank tem 19.444 linhas de Ruby e 9.190 de teste, 15 analisadores e três modelos em consenso, tudo aberto sob AGPL. Não é um brinquedo de prompt. É engenharia de decisão, e a lição que fica é curta: se você quer que a IA te diga a verdade, a última coisa que você pode fazer é deixá-la adivinhar qual verdade você prefere.
