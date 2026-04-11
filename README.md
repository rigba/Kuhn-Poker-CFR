# Kuhn Poker CFR

A Python implementation of Counterfactual Regret Minimization (CFR) for Kuhn Poker, with a small command-line interface that lets a human play against the learnt strategy.
## Overview

This project trains a strategy for [Kuhn Poker](https://en.wikipedia.org/wiki/Kuhn_poker) using CFR, then allows the user to play repeated hands against the trained bot in the terminal.

The project was created with the purpose of touching up on python skills, aswell as an introduction to techniques for discovering Nash Equilibrium for imperfect information, zero sum games.
## Usage
Navigate to directory and run:
```py
python main.py
```
## Somewhat hand-wavey theoretical explanation as to how CFR is calculated and how it works
CFR is a learning algorithm that approximates a [Nash equilibrium](https://en.wikipedia.org/wiki/Nash_equilibrium) (roughly speaking: "the least exploitable strategy profile") by traversing the game tree at each information set $I$, comparing the expected utility of the current strategy $\sigma^{i}_{t}$ with the expected utility of a modified strategy $\sigma _{I\to a}$ that will always choose action $a$. This difference is accumulated as regrets, and then used to update the strategy assigning higher probabilities to actions which yielded higher regrets.  

Term definitions:
- $\sigma^{t}_{i}(I,a)$ : probability player $i$ takes action $a$ for information set $I$ at iteration $t$. 
- $h$ : a sequence of actions such as pass, bet, bet.
- $z\in Z$ : a terminal history of actions
- $\pi^{\sigma}(h)$ : the probability of reaching $h$ under strategy $\sigma$
- $\pi _{-i}^{\sigma}(h)$ : the probability of getting to history $h$ from everything except player $i$'s choices.
- $u_{i}(z)$: the utility for player $i$ reaching $z$ aka "the payout"

**Counterfactual Value at non terminal history $h$ of $z$**:

$$
v_{i}(\sigma,h)=\sum _{z\in Z,\ h\sqsubset z}\pi _{-i}^{\sigma}(h)\pi^{\sigma}(h, z)u_{i}(z)
$$

**Counterfactual Regret of not taking action $a$ at $h$**:

$$
r^{t}_{i}(h,a) = v_{i}(\sigma _{I\to a}^{t}, h)-v_{i}(\sigma^{t}, h)
$$

**Positive Cumulative Regret**:

$$
R^{T,+}_{i}(I,a)=\text{max}\left( \sum _{t=1}^{T}r_{i}^{t}(I,a), 0 \right)
$$

**Strategy Update**:

$$
\sigma_i^{T+1}(I,a)=
\begin{cases}
\dfrac{R_i^{T,+}(I,a)}{\sum_{a'\in A(I)} R_i^{T,+}(I,a')} & \text{if } \sum_{a'\in A(I)} R_i^{T,+}(I,a') > 0 \\
\dfrac{1}{|A(I)|} & \text{otherwise}
\end{cases}
$$

## Rounded approximation of the Nash equilibrium after $10^{6}$ training iterations
|Infoset|Pass probability|Bet probability|
|---|--:|--:|
|`1`|0.7900|0.2101|
|`2p`|0.9998|0.0002|
|`1pb`|1.0000|0.0000|
|`2b`|0.6671|0.3329|
|`2`|0.9998|0.0002|
|`3p`|0.0000|1.0000|
|`2pb`|0.4734|0.5266|
|`3b`|0.0000|1.0000|
|`3`|0.3772|0.6228|
|`1p`|0.6614|0.3386|
|`3pb`|0.0000|1.0000|
|`1b`|1.0000|0.0000|
