---
title: "Os 5 subsistemas que separam um agente que funciona de um que só parece funcionar"
slug: harness-5-subsistemas-agente-que-funciona
date: 2026-06-27
publishDate: 2026-06-27
draft: false
description: "Semana passada eu escrevi que a LLM não faz nada, o harness faz. Recebi várias mensagens concordando, e uma que me incomodou: \"ok, entendi que o harness impo..."
tags: ["ia", "agentes"]
images:
  - cover.png
---
Semana passada eu escrevi que a LLM não faz nada, o harness faz. Recebi várias mensagens concordando, e uma que me incomodou: "ok, entendi que o harness importa. Mas o que é o harness, na prática?". Justo. Aquele post provou QUE o harness é o que move o agente. Este aqui abre o capô e mostra O QUE tem dentro. São cinco subsistemas. Falta um, e você tem o agente que eu chamo de "só parece funcionar": demo linda na sexta, quebrado na segunda em produção.

Eu uso esse modelo de cinco peças como checklist sempre que crio um agente novo, e ele já me salvou de mais de um pipeline que parecia pronto e não estava.

## O modelo: cinco peças, nenhuma opcional

Pensa num cozinheiro novo na sua cozinha. Pra ele entregar um prato, ele precisa de cinco coisas. Tira qualquer uma e o melhor chef do mundo vira inútil. Agente é igual.

**1. Instructions.** O livro de receitas da casa. Não é o cardápio do mundo, é o que ESTA cozinha faz: visão geral, comandos, restrições, links. No agente, é o `CLAUDE.md` ou `AGENTS.md`. Responde "qual é o universo de regras em que eu opero?". Sem isso, o agente gera solução genérica em vez de raciocinar sobre o SEU código.

**2. Tools.** As facas, as panelas, o fogão. As ações que o agente sabe executar: shell, editar arquivo, buscar, rodar teste. Responde "o que eu sei fazer?". Sem ferramenta, não adianta pedir pra ele "tentar mais".

**3. Environment.** A despensa estocada, o gás ligado. O estado autoexplicativo do ambiente: `pyproject.toml`, `.python-version`, Docker. Responde "onde estou, tenho tudo instalado?". Sem isso, o agente gasta metade da sessão se organizando antes de começar.

**4. State.** A anotação do prato que o cozinheiro do turno anterior deixou meio pronto. Onde paramos, por que decidimos X: `PROGRESS.md`, `feature_list.json`, commits. Responde "o que aconteceu antes desta sessão?". Sem State, toda sessão recomeça do zero.

**5. Feedback.** O paladar treinado, o termômetro, o cronômetro. O que conta como "funcionou": `pytest`, `mypy`, `make check` declarados. Responde "como sei que terminei bem?". Sem Feedback, o agente serve o prato "achando que tá bom".

![Os cinco subsistemas do harness na analogia da cozinha: Instructions (o livro de receitas), Tools (as facas e panelas), Environment (a despensa estocada), State (a anotação do turno anterior) e Feedback (o paladar e o termômetro). Feedback é a peça que quase sempre falta; sem ela o agente só parece funcionar.](images/01-cinco-subsistemas.png)

## O agente que só parece funcionar

Quase sempre falta o mesmo subsistema: **Feedback**.

O agente sem Feedback é o mais perigoso porque ele é convincente. Ele escreve o código, marca a tarefa como concluída, retorna exit 0. Tudo parece ok. Aí você inspeciona o trace e descobre que metade dos arquivos foi escrita por outro modelo num fallback silencioso, ou que os testes são teatro de cobertura que nunca exercitam a lógica real. Akita documentou exatamente isso num benchmark recente: um modelo em opencode batia num erro de protocolo que o harness soterrava no event stream e caía pro fallback. A run "completava", os arquivos eram escritos, e só no trace dava pra ver que o autor real era outro. Exit 0 não é sucesso.

![Exit 0 não é sucesso: o que você vê (exit 0, tarefa concluída, demo linda) contra o que o trace revela (fallback silencioso pra outro modelo, testes que não exercitam a lógica, código escrito por outro, quebrado em produção). 65% das falhas de IA em empresa são defeito de harness, não do modelo.](images/02-exit-zero.png)

A lição que levei pros meus próprios pipelines de engenharia de dados: nunca confiar em "retornou sem erro". Eu instrumento verificação de output esperado, não só de código de saída.

E os números que vi essa semana reforçam: pesquisa recente atribui 65% das falhas de IA em empresa a defeitos de harness (context drift, desalinhamento de schema, degradação de state), não ao modelo. Um estudo de ablação levou um GPT-5.2 fixo de 52,8% para 66,5% num benchmark só mexendo na infraestrutura ao redor, sem tocar no modelo. A peça que falta é sempre um desses cinco subsistemas.

## Quando você NÃO precisa dos cinco

Importante, porque o oposto também é armadilha. Se o que você quer é um script one-shot, "resume esse texto", "classifica esses 50 e-mails", uma chamada e acabou, você não precisa de harness nenhum. Não tem sessão seguinte, então não precisa de State. Não tem ambiente pra navegar, então Environment é irrelevante. Montar os cinco subsistemas pra uma tarefa one-shot é overengineering puro. O harness completo se justifica quando o agente opera de forma contínua, sobre um ambiente real, ao longo de várias sessões. Os meus projetos open-source, um agente de engenharia de dados e meu projeto de cripto, são esses casos. Um prompt de resumo, não.

## O modelo mental que fica

Os cinco subsistemas não são receita rígida, são inventário. Antes de aprovar um agente novo, eu passo o checklist: tem Instructions? Tools? Environment? State? Feedback? Se um está faltando, o harness está incompleto, e o agente vai te decepcionar exatamente no momento em que você confiar nele. A diferença entre funcionar e parecer funcionar mora quase sempre na quinta peça, a que ninguém quer construir porque dá trabalho e não aparece na demo.
