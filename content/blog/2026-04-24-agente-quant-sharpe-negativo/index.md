---
title: Construí um agente quant. Sharpe ficou -1.14. Não é fracasso.
slug: agente-quant-sharpe-negativo
date: 2026-04-22
publishDate: 2026-04-23
draft: false
description: Como construir um sistema robusto de quant trading em Python, testado e auditável. O que aprender quando a métrica inicial falha.
tags: ["quant-trading", "cripto", "python", "risk-management", "data-engineering"]
images: ["cover.png"]
---

Por 6 meses, construí um agente quant para trading de BTC/USDT.

Objetivo: maximizar retorno.

Resultado: Sharpe ratio de **-1.14**. Não é bom.

Mas aqui está o ponto: o sistema não fracassou. Fracassou em um objetivo (alpha), mas se saiu bem em outro (capital preservation).

Neste post, vou contar como construir um agente robusto, testado, auditável, e por que até "falhas" são vitórias quando você aprende delas.

---

## A Arquitetura: 7 Camadas

Quant trading é complexo. Não é "compre aqui, venda ali". É isso:

```
L1: Ingestion        (dados de verdade)
L2: Processing       (sinais)
L3: Intelligence     (previsões)
L4: Decision         (sizing)
L5: Execution        (minimizar impacto)
L6: Evaluation       (backtests)
L7: Compliance       (auditoria)
```

Cada camada é independente. Cada uma tem fallbacks.

### L1: Ingestion

```
- BinanceFetcher: OHLCV, funding rates, open interest, order book
- MacroFetcher: DXY, S&P 500 via yfinance
- GlassnodeFetcher: on-chain metrics
```

**Por que 3 fontes?** Triangulação. Se Binance cai, você continua com macro + on-chain.

### L2: Processing

```
32+ indicadores técnicos:
- RSI, MACD, Bollinger Bands (clássicos)
- ATR, Stochastic, Williams %R (volatilidade)
- Volume profile, Time-weighted moving average
- On-chain: MVRV, SOPR, Cumulative delta
- Macro: VIX-like crypto index

Tudo normalizado (z-score, min-max).
Tudo alinhado temporalmente (sem forward-looking bias).
```

### L3: Intelligence

Gaussian HMM (Hidden Markov Model) com 3 estados:

```
BULL (uptrend)    → RSI > 60 + momentum + macro positive
SIDEWAYS (range)  → RSI 40-60 + low volatility
BEAR (downtrend)  → RSI < 40 + momentum negative
```

LightGBM regressor prediz retornos nos próximos 4 candles (walk-forward).

**Insight crítico:** Você não precisa de accuracy 60% pra ter alpha. Você precisa de *consistency*. Um modelo que acerta 45% das vezes, mas com low drawdown, supera um modelo que acerta 70% mas com 30% max DD.

### L4: Decision

Quarter Kelly sizing. Não full Kelly (agressivo demais).

```
Position size = (edge * odds) / odds_ratio
Capped at 2% of portfolio (max risk per trade)

Guardrails (inegociáveis):
- Max drawdown: 15%
- Circuit breaker: 3 consecutive losses = pausa
- Kill switch: manual override sempre disponível
```

### L5: Execution

Almgren-Chriss (minimizar market impact):

```
Não execute 100% em 1 candle.
Quebre em 5-10 pequenas ordens.
Use TWAP/VWAP pra timing melhor.
Cheque liquidez antes de cada ordem.
```

### L6: Evaluation

Walk-forward backtesting (não data leakage):

```
Train window: 60 days
Test window: 5 days
Roll forward: shift 5 days, repeat

Métricas:
- Sharpe, Sortino, Calmar ratios
- Max drawdown
- Win rate
- Recovery factor
```

### L7: Compliance

```
- KillSwitch thread-safe (emergência)
- Auditor append-only em JSONL (irrevogável)
- Telegram notifications (alertas em tempo real)
- 202 testes (Python, pytest)
- CI/CD (GitHub Actions)
```

**O insight:** Engenharia de quant não é "acertar previsões". É construir um **sistema** testado, auditável, que falha com graça (drawdown mínimo).

---

## O Bug Que Revelou Tudo

Inicialmente, o Sharpe era **+0.66**. Parecia bom.

Então encontrei **data leakage no HMM**: o modelo via o futuro durante treinamento.

Um simples descuido:

```
# WRONG: treina com dados inteiros (future data vaza)
hmm.fit(all_indicators)

# RIGHT: treina apenas com passado até data T
hmm.fit(indicators_until_date_T)
```

Ao corrigir: Sharpe caiu para **-1.14**.

Esse momento foi crucial: **real >> espúrio**.

Eu poderia ter:
1. Ignorado o bug e lançado o sistema (risco: fraude)
2. Abandonado o projeto (risco: oportunidade de aprendizado perdida)

Em vez disso, documentei a correção, refiz os testes, e fiz a pergunta certa: "O que este sistema *realmente* resolve?"

---

## O Tradeoff: Alpha vs Preservação de Capital

Vamos aos números (out-of-sample, walk-forward):

| Métrica | Agente Quant | Buy & Hold |
|---------|-------------|-----------|
| Sharpe ratio | **-1.14** | -0.04 |
| Max drawdown | **0.29%** | 26.24% |
| Win rate | 1/7 windows | 4/7 windows |

Leia isso novamente.

Agente não tem alpha. Mas reduz drawdown em **~90x**.

Pergunte-se: em qual cenário você preferiria estar?

**Cenário 1:** Você compra e segura (Buy & Hold). Em um ano, há 1 dia onde você perde 26% de tudo. Dia seguinte, você recupera 15%. Você dorme?

**Cenário 2:** Você tá no agente. Max loss é 0.29% em qualquer dia. Você dorme melhor.

Preservação de capital > busca por alpha.

---

## Framework vs Resultado

O código não "falhou". O código *resolveu um problema diferente* do planejado.

Systems thinking:
- **Objetivo inicial:** Gerar retorno positivo (alpha)
- **Problema descoberto:** Alpha é raro (até pros profissionais)
- **Solução emergente:** Risk management é consistente
- **Resultado real:** Um sistema de preservação de capital

Às vezes, falhar no objetivo original é a forma que o universo tem de te mostrar o verdadeiro objetivo.

---

## O Stack Técnico

Para devs, aqui está o que funcionou:

**O que funcionou:**
- Python + SQLAlchemy (ORM robusto)
- asyncio (concorrência real, non-blocking I/O)
- pytest (202 testes passando)
- Postgres (auditoria append-only, compliance)
- Task Scheduler do Windows (low-cost orchestration)

**O que foi desafiador:**
- HMM em dados não-estacionários (quant é *hard*)
- Market microstructure (Almgren-Chriss é complexo)
- Real-time data latency (lag = slippage real)

**Stack final:**
```
Data ingestion:  Binance API + Glassnode + yfinance
ML stack:        scikit-learn (HMM), LightGBM (regressão)
Backend:         FastAPI (opcional, current: local scheduler)
Database:        Postgres 16 + JSONL audit trail
Notifications:   Telegram bot + Discord webhook
Infrastructure:  VPS barato (1 vCPU, 4GB RAM, 50GB NVMe)
```

Tudo roda em **uma máquina barata**. Sem Kubernetes, sem AWS bill assustador.

---

## 7 Lições Duradouras

### 1. Testes Primeiro (TDD)

202 testes = confiança. Você refatora sem medo.

Sem testes? Falhas silenciosas. Você descobre em produção.

```
Cada feature tem teste associado:
- test_hmmpredict.py (validação do modelo)
- test_kelly_sizing.py (risk management)
- test_market_impact.py (execution)
- test_audit_trail.py (compliance)
```

### 2. Auditoria é Design

JSONL append-only logs me salvaram quando questionei resultados.

```json
{"timestamp": "2026-04-22T10:30:00", "action": "BUY", "size": 0.05, "price": 65000, "reason": "BULL_regime_high_momentum"}
{"timestamp": "2026-04-22T11:45:00", "action": "CLOSE", "pnl": 50, "drawdown": 0.0015}
```

Você pode rastrear *por que* cada decisão foi tomada.

### 3. Constraints Geram Inovação

Quarter Kelly sizing é mais conservador que full Kelly. Mas foi mais efetivo.

Constraints (2% max risk, 15% max DD) obrigaram criatividade na decisão.

Livre demais = overfitting.

### 4. Real-time é Diferente de Backtesting

Walk-forward validation previne surpresas.

Seu modelo pode ter 70% de accuracy no backtest, mas em produção? 45%. Por quê?

- Slippage (você não pega o preço exato)
- Latência (0.5s de delay = preço diferente)
- Spread (bid/ask widening em volatilidade)

Real-time não perdoa.

### 5. Falhar é Learning

Data leakage (-1.14 vs +0.66) foi a descoberta mais valiosa.

Correção daquele bug = aprendi mais do que 10 livros sobre quant.

Não tenha medo de "falhas" que educam.

### 6. Simplicidade > Complexidade

3 estados no HMM funcionou melhor que 10+ features.

6 meses construindo. Resultado: simples.

Inversão de tempo: 95% construindo, 5% simplificando. Mas aqueles 5% = o código que realmente roda em produção.

### 7. Preservação de Capital > Busca por Alpha

Seu objetivo deve ser: "Não perder dinheiro."

Alpha (extra retorno) é bônus.

A maioria dos quants inverte: "Busco alpha, tolero perda."

Errado.

---

## O Que Vem Depois

Este agente não vai gerar riqueza da noite para o dia.

(Se alguém prometer isso, corre.)

Mas ele resolve um problema real:

> "Como construir um sistema robusto de decisão em Python?"

Próximos passos para você:

1. **Explore o código:** [github.com/tvazdataengineer/cripto_invest](https://github.com/tvazdataengineer/cripto_invest)
2. **Roda localmente:** `pytest` (todos 202 testes passam)
3. **Adapte:** Para stocks, commodities, cripto (framework é agnóstico)
4. **Realize:** Quão difícil é quant. Respeite quem faz bem.

---

## Qual É a Sua Métrica?

Sharpe é útil. Mas talvez você otimize para outra coisa:

- **Máxima riqueza em tempo mínimo?** (tempo alocado)
- **Mínimo drawdown?** (paz de espírito)
- **Mínimo capital needed?** (acessibilidade)

Escolha sua métrica. Construa para ela. Valide com dados reais.

Não a escolha dele. Não a moda. A sua.

---

Sharpe de -1.14 é um fracasso de marketing. Mas é um sucesso de engenharia.

Se o objetivo era aprender a construir um sistema robusto, testado, auditável, escalável, missão cumprida.

O próximo objetivo é seu.

Responde no [LinkedIn](https://linkedin.com/in/thacvaz) ou assina a [newsletter no Substack](https://vazdeng.substack.com) pra receber os próximos posts.
