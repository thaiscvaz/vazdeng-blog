---
title: "Quando o modelo deveria dizer 'não sei'"
slug: hmm-aprende-a-abster
date: 2026-05-17
publishDate: 2026-05-17
draft: false
description: "Depois do Sharpe -1.14, o que ainda incomodava no meu HMM era outra coisa. Ele nunca dizia 'não sei'. Sempre devolvia BULL, SIDEWAYS ou BEAR, mesmo quando o mercado entrava em zona que ele nunca tinha visto."
tags: ["cripto", "hmm", "quant", "risk-management", "agente-quant"]
images:
  - cover.png
---

O post anterior fechou o capítulo do Sharpe -1.14: o número é ruim em alpha, é honesto em risco, e eu prefiro um sistema honesto a um sistema decorativo.

Mas tinha um ponto cego que não aparecia no Sharpe. Um problema diferente, mais sutil. Resolvi essa semana.

## O que sobrou depois de consertar o data leakage

O HMM de regime do meu agente quant classifica candle a candle entre três estados: BULL, SIDEWAYS, BEAR. Treinado com 8 features (price vs EMA200, ADX, RSI, BB width, vol ratio, return 7, DI spread, funding zscore). Depois do data leakage fix, a posterior virou causal (forward-only), o Sharpe caiu de +0.66 espúrio para -1.14 real, e tudo bem.

O problema é que o modelo continuava classificando sempre. Mesmo quando as features entravam em uma região que ele nunca tinha visto no treino.

Cenário concreto: ATR diário 4x acima da média de 90 dias, funding rate em zona de extremo negativo, volume 10x acima do normal. Um pico que o modelo simplesmente não tem ponto de referência. O que o HMM devolve? "BULL com 73% de confiança", porque a posterior dele soma 1.0 entre as três classes e uma delas vai ganhar.

Matematicamente legítimo. Operacionalmente perigoso.

## Onde aprendi a chamar isso pelo nome

A literatura chama isso de **out-of-distribution problem**. Em sistemas críticos (medicina, fraude, infraestrutura), existe uma prática estabelecida: o modelo precisa ter a opção de abster. Em vez de chutar entre as classes que conhece, devolver um rótulo do tipo `unknown`, `OOD`, `low confidence`, e deixar o operador decidir.

Vi isso descrito como **conservative degradation**: quando o sinal é fraco ou os dados estão fora do que o modelo viu, o sistema prefere parar a fabricar. Os modelos atuais de classificação de fato-vs-rumor em IA aplicam exatamente esse princípio, e eu queria trazer pro meu agente quant.

A pergunta prática: como detectar OOD num HMM gaussiano de 3 estados sem adicionar 200 linhas de código?

## A implementação que cabe em 20 linhas

As features do HMM passam por um `StandardScaler` antes do treino. Isso quer dizer que, no espaço escalado, a média de cada feature no treino é zero e o desvio padrão é um. Qualquer candle novo que aparecer com uma feature em z-score absoluto muito alto está, por definição, fora da distribuição que o modelo aprendeu.

Defini o limite em 5 sigmas (conservador, considerando que cripto tem fat tails). E adicionei um método estático no `MarketRegimeHMM`:

```python
@staticmethod
def is_ood(x_scaled_row, threshold=OOD_SIGMA_THRESHOLD):
    if x_scaled_row.size == 0:
        return False
    return bool(np.nanmax(np.abs(x_scaled_row)) > threshold)
```

E mudei o `predict_state` para checar isso antes de chamar a posterior:

```python
if self.is_ood(last_features):
    logger.warning("OOD detectado: max |z| = %.2f > %.1f. Abstem-se.",
                   max_dev, OOD_SIGMA_THRESHOLD)
    return REGIME_OOD, 0.0, {REGIME_OOD: 1.0}
```

O downstream da decisão (`decide_position` na camada 4) já tinha um lookup em `REGIME_MULTIPLIER`. Adicionei `"OOD": 0.0`, defesa em camadas, e um log explícito de "ABSTAIN" para deixar visível quando o sistema preferiu não operar.

70 testes passaram, mais 2 novos cobrindo o caminho OOD. Suite completa em 6 segundos.

## O que muda no comportamento do agente

Antes: o sistema chutava um regime mesmo em condição de mercado que ele nunca tinha visto. Esse chute alimentava a função de sizing, que respeitava o cap de 2% mas ainda assim abria posição.

Depois: o sistema lê o tick atual, percebe que está fora da distribuição de treino, devolve `OOD` ao invés de BULL/SIDEWAYS/BEAR, e o decisor zera o sizing automaticamente. O log mostra explicitamente "ABSTAIN: regime sem playbook (OOD, conf=0.000). Sizing=0". Nada de operação no escuro.

Em termos práticos: o agente passa a ter três opções de output, não duas. Operar com convicção. Esperar com convicção. E agora também admitir que não sabe.

## Por que isso vale mais que tentar caçar alpha

A intuição comum é que adicionar uma classe `OOD` reduz a frequência de trade e portanto o retorno. É verdade. Em backtest histórico, posso reduzir o número de operações em algum percentual.

Mas o trade que eu deixei de fazer era um trade tomado em estado de modelo confuso. Capital preservation primeiro, lembra? Cada vez que o sistema abstém, ele me dá tempo de olhar manualmente o que está acontecendo. Pode ser um flash crash, uma mudança de regime macro, um erro de feature na ingestão. Em todos os casos, prefiro o sistema parado a fabricar uma decisão que depois eu não saberia explicar.

A regra acabou sendo: se o modelo sai do conforto da distribuição que viu, ele me chama. E eu decido se quero substituir a abstenção por uma intervenção manual, ou se aceito que esse não é momento de operar.

Isso não substitui melhorar o modelo. É só o reconhecimento honesto de que nenhum modelo de 3 estados, com 8 features, vai cobrir todos os regimes possíveis de um mercado que tem ciclos de adoção, eventos macro, halvings e mudanças regulatórias.

## O próximo capítulo

A versão atual aceita um único critério de OOD (z-score absoluto). Já tenho duas extensões pensadas: Mahalanobis distance no espaço completo (capta correlações que z-score perde) e likelihood do tick sob o modelo HMM treinado (mais sensível, mais caro). Ambas em backlog.

Por enquanto, o que está em produção é a versão simples. E ela já mudou meu sono.

Você já teve um modelo que devolveu confiança alta numa decisão que não deveria ter sido tomada? Me conta no [LinkedIn](https://linkedin.com/in/thaisvaz) ou assina a [newsletter](https://vazdeng.substack.com) para receber os próximos posts.
