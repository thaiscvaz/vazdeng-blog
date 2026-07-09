---
title: "Build verde, produção em chamas: quando o stub do teste ensina uma mentira sobre a lib real"
slug: stub-mentiroso-teste-verde-falha-producao
date: 2026-07-09
publishDate: 2026-07-09
draft: false
description: "Um modelo de ponta tirou nota baixa num benchmark de coding com CI 100% verde. O bug estava blindado pelo próprio mock. Teste verde não prova integração correta."
tags: ["ferramentas"]
images:
  - cover.png
---
Um agente de coding entregou o projeto inteiro. Docker buildando, Compose de pé, CI verde, RuboCop limpo, Brakeman sem alerta, README caprichado, suíte de testes passando. No papel, um trabalho sênior. Na primeira conversa real do app, `NoMethodError`. O recurso principal, a única coisa que o produto precisava fazer, estava quebrado desde o primeiro commit. E nenhum teste pegou.

Esse caso não é hipotético. É o que o Fabio Akita documentou no benchmark de coding dele de julho de 2026, lendo o código na mão em vez de confiar na nota automática. E ele expõe a armadilha que eu mais temo quando reviso código gerado por IA: o teste que passa exatamente sobre o bug.

## O mock que valida a alucinação

O benchmark do Akita é sempre o mesmo pedido: construir sozinho um chat estilo ChatGPT em Rails 8 com RubyLLM, Hotwire e Docker, com testes e CI. Ele então lê o resultado à mão e dá nota de 0 a 100.

O Sonnet 5, um modelo de nome forte, tirou 58 de 100, Tier C, posição 25. A casca estava impecável. O miolo, morto. O modelo chamou `chat.messages = history`, um setter que a versão 1.16 do RubyLLM simplesmente não tem. Em produção, isso estoura na primeira mensagem.

Aqui está a parte que interessa pra quem escreve teste. O bug não passou apesar da suíte. Ele passou por causa da suíte. O `FakeChat`, o dublê (mock, ou stub) que o próprio projeto criou pra testar sem chamar a API de verdade, definia `attr_accessor :messages`. Ou seja, o mock inventou o setter que a biblioteca real não oferece. O teste rodava contra uma versão idealizada da lib, confirmava a API que não existe, e pintava tudo de verde.

O mock não falhou em pegar o bug. Ele ensinou o bug pro teste.

## Verde não é sinal de integração, é sinal de concordância com o dublê

A lição não é sobre Ruby nem sobre um modelo específico. É sobre o que um teste verde realmente mede. Ele mede que o código concorda com o dublê que você escreveu. Se o dublê imita o contrato real da dependência, ótimo, o verde vale. Se o dublê imita uma versão que você imagina que a lib tem, o verde é uma mentira educada.

O contraste no mesmo benchmark mostra a diferença. O Gemini 3.5 Flash tirou 93, Tier A, usando a API real do RubyLLM: `with_instructions`, replay de histórico com `add_message`, `complete`, `response.content`. Tudo existe, tudo integra. Já o Sakana Fugu Ultra tirou 79 com um app que subia e conversava, mas só enviava a última mensagem pro modelo. A interface parecia um chat. O modelo trabalhava como se cada mensagem fosse a primeira. Verde por fora, sem memória por dentro.

Três modelos, três graus de "funciona". Só a leitura do código à mão separou o que integra do que finge integrar.

## O que eu mudei na forma de testar LLM

Eu leio código gerado e não confio em suíte verde de agente sem olhar o mock primeiro. Passei a tratar o dublê como a parte mais perigosa do teste, não a mais chata. A pergunta que faço em cada stub de integração de LLM é uma só: esse fake imita a biblioteca real ou uma versão que ficou conveniente pro teste passar?

Na prática isso vira três hábitos. Fixar a versão exata da dependência e gerar o dublê a partir do contrato dela, não da memória. Ter pelo menos um teste que sobe a integração de verdade, mesmo que rode devagar e fora do CI de cada commit. E desconfiar de todo verde que chega rápido demais num ponto de contato com biblioteca externa.

No Brasil isso pesa mais do que parece. Um bug blindado por mock não aparece no pipeline verde. Aparece na primeira interação real do cliente. E aí o custo não é o teste que faltou, é o incidente que a suíte prometeu que não aconteceria.

O veredito é simples e incômodo. Build verde prova que seu código concorda com as suas suposições. Não prova que suas suposições sobre a lib estão certas. Enquanto a nota vem de dentro do seu próprio mundo de dublês, ela pode estar te parabenizando pelo bug. A única auditoria que pega isso ainda é ler o código e rodar a coisa real. Nenhum verde substitui isso.
