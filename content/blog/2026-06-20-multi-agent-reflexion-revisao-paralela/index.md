---
title: "Por que pedir pra IA revisar o próprio código não funciona (e o que funciona)"
slug: multi-agent-reflexion-revisao-paralela
date: 2026-06-20
publishDate: 2026-06-20
draft: false
description: "IA Foundations 03: pedir pro mesmo modelo se autocorrigir pode degradar o raciocínio. A alternativa com múltiplos agentes chega a 82.6% no HumanEval."
tags: ["ia", "agentes"]
images:
  - cover.png
---
Existe um padrão tentador em pipelines com IA: pede pro modelo gerar, depois pede pro mesmo modelo revisar o que gerou.

Parece inteligente. Tem uma lógica atraente. O modelo vai olhar com "outros olhos" e pegar o que errou na primeira passagem.

Não funciona. Testei, vi nos resultados, e tem pesquisa mostrando que em alguns casos piora.

Mas existe uma versão que funciona. A diferença está em quem faz a revisão.

## O que é Reflexion e por que falha

Reflexion é um framework publicado por Shinn et al. em 2023. A ideia é simples: o agente gera uma resposta, recebe feedback sobre o que errou, e tenta de novo. Iterativo, autocorretivo.

Funcionou o suficiente pra virar padrão em vários sistemas. O problema é o que acontece depois da segunda ou terceira iteração.

O modelo cai no que os pesquisadores chamam de degeneration of thought. Em vez de explorar caminhos diferentes, o agente começa a repetir os mesmos erros com palavras levemente diferentes. A autocrítica passa a ser performática. O modelo "sabe" que errou, menciona o erro, e comete de novo.

Por que isso acontece? Porque o mesmo modelo com os mesmos pesos vai ter os mesmos padrões de raciocínio. Você pode mudar o prompt, dar feedback explícito, pedir perspectivas diferentes. No fundo, é o mesmo processo gerando variações do mesmo output.

Huang et al. 2023 (arXiv:2310.01798) mostrou que autocorreção intrínseca, sem feedback externo, chega a degradar o raciocínio do modelo. Não é marginal. Em vários casos, pedir pra revisar a si mesmo atrapalha mais do que ajuda.

## MAR: múltiplos agentes, múltiplos padrões de raciocínio

O paper MAR (arXiv 2512.20845) parte de um diagnóstico direto: se o problema é que um LLM não consegue escapar dos próprios padrões, a solução é ter padrões diferentes.

MAR encadeia quatro etapas com agentes distintos:

**Actor:** gera a solução inicial. Não sabe que vai ser revisado.

**Evaluator:** testa o output e sinaliza quando há falha. É o gatilho da revisão, não o revisor em si.

**Critics por persona:** quando o Evaluator sinaliza falha, múltiplos critics, cada um com uma persona diferente, entram em debate sobre o que quebrou. Não é um crítico só dando veredito. São perspectivas distintas argumentando entre si.

**Judge:** sintetiza o debate dos critics numa Consensus Reflection, o diagnóstico consolidado que instrui o Actor a refazer.

A separação força perspectivas diferentes. Cada critic ataca o problema por um ângulo, o debate expõe pontos cegos que um revisor único não veria, e o judge não tem viés de autoria porque não gerou a solução original.

Os resultados: HumanEval (benchmark de programação) subiu de 76.4% para 82.6%. HotPotQA chegou a 47% de exact match. Os dois superam Reflexion com agente único.

## O custo real e quando não vale a pena

MAR não é gratuito. O overhead é de aproximadamente 3x em chamadas de API comparado com Reflexion simples. Em pipeline que usa LLM em cada evento, isso muda o custo operacional de forma significativa.

Quando faz sentido usar: código que vai pra produção e erros têm custo alto, decisões que afetam dado de cliente, geração de SQL complexo que vai rodar em dado financeiro, situações onde revisar manualmente depois é mais caro que 3x o custo de API.

Quando não faz sentido: tasks simples one-shot, extração de campos estruturados de documentos padronizados, qualquer caso onde você já tem testes automatizados que capturam os erros relevantes.

A lógica é a mesma de qualquer decisão de custo em engenharia: o custo extra tem que ser menor que o custo do erro que você está prevenindo.

IA Foundations 02 mostrou que o modelo não faz nada. O harness faz. Esse post é o próximo passo: quando o harness pede ao modelo pra revisar a si mesmo, os resultados são ruins. Quando o harness orquestra múltiplos papéis com perspectivas independentes, os resultados melhoram.

O padrão não é "IA revisa IA". O padrão é papéis diferentes com responsabilidades diferentes produzindo raciocínio que um único papel não consegue.

É o que uso em produção hoje. O paper confirma por que funciona.
