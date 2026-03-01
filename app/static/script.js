async function callApi(path, method = 'GET', body = null) {
  const opts = { method, headers: {} };
  if (body !== null) {
    opts.headers['Content-Type'] = 'application/json';
    opts.body = JSON.stringify(body);
  }
  const res = await fetch(path, opts);
  return res.json();
}

const fmt = (n, d = 1) => Number(n ?? 0).toFixed(d);
const fmtPct = (n) => `${(Number(n ?? 0) * 100).toFixed(1)}%`;
const fmtToken = (n) => fmt(n, 1);
const fmtMoney = (n) => fmt(n, 1);

function setText(id, value) {
  document.getElementById(id).textContent = value;
}

function setDisabled(id, isDisabled) {
  document.getElementById(id).disabled = isDisabled;
}

function renderEventLog(events) {
  const root = document.getElementById('eventLog');
  if (!events || events.length === 0) {
    root.innerHTML = '<li>-</li>';
    return;
  }

  root.innerHTML = '';
  const latestFirst = [...events].reverse();
  for (const evt of latestFirst) {
    const li = document.createElement('li');
    li.textContent = evt;
    root.appendChild(li);
  }
}

function logGamma(z) {
  const c = [
    676.5203681218851,
    -1259.1392167224028,
    771.32342877765313,
    -176.61502916214059,
    12.507343278686905,
    -0.13857109526572012,
    9.9843695780195716e-6,
    1.5056327351493116e-7,
  ];

  if (z < 0.5) {
    return Math.log(Math.PI) - Math.log(Math.sin(Math.PI * z)) - logGamma(1 - z);
  }

  let x = 0.99999999999980993;
  const t = z - 1;
  for (let i = 0; i < c.length; i += 1) {
    x += c[i] / (t + i + 1);
  }

  const g = 7;
  const y = t + g + 0.5;
  return 0.5 * Math.log(2 * Math.PI) + (t + 0.5) * Math.log(y) - y + Math.log(x);
}

function betaPdf(x, a, b) {
  if (x <= 0 || x >= 1) {
    return 0;
  }

  const logBeta = logGamma(a) + logGamma(b) - logGamma(a + b);
  const logPdf = (a - 1) * Math.log(x) + (b - 1) * Math.log(1 - x) - logBeta;
  return Math.exp(logPdf);
}

function buildPath(xs, ys, xMin, xMax, yMax, plotBox) {
  const { left, top, width, height } = plotBox;
  let d = '';

  for (let i = 0; i < xs.length; i += 1) {
    const x = left + ((xs[i] - xMin) / (xMax - xMin)) * width;
    const y = top + height - (ys[i] / yMax) * height;
    d += `${i === 0 ? 'M' : ' L'}${x.toFixed(2)} ${y.toFixed(2)}`;
  }

  return d;
}

function renderAlgo2Distribution(headCount, tailCount) {
  const alphaHeads = headCount + 1;
  const betaHeads = tailCount + 1;
  const alphaTails = tailCount + 1;
  const betaTails = headCount + 1;

  const points = 140;
  const eps = 1e-3;
  const xs = [];
  const headsYs = [];
  const tailsYs = [];

  for (let i = 0; i < points; i += 1) {
    const x = eps + (i / (points - 1)) * (1 - 2 * eps);
    xs.push(x);
    headsYs.push(betaPdf(x, alphaHeads, betaHeads));
    tailsYs.push(betaPdf(x, alphaTails, betaTails));
  }

  const yMax = Math.max(...headsYs, ...tailsYs, 1e-12);
  const plotBox = { left: 55, top: 20, width: 480, height: 215 };

  const headsPath = buildPath(xs, headsYs, 0, 1, yMax, plotBox);
  const tailsPath = buildPath(xs, tailsYs, 0, 1, yMax, plotBox);

  document.getElementById('algo2HeadPdfPath').setAttribute('d', headsPath);
  document.getElementById('algo2TailPdfPath').setAttribute('d', tailsPath);
}

function renderAlgorithm(prefix, data) {
  setText(`${prefix}BalanceHeads`, fmtToken(data.balances.heads));
  setText(`${prefix}BalanceTails`, fmtToken(data.balances.tails));
  setText(`${prefix}BalanceMoney`, fmtMoney(data.balances.money));

  setText(`${prefix}BuyStakeHeads`, fmtMoney(data.trades.heads.buy.stake));
  setText(`${prefix}BuyTokensHeads`, fmtToken(data.trades.heads.buy.tokens));
  setText(`${prefix}SellMoneyHeads`, fmtMoney(data.trades.heads.sell.money));
  setText(`${prefix}SellTokensHeads`, fmtToken(data.trades.heads.sell.tokens));

  setText(`${prefix}BuyStakeTails`, fmtMoney(data.trades.tails.buy.stake));
  setText(`${prefix}BuyTokensTails`, fmtToken(data.trades.tails.buy.tokens));
  setText(`${prefix}SellMoneyTails`, fmtMoney(data.trades.tails.sell.money));
  setText(`${prefix}SellTokensTails`, fmtToken(data.trades.tails.sell.tokens));

  setDisabled(`${prefix}BuyHeadsBtn`, data.trades.heads.buy.stake <= 0);
  setDisabled(`${prefix}BuyTailsBtn`, data.trades.tails.buy.stake <= 0);
  setDisabled(`${prefix}SellHeadsBtn`, data.trades.heads.sell.tokens <= 0);
  setDisabled(`${prefix}SellTailsBtn`, data.trades.tails.sell.tokens <= 0);
}

function render(state) {
  setText('coinActualHeads', fmtPct(state.coin.actual_probability.heads));
  setText('coinActualTails', fmtPct(state.coin.actual_probability.tails));
  setText('coinActualSum', fmtPct(state.coin.actual_probability.sum));

  setText('coinCountHeads', state.coin.occurrence_count.heads);
  setText('coinCountTails', state.coin.occurrence_count.tails);
  setText('coinCountSum', state.coin.occurrence_count.sum);

  setText('coinImpliedHeads', fmtPct(state.coin.implied_probability.heads));
  setText('coinImpliedTails', fmtPct(state.coin.implied_probability.tails));
  setText('coinImpliedSum', fmtPct(state.coin.implied_probability.sum));
  setText('tossOutcome', state.last_toss_outcome || '-');

  setText('marketPriceHeads', fmtPct(state.market.prices.heads));
  setText('marketPriceTails', fmtPct(state.market.prices.tails));
  setText('marketDerivativeHeads', '-');
  setText('marketDerivativeTails', '-');

  setText('marketBalanceHeads', fmtToken(state.market.balances.heads));
  setText('marketBalanceTails', fmtToken(state.market.balances.tails));
  setText('marketBalanceMoney', fmtMoney(state.market.balances.money));

  renderAlgorithm('algo1', state.algorithm1);
  renderAlgorithm('algo2', state.algorithm2);

  setText('algo1EstHeads', fmtPct(state.algorithm1.estimate.heads));
  setText('algo1EstTails', fmtPct(state.algorithm1.estimate.tails));

  renderAlgo2Distribution(state.coin.occurrence_count.heads, state.coin.occurrence_count.tails);

  setText('mmBalanceHeads', fmtToken(state.market_maker.balances.heads));
  setText('mmBalanceTails', fmtToken(state.market_maker.balances.tails));
  setText('mmBalanceMoney', fmtMoney(state.market_maker.balances.money));

  renderEventLog(state.event_log || []);
}

async function refresh() {
  render(await callApi('/api/state'));
}

async function trade(algo, side, action) {
  render(await callApi('/api/trade', 'POST', { algo, side, action }));
}

document.getElementById('resetBtn').addEventListener('click', async () => {
  render(await callApi('/api/reset', 'POST'));
});

document.getElementById('testTossBtn').addEventListener('click', async () => {
  render(await callApi('/api/test-toss', 'POST'));
});

document.getElementById('eventTossBtn').addEventListener('click', async () => {
  render(await callApi('/api/event-toss', 'POST'));
});

document.getElementById('algo1BuyHeadsBtn').addEventListener('click', () => trade('algo1', 'heads', 'buy'));
document.getElementById('algo1BuyTailsBtn').addEventListener('click', () => trade('algo1', 'tails', 'buy'));
document.getElementById('algo1SellHeadsBtn').addEventListener('click', () => trade('algo1', 'heads', 'sell'));
document.getElementById('algo1SellTailsBtn').addEventListener('click', () => trade('algo1', 'tails', 'sell'));

document.getElementById('algo2BuyHeadsBtn').addEventListener('click', () => trade('algo2', 'heads', 'buy'));
document.getElementById('algo2BuyTailsBtn').addEventListener('click', () => trade('algo2', 'tails', 'buy'));
document.getElementById('algo2SellHeadsBtn').addEventListener('click', () => trade('algo2', 'heads', 'sell'));
document.getElementById('algo2SellTailsBtn').addEventListener('click', () => trade('algo2', 'tails', 'sell'));

refresh();
