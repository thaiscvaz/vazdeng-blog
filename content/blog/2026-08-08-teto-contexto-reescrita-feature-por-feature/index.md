---
title: "1M linhas não cabem no LLM. Por que reescrita direta falha e o loop feature-por-feature funciona"
slug: teto-contexto-reescrita-feature-por-feature
date: 2026-08-08
publishDate: 2026-08-08
draft: false
description: "O caso FrankClaw: a ordem direta devolve casca com promessa dentro. O loop lento produz sistema 22x menor que compila."
tags: ["ia", "agentes"]
images:
  - cover.png
---
Em março o Akita pediu a um assistente de código a coisa mais natural do mundo: "reescreve esse projeto em Rust". O projeto era o OpenClaw, um gateway de chat com IA que tinha crescido num ritmo de 50 commits por dia, vindos de 42 contribuidores, até passar de 1,2 milhão de linhas de TypeScript. Ele tentou a ordem direta em dois assistentes de código de fronteira, e os dois falharam do mesmo jeito: tipos criados sem implementação e `todo!()` espalhado por toda parte. A casca do projeto inteiro, com promessa dentro.

A falha não é de capacidade, é de geometria. Um codebase de 1,2 milhão de linhas não cabe na janela de contexto de modelo nenhum. Já escrevi aqui sobre o que acontece quando a informação cai no meio de uma janela onde ela cabe; o problema de hoje é o passo anterior: o sistema que nem cabe. E quando não cabe, o modelo não avisa que está trabalhando às cegas. Ele gera uma resposta com a forma certa e preenche o resto com plausibilidade. E plausibilidade em volume é o pior tipo de defeito pra revisar: o código parece completo, compila em pedaços, e o buraco só aparece quando alguém tenta rodar o caminho de ponta a ponta.

## O loop que funciona é lento de propósito

A técnica que produziu código de verdade no caso FrankClaw é tediosa: pedir a análise do original em etapas, escrever um plano longo por feature, implementar uma feature por vez em Rust com testes, commitar, repetir. Cada iteração cabe na janela com folga, e cada commit vira um checkpoint verificável antes do próximo passo. O resultado desse loop: quase 57 mil linhas de Rust funcionais em cerca de 5 dias, um sistema 22x menor que o original.

![O contraste entre as duas abordagens de reescrita com LLM: à esquerda, a ordem direta de reescrever 1,2 milhão de linhas de uma vez estoura o teto de contexto e devolve tipos sem implementação e todo!() por toda parte; à direita, o loop feature-por-feature, com análise em etapas, plano por feature, uma feature com teste, commit e repetição, mantém cada iteração dentro da janela e produziu quase 57 mil linhas funcionais em cerca de 5 dias. A barra âmbar resume: a janela de contexto é a cabeça do modelo, dimensione o trabalho pra ela.](images/01-loop-feature-por-feature.png)

A parte do trabalho que não dá pra terceirizar é decidir o que não reescrever. Dos 28 canais de mensagem do original, ele manteve 7 e jogou fora 21. Complexidade sem valor proporcional é peso morto, e o loop feature-por-feature te força a olhar cada peça e perguntar se ela merece existir. A reescrita direta nunca oferece essa chance: ela copia a entropia junto com o comportamento.

O loop também não fecha o trabalho sozinho. Depois do código funcional vieram 22 commits só de security hardening, sobre um original que carregava 7 vulnerabilidades críticas conhecidas. Funcionalidade reescrita não é segurança auditada, e essa fase pediu mais direção humana que qualquer outra.

## Como isso vira regra no meu dia a dia

Uso a mesma mecânica em trabalho que nem é reescrita. Meu workflow padrão quebra qualquer implementação em issues de um comportamento, com plano escrito antes do código e limpeza de contexto entre as etapas. Aprendi a manter a minha conversa com o modelo abaixo da metade da janela, porque a degradação começa bem antes do limite oficial. O teto de contexto é restrição de engenharia, não preferência de estilo, e tratar ele como restrição muda o desenho do trabalho: o tamanho do passo passa a ser uma decisão de arquitetura.

Vale nomear quando o loop não paga: projeto pequeno, que cabe inteiro na janela com folga, dispensa a cerimônia. Geração direta resolve, e o overhead de plano por feature só atrasa. O loop existe exatamente pro caso em que a ordem direta quebra: sistema maior que a janela, onde cada passo precisa de um checkpoint que alguém consegue verificar.

A lição que fica não é "IA não consegue reescrever sistema grande". É a inversão dela: ninguém consegue, de uma vez só. A IA apenas tornou visível uma regra que a engenharia já conhecia: trabalho grande demais pra caber numa cabeça se quebra em pedaços com teste. A janela de contexto é a cabeça do modelo. Dimensione o trabalho pra ela.
