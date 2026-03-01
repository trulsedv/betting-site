## Kelly criterion

The Kelly criterion give the fraction $f^*$ of the current bankroll to wager given the odds $b$ and your estimation of the probability of a win $p$.

$$ f^* = p - \frac{1 - p}{b} $$

Here the odds $b$ are given as profit over stake (profit = payout - stake). Using decimal odds $B$, payout over stake, the equation become as below.

$$ f^* = p - \frac{1 - p}{B - 1} $$

Using prediction market price $P$ (implied probability), which it one over decimal odds.

$$ f^* = p - \frac{1 - p}{\frac{1}{P} - 1} $$

## Kelly criterion with constant product AMM

In a market with an Automated Marked Maker the price/odds will change with the size of the stake. Staking $m$ money-tokens on an outcome happening will give the bettor $y$ yes-tokens.

$$ y = Y_0 + m - \frac{Y_0 \cdot N_0}{N_0 + m} $$

Here $Y_0$ and $N_0$ are the balance of yes-tokens and no-tokens in the market before the bet. A yes-token will give a payout of 1 money-tokens if the outcome happen. This yields the following odds.

$$ B = \frac{\mathrm{payout}}{\mathrm{stake}} = \frac{y}{m} = \frac{Y_0 + m - \frac{Y_0 \cdot N_0}{N_0 + m}}{m} $$

The optimal stake $m^* = f^*M$ can then be solved for.

$$ f^* = \frac{m^*}{M} = p - \frac{1 - p}{\frac{Y_0 + m^* - \frac{Y_0 \cdot N_0}{N_0 + m^*}}{m^*} - 1} $$


$$ m^* = \frac{p Y_0 - (1 - p) N_0}{\frac{Y_0}{M} + (1 - p)} $$
