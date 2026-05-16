---
title: "When the model should say 'I don't know'"
description: "After the -1.14 Sharpe, what still bothered me about my HMM was something else. It never said 'I don't know'. It always returned BULL, SIDEWAYS, or BEAR, even when the market entered a zone it had never seen."
tags: ["crypto", "hmm", "quant", "risk-management", "agente-quant"]
images:
  - cover.png
---

The previous post closed the chapter on -1.14 Sharpe: the number is bad on alpha, honest on risk, and I'd rather have an honest system than a decorative one.

But there was a blind spot the Sharpe didn't show. A different, more subtle problem. I solved it this week.

## What was left after fixing the data leakage

My quant agent's HMM regime classifier labels each candle as one of three states: BULL, SIDEWAYS, BEAR. It's trained on 8 features (price vs EMA200, ADX, RSI, BB width, vol ratio, return 7, DI spread, funding zscore). After the data leakage fix, the posterior became causal (forward-only), the Sharpe fell from a spurious +0.66 to a real -1.14, and that was fine.

The problem was that the model still classified, always. Even when the features entered a region it had never seen in training.

A concrete scenario: daily ATR 4x above the 90-day average, funding rate in extreme negative zone, volume 10x above normal. A spike the model has no reference point for. What does the HMM return? "BULL with 73% confidence", because its posterior sums to 1.0 across the three classes and one of them has to win.

Mathematically legitimate. Operationally dangerous.

## Where I learned to name this

The literature calls this the **out-of-distribution problem**. In critical systems (medicine, fraud, infrastructure), there's an established practice: the model needs the option to abstain. Instead of guessing among the classes it knows, return a label like `unknown`, `OOD`, `low confidence`, and let the operator decide.

I saw this described as **conservative degradation**: when the signal is weak or the data is outside what the model has seen, the system prefers to stop rather than fabricate. Current models for fact-vs-rumor classification in AI apply exactly this principle, and I wanted to bring it to my quant agent.

The practical question: how do you detect OOD in a 3-state Gaussian HMM without adding 200 lines of code?

## An implementation that fits in 20 lines

The HMM features go through a `StandardScaler` before training. That means, in the scaled space, the mean of each feature in training is zero and the standard deviation is one. Any new candle that shows up with a feature at high absolute z-score is, by definition, outside the distribution the model learned.

I set the limit at 5 sigmas (conservative, given crypto has fat tails). And I added a static method to `MarketRegimeHMM`:

```python
@staticmethod
def is_ood(x_scaled_row, threshold=OOD_SIGMA_THRESHOLD):
    if x_scaled_row.size == 0:
        return False
    return bool(np.nanmax(np.abs(x_scaled_row)) > threshold)
```

And I changed `predict_state` to check this before calling the posterior:

```python
if self.is_ood(last_features):
    logger.warning("OOD detected: max |z| = %.2f > %.1f. Abstaining.",
                   max_dev, OOD_SIGMA_THRESHOLD)
    return REGIME_OOD, 0.0, {REGIME_OOD: 1.0}
```

The downstream decision (`decide_position` in layer 4) already had a lookup in `REGIME_MULTIPLIER`. I added `"OOD": 0.0` as defense in depth, plus an explicit "ABSTAIN" log to make it visible whenever the system chose not to operate.

70 tests passed, plus 2 new ones covering the OOD path. Full suite in 6 seconds.

## What changes in the agent's behavior

Before: the system guessed a regime even in market conditions it had never seen. That guess fed into the sizing function, which respected the 2% cap but still opened a position.

After: the system reads the current tick, recognizes it's outside the training distribution, returns `OOD` instead of BULL/SIDEWAYS/BEAR, and the decider zeroes the sizing automatically. The log shows explicitly "ABSTAIN: regime without playbook (OOD, conf=0.000). Sizing=0". No operating in the dark.

In practical terms: the agent now has three output options, not two. Operate with conviction. Wait with conviction. And now also admit it doesn't know.

## Why this matters more than chasing alpha

The common intuition is that adding an `OOD` class reduces trade frequency and therefore return. True. In historical backtest, I can cut the number of operations by some percentage.

But the trade I skipped was a trade taken in a state of model confusion. Capital preservation first, remember? Each time the system abstains, it gives me time to manually inspect what's happening. It could be a flash crash, a macro regime change, a feature ingestion error. In all cases, I'd rather have the system stopped than fabricating a decision I later couldn't explain.

The rule ended up being: if the model leaves the comfort of the distribution it has seen, it calls me. And I decide whether to replace the abstention with a manual intervention, or accept that this isn't a moment to operate.

This doesn't replace improving the model. It's just the honest recognition that no 3-state model with 8 features will cover every possible regime of a market that has adoption cycles, macro events, halvings, and regulatory changes.

## The next chapter

The current version accepts a single OOD criterion (absolute z-score). I already have two extensions in mind: Mahalanobis distance in the full space (captures correlations z-score misses) and tick likelihood under the trained HMM (more sensitive, more expensive). Both in backlog.

For now, what's in production is the simple version. And it has already changed my sleep.

Have you ever had a model return high confidence on a decision that shouldn't have been made? Tell me on [LinkedIn](https://linkedin.com/in/thaisvaz) or subscribe to the [newsletter](https://vazdeng.substack.com) to get the next posts.
