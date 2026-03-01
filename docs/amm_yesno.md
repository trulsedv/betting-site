## A trade in an yes/no-AMM-market

A bettor makes a bet on an outcome happing with a stake $m$ money-tokens and recieves tokens $y$ yes-tokens for that outcome. The balances of the market and the bettor then change as follows.

| Token | Bettor before| Bettor after | Market before | Market after|
|-|-|-|-|-|
| Money | $M_b$ | $M_b - m$ | $M_m$ | $M_m + m$ |
| Yes | $Y_b$ | $Y_b + y$ | $Y_m$ | $Y_m + m - y$ |
| No | $N_b$ | $N_b$ | $N_m$ | $N_m + m$ |

Note that there is created $m$ yes-tokens and no-tokens in the market when the market recieves $m$ money-tokens. Then the market withdraw $y$ yes-tokens for the bettor.

### How many tokens is recieved?

The AMM in this example has a constant product. Meaning the product of the balance of yes-tokens and no-tokens in the market must always be constant.

$$ Y \cdot N = K $$

$$ Y_0 \cdot N_0 = Y_1 \cdot N_1 $$

$$ Y_0 \cdot N_0 = (Y_0 + m -y) \cdot (N_0 + m) $$

$$ y = Y_0 + m - \frac{Y_0 \cdot N_0}{N_0 + m} $$

## No-bet example

A bettor makes a bet on an outcome not happing with a stake $m$ money-tokens and recieves tokens $n$ no-tokens for that outcome. The balances of the market and the bettor then change as follows.

| Token | Bettor before| Bettor after | Market before | Market after|
|-|-|-|-|-|
| Money | $M_b$ | $M_b - m$ | $M_m$ | $M_m + m$ |
| Yes | $Y_b$ | $Y_b$ | $Y_m$ | $Y_m + m$ |
| No | $N_b$ | $N_b + n$ | $N_m$ | $N_m + m - n$ |

The amount of no-tokens recieved is given by the following equation.

$$ Y_0 \cdot N_0 = (Y_0 + m) \cdot (N_0 + m - n) $$

$$ n = N_0 + m - \frac{Y_0 \cdot N_0}{Y_0 + m} $$

## Selling yes-token example

A bettor sells $y$ yes-tokens and recieved $m$ money tokens.

| Token | Bettor before| Bettor after | Market before | Market after|
|-|-|-|-|-|
| Money | $M_b$ | $M_b + m$ | $M_m$ | $M_m - m$ |
| Yes | $Y_b$ | $Y_b - y$ | $Y_m$ | $Y_m - m + y$ |
| No | $N_b$ | $N_b$ | $N_m$ | $N_m - m$ |

$$ Y_0 \cdot N_0 = (Y_0 - m + y) \cdot (N_0 - m) $$

$$ m = \frac{(Y_0 + N_0 + y) - \sqrt{(Y_0 + N_0 + y)^2 - 4 y N_0}}{2} $$

*Note that it is not $\pm$ in the quadratic equation above. Pluss would yield a solution where both $Y_1$ and $N_1$ are negative.*

Note that this is the reverse of the first trade and buying (placing a bet) $y$ yes-tokens then selling $y$ yes-tokens right after will result in an unchanged market, and the bettor will get the moeny back. Ff other trades have happend inbetween this might to be true of course since the market has changed. So if $y_{buy} = y_{sell}$, subscript 0 is before buying, 1 is after buying (before selling), and 2 is after selling.

$$ Y_0 \cdot N_0 = (Y_1 - m_{sell} + y_{sell}) \cdot (N_1 - m_{sell}) $$

$$ Y_0 \cdot N_0 = ((Y_0 + m_{buy} - y_{buy}) - m_{sell} + y_{sell}) \cdot ((N_0 + m_{buy}) - m_{sell}) $$

$$ Y_0 \cdot N_0 = (Y_0 + m_{buy} - y_{buy} - m_{sell} + y_{buy}) \cdot (N_0 + m_{buy} - m_{sell}) $$

$$ Y_0 \cdot N_0 = (Y_0 + m_{buy} - m_{sell}) \cdot (N_0 + m_{buy} - m_{sell}) $$

This can only be true if $m_{buy} = m_{sell}$.