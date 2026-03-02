## Kelly criterion

The Kelly criterion give the fraction $f^*$ of the current bankroll to wager given the odds $b$ and your estimation of the probability of a win $p$.

$$ f^* = p - \frac{1 - p}{b} $$

Here the odds $b$ are given as profit over stake (profit = payout - stake). Using decimal odds $B$, payout over stake, the equation become as below.

$$ f^* = p - \frac{1 - p}{B - 1} $$

Using prediction market price $P$ (implied probability), which it one over decimal odds.

$$ f^* = p - \frac{1 - p}{\frac{1}{P} - 1} $$

## Kelly criterion with constant product AMM

In a market with an Automated Marked Maker the price/odds will change with the size of the stake. Staking $m$ money-tokens on an outcome happening will give the bettor $y$ yes-tokens.

$$ y = m + Y_0 (1 - \frac{N_0}{N_0 + m}) $$

To avoid repeated bets the criterion also needs to account for aleady placed bets. If the bettor already have placed bets for $m_0$ money-tokens, and own $Y_b$ yes-tokens and $N_b$ no-tokens, a bet on yes with a yes outcome will yield the followng money-tokens after resolution.

$$ M_{b1y} = M_{b0} - m_0 + Y_b - m + y $$

While a no outcome will yield the following.

$$ M_{b1n} = M_{b0} - m_0 - N_b - m $$

Changing these equations into a fraction of $M_{b0}$.

$$ \frac{M_{b1y}}{M_{b0}} = 1 - \frac{m_0}{M_{b0}} + \frac{Y_b}{M_{b0}} - \frac{m}{M_{b0}} + \frac{y}{M_{b0}} = 1 + r_y $$

$$ \frac{M_{b1n}}{M_{b0}} = 1 - \frac{m_0}{M_{b0}} + \frac{N_b}{M_{b0}} - \frac{m}{M_{b0}} = 1 + r_n $$

Assuming these fractional bets could be reapeated with the same odds $N = \infty$ times the expected growth rate would be as follows.

$$ 1 + r = \left(\frac{M_{bNn}}{M_{b0}} \right)^{1/N} = \left(1 - \frac{m_0}{M_{b0}} + \frac{Y_b}{M_{b0}} - \frac{m}{M_{b0}} + \frac{y}{M_{b0}} \right)^{p} \left(1 - \frac{m_0}{M_{b0}} + \frac{N_b}{M_{b0}} - \frac{m}{M_{b0}} \right)^{1 - p} $$

This is what the Kelly criterion is able to maximize for a "simple" bet with a simple expression. This now become much more complex.

$$ m^* = \arg \max_{m} \, \left( \left(1 - \frac{m_0}{M_{b0}} + \frac{Y_b}{M_{b0}} - \frac{m}{M_{b0}} + \frac{m + Y_m (1 - \frac{N_m}{N_m + m})}{M_{b0}} \right)^{p} \left(1 - \frac{m_0}{M_{b0}} + \frac{N_b}{M_{b0}} - \frac{m}{M_{b0}} \right)^{1 - p} \right) $$

This has been solved by sympy (see docs/derivations).