---
title: "Markowitz morre em cripto: a fronteira eficiente ignora o regime, o único fator que decide sobrevivência"
slug: markowitz-morre-em-cripto-sizing-por-regime
date: 2026-08-13
publishDate: 2026-08-13
draft: false
description: "Média de bull e bear é um mercado que não existe. A covariância muda com o regime e a diversificação encolhe na queda."
tags: ["cripto", "ia"]
images:
  - cover.png
---
Todo curso de finanças desenha a mesma figura: a fronteira eficiente de Markowitz, a curva elegante que promete o portfólio ótimo pra cada nível de risco. Foi construindo meu agente quant de cripto que eu aprendi a desconfiar dela. O primeiro tapa veio da estimativa de retorno esperado: o mesmo ativo, medido numa janela de 30 dias, dava -5% ao mês; medido numa janela de 180 dias, +15% ao mês. Qual dos dois entra no otimizador? Qualquer resposta é uma aposta disfarçada de matemática.

Os defeitos práticos de Markowitz em cripto estão documentados na minha própria spec do agente. A otimização inverte a matriz de covariância, e essa inversão amplifica erro de estimativa: mudança pequena no retorno esperado vira mudança grande nos pesos. A variância penaliza ganho tanto quanto perda, o que é um contrassenso pra uma classe de ativo cujo apelo inteiro é a assimetria positiva. E não existe estimativa estável de retorno esperado, como o exemplo das janelas mostra. Só que esses três defeitos, com anos de literatura e paliativo conhecido, ainda não são o problema central.

## A premissa escondida: uma matriz só

O problema central é a premissa de que existe UMA matriz de covariância. Ang e Timmermann, na revisão clássica sobre regimes em mercados financeiros, documentam que médias, volatilidades e covariâncias cruzadas dos retornos diferem entre regimes, e que as correlações variam no tempo. Cripto leva isso ao extremo: o mercado alterna entre bull, lateralização e bear como estados com dinâmicas próprias, e a matriz de covariância de um não serve pro outro.

Otimizar sobre a média histórica calibra o portfólio pra um mercado que não existe: a média de bull e bear. O anti-padrão aparece na pior hora possível. A diversificação que o otimizador mediu na média encolhe na transição pro bear, quando as correlações sobem e tudo cai junto. O portfólio "ótimo" quebra exatamente no momento em que a otimização deveria estar te protegendo.

![Dois painéis lado a lado: à esquerda, o que o Markowitz clássico vê, uma única matriz de covariância média e uma fronteira eficiente suave; à direita, o que o mercado de cripto faz, três regimes (bull, lateral, bear) com covariâncias próprias, e no bear as correlações sobem e a diversificação medida na média encolhe. A barra âmbar resume: otimizar sobre a média calibra pra um mercado que não existe.](images/01-covariancia-por-regime.png)

## Alocação como função do regime

A resposta que eu adotei no design do agente inverte a ordem: primeiro o regime, depois os pesos. A regra de alocação é uma função do estado detectado, não um vetor fixo. No meu agente, stablecoins ocupam de 5-10% no bull e sobem pra 40-60% no bear; altcoins fazem o caminho oposto e vão de 20-30% pra quase zero. Por cima disso existe um overlay de alta volatilidade que corta o sizing pela metade e alarga os stops em 30%, independente do regime primário. São regras de design informadas pela literatura, não resultado medido de performance: o primeiro ciclo do agente, aliás, fechou com Sharpe negativo, e eu contei essa história aqui no blog sem maquiagem.

A detecção do regime importa tanto quanto a tabela. Regra de threshold simples, tipo preço abaixo da média móvel igual bear, gera whipsaw em lateralização: troca de estado a cada ruído, e cada troca custa taxa e slippage. Uso um HMM de 3 estados porque ele carrega memória (o estado anterior influencia o próximo) e devolve probabilidade, não veredito binário, o que permite dimensionar posição proporcional à confiança. E não é só intuição minha: Nystrup e coautores mostraram no Quantitative Finance que alocação baseada em regime agrega valor sobre pesos estáticos e, em particular, reduz drawdowns por reagir à mudança de condição de mercado.

![Tabela de alocação por regime do agente quant: no bull, stablecoins em 5-10% e altcoins em 20-30%; na lateralização, stablecoins em 15-25%; no bear, stablecoins em 40-60% e altcoins perto de zero; no overlay de alta volatilidade, stablecoins em 50-60%, sizing cortado pela metade e stops 30% mais largos. A barra âmbar resume: a alocação é função do regime, não um vetor fixo.](images/02-alocacao-por-regime.png)

## Quando não usar

Sizing por regime não é resposta universal, e três situações me fariam largar a ideia. Altcoin de baixa liquidez: as features que alimentam a detecção (funding, volume, derivativos) são ruidosas ou nem existem, e o modelo detecta fantasma. Histórico curto: ajustar 3 estados em poucos meses de dado é astrologia com matriz de transição. E operação que não comporta o rebalanceamento: cada troca de regime dispara ordens, taxas e evento tributável; se o custo de girar come o ganho de reagir, o vetor estático perde feio no papel e ganha na conta.

A decisão que este post defende cabe numa frase: escolha o modelo de regime antes de escolher o otimizador. Markowitz responde "quanto de cada ativo". O regime responde "em qual mercado você está". Responder a primeira sem a segunda é precisão em cima da pergunta errada, e em cripto essa precisão custa o drawdown que decide se você continua no jogo.
