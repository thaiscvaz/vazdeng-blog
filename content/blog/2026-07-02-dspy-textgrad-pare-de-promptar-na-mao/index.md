---
title: "Pare de escrever prompt na mão: DSPy e TextGrad tratam prompt como código compilável"
slug: dspy-textgrad-pare-de-promptar-na-mao
date: 2026-07-02
publishDate: 2026-07-02
draft: false
description: "Melhorar prompt não é redação manual, é compilação contra uma métrica. Dois frameworks de Stanford provam isso, e um deles saiu na Nature."
tags: ["ferramentas"]
images:
  - cover.png
---
Toda vez que vejo alguém ajustando uma frase no prompt, rodando, conferindo o resultado e voltando a ajustar a frase, eu vejo a mesma cena de quinze anos atrás: o cara editando configuração de servidor direto no SSH de produção, salvando, recarregando, torcendo. A gente parou de fazer isso com infraestrutura. Inventamos Terraform, declaramos o estado desejado, deixamos a ferramenta aplicar. Com prompt, a maioria dos times ainda está no SSH de produção, girando knob no olho.

A tese deste post é incômoda de propósito: melhorar um prompt não deveria ser trabalho de redação manual. Deveria ser compilação contra uma métrica. Você descreve o comportamento que quer, define o que conta como sucesso, e deixa um otimizador descobrir o texto que maximiza isso. DSPy e TextGrad, os dois saídos do ecossistema de Stanford, são as duas implementações sérias dessa ideia que eu olharia hoje.

## O prompt artesanal é software sem teste

Vou ser direta sobre por que o estado atual me irrita tecnicamente. Um prompt escrito na mão tem todos os pecados que a gente combateu em código e fingiu não ver em LLM.

Não é versionável de forma significativa. O diff de um prompt é um diff de prosa, e ninguém sabe dizer se a versão nova é melhor ou pior sem rodar na mão. Não é testável: você ajusta a frase, melhora num caso, quebra em três que você não reparou. Não é reproduzível: a pessoa que escreveu sabia por que aquela palavra estava ali, ela saiu da empresa, e agora aquela linha é conhecimento tácito embutido numa string. Isso é a definição literal de software frágil. A diferença é que a gente normalizou.

> Em uma frase: prompt na mão é o último reduto de configuração não declarativa que a engenharia ainda tolera, e DSPy e TextGrad são a tentativa séria de matá-lo.

A inversão que os dois propõem é a mesma que aconteceu com compiladores. Você não escreve assembly. Você descreve a lógica em linguagem de alto nível e deixa a toolchain gerar o código de baixo nível, melhor do que você escreveria à mão e de forma reprodutível. DSPy e TextGrad querem fazer isso com o prompt: o prompt vira o assembly que você nunca mais edita diretamente.

## DSPy: você declara o contrato, o otimizador compila o prompt

DSPy é mantido pelo Stanford NLP e a sigla significa **Declarative Self-improving Python**. O README oficial se descreve, palavra por palavra, como "the framework for *programming, rather than prompting, language models*". A proposta concreta é você parar de escrever o texto do prompt e declarar três coisas em Python.

**Signature** é o contrato de entrada e saída de uma chamada de LLM, tipo `contexto, pergunta -> resposta`. Diz o que a chamada faz, não como prompá-la. **Module** é o bloco que implementa uma estratégia de inferência sobre a signature, como `Predict`, `ChainOfThought` ou `ReAct`, e você compõe módulos num programa Python normal com loops e condicionais. **Optimizer** é onde a mágica acontece: ele recebe seu programa, uma função-métrica que pontua a saída e alguns exemplos, e ajusta automaticamente as instruções e seleciona as demonstrações few-shot para maximizar a métrica.

O otimizador que eu citaria como o estado da prática é o MIPROv2. A documentação oficial descreve o que ele faz sem rodeio: "Generates instructions *and* few-shot examples in each step. The instruction generation is data-aware and demonstration-aware. Uses Bayesian Optimization to effectively search over the space of generation instructions/demonstrations across your modules." Em português: ele gera instruções e exemplos, leva em conta seus dados, e usa otimização Bayesiana para varrer o espaço de prompts possíveis de forma eficiente.

O passo final chama-se `compile`. E o nome é honesto: o que sai é um pipeline executável com os prompts já otimizados, congelado, versionável. Você compilou seu prompt a partir de código, dados e métrica. Não escreveu uma frase.

```python
import dspy

class GerarResposta(dspy.Signature):
    """Responde a pergunta usando o contexto recuperado."""
    contexto = dspy.InputField()
    pergunta = dspy.InputField()
    resposta = dspy.OutputField()

otimizador = dspy.MIPROv2(metric=minha_metrica_de_acerto)
rag_compilado = otimizador.compile(programa, trainset=exemplos)
# rag_compilado carrega instrucoes + few-shot otimizados pela metrica
```

## TextGrad: o mesmo objetivo, por gradiente textual

TextGrad ataca o mesmo problema por outro ângulo, e esse vale uma pausa porque saiu na Nature. O paper se chama "Optimizing generative AI by backpropagating language model feedback", publicado na *Nature* em 2025, volume 639, páginas 609 a 616, do grupo do James Zou em Stanford. Eu fiz questão de checar isso na própria Nature antes de escrever, porque "publicado na Nature" é o tipo de claim que vira lenda de LinkedIn rápido demais.

A sacada é replicar a mecânica do autograd do PyTorch, mas onde o gradiente não é um número e sim feedback em linguagem natural gerado por um LLM. Você envolve o texto a otimizar numa `Variable` com `requires_grad=True`, define uma loss em linguagem natural ("avalie se esta resposta está correta e completa"), e ao chamar `.backward()` um LLM produz uma crítica textual de como aquela variável deveria mudar. O otimizador TGD (Textual Gradient Descent) aplica essa crítica e reescreve o texto. Forward, loss, backward, step. A mesma coreografia do treino de rede neural, com prosa no lugar de números.

A diferença prática de timing entre os dois importa na hora de escolher. **DSPy otimiza no compile-time**: você compila uma vez contra um conjunto de exemplos e congela o programa para produção. **TextGrad otimiza por iteração de feedback**: cada ciclo refina a variável, podendo rodar em loop. Conceitualmente os dois fazem a mesma coisa profunda, treinar o sistema de LLM sem tocar nos pesos do modelo, mexendo no texto que o orquestra.

## Manual contra compilado, lado a lado

| Dimensão | Prompt na mão | DSPy / TextGrad |
|---|---|---|
| Como melhora | editar prosa no olho | otimizar contra métrica/loss |
| Versionável | diff de texto sem significado | artefato compilado, reproduzível |
| Testável | "rodei e pareceu melhor" | métrica explícita pontua a saída |
| Quem detém o saber | tácito, na cabeça de quem escreveu | código + dados + métrica |
| Troca de modelo | reescrever tudo na mão | recompilar contra a mesma métrica |
| Custo | barato por iteração, caro no acúmulo | caro no compile, barato depois (DSPy) |

E uma tabela rápida de DSPy contra TextGrad, porque não são intercambiáveis:

| | DSPy | TextGrad |
|---|---|---|
| Timing | compile-time, congela e serve | iterativo, loop de crítica |
| Unidade | programa de módulos + signatures | variável de texto + loss natural |
| Caso natural | pipelines (RAG, classificação, agente) | otimizar uma saída/código/solução por crítica |
| Origem | Stanford NLP | Zou Group, Nature 2025 |

## O verdito honesto: quando vale e quando é overkill

Sou cética de ofício com hype de ferramenta, então o veredito vem com o lado ruim explícito.

Vale quando o prompt é **repetido, mensurável e de volume**. Pipeline que roda todo dia, que você consegue pontuar de forma objetiva, onde um ganho de qualidade se multiplica por milhares de execuções. É exatamente onde prompt artesanal acumula mais dívida silenciosa, e onde compilar paga o investimento. Para classificação, extração estruturada, RAG com resposta verificável, é o caso de ouro.

Não vale, e aqui está o coração do Tool Verdict, em três situações que eu recusaria de cara.

**One-off.** Se o prompt roda uma vez ou dez, o custo de montar métrica, trainset e rodar o otimizador (que faz muitas chamadas de LLM no processo) supera o de só escrever um prompt decente à mão. Compilar para descartar é desperdício.

**Métrica fraca.** O valor inteiro depende de uma função-métrica que capture qualidade de verdade. Se a métrica é ruim ou enviesada, o otimizador maximiza a métrica errada com competência assustadora. É Goodhart puro: a medida vira alvo e deixa de ser boa medida. Para saída subjetiva sem rótulo confiável, o ganho evapora.

**Sem volume.** Sem repetição que dilua o custo de compile, a conta não fecha. Otimização Bayesiana e loop de gradiente textual gastam chamadas. Se você não vai amortizar isso em escala, fica mais caro que o problema.

Outro ponto de honestidade técnica: nenhum dos dois troca os pesos do modelo. Eles otimizam o texto que orquestra o LLM, não fazem fine-tuning. Se o gargalo é capacidade do modelo base, recompilar prompt não resolve. E o ferramental ainda evolui rápido, então para pipeline crítico eu fixaria versão e testaria, sem tratar como infra estável de longo prazo.

## Anti-padrões

- Adotar DSPy num classificador de uma linha que já funciona. Dependência e complexidade sem retorno.
- Compilar contra uma métrica que você não confia. Você vai otimizar lindamente a coisa errada.
- Achar que "compilado" é eterno. O artefato depende do modelo que o gerou; trocou de modelo, recompila.
- Confiar cegamente no loop do TextGrad. Ele é estocástico (LLM avaliando LLM) e pode oscilar ou regredir entre iterações. Precisa de verificação por cima.
- Rodar otimizador sem orçar o custo de API antes. O compile faz muitas chamadas; meça primeiro.
- Repetir o mantra "prompt engineering morreu". Não morreu. Virou compilação no caso certo, e continua artesanal no caso pequeno.

Se você mantém qualquer pipeline de LLM em produção, a pergunta de checklist é uma só: meu prompt é um artefato compilado contra uma métrica que eu confio, ou é uma string mágica que alguém ajustou no olho e ninguém ousa tocar? Se for a segunda, você não tem um prompt. Você tem dívida técnica com cara de texto.
