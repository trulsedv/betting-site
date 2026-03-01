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
  setText('algo2EstHeads', fmtPct(state.algorithm2.estimate.heads));
  setText('algo2EstTails', fmtPct(state.algorithm2.estimate.tails));

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
