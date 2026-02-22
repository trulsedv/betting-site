async function callApi(path, method = 'GET') {
  const res = await fetch(path, { method });
  return res.json();
}

const fmt = (n, d = 4) => Number(n).toFixed(d);

function render(state) {
  document.getElementById('trueP').textContent = fmt(state.true_p_heads, 4);
  document.getElementById('heads').textContent = state.heads;
  document.getElementById('tails').textContent = state.tails;
  document.getElementById('flipIndex').textContent = state.flip_index;
  document.getElementById('phase').textContent = state.phase;
  document.getElementById('nextBettor').textContent = state.next_bettor;
  document.getElementById('ammImpP').textContent = state.amm_implied_p_heads?.toFixed(4) || '-';
  document.getElementById('algo1Est').textContent = state.algo1_estimate?.toFixed(4) || '-';
  document.getElementById('algo2Est').textContent = state.algo2_estimate?.toFixed(4) || '-';

  document.getElementById('bank1').textContent = fmt(state.bankroll.algo1, 2);
  document.getElementById('bank2').textContent = fmt(state.bankroll.algo2, 2);

  document.getElementById('ammHead').textContent = fmt(state.amm.head, 2);
  document.getElementById('ammTail').textContent = fmt(state.amm.tail, 2);
  document.getElementById('bets').textContent = JSON.stringify(state.pending_bets, null, 2);
  document.getElementById('last').textContent = state.last_result || '-';
}

async function refresh() {
  render(await callApi('/api/state'));
}

document.getElementById('nextBetBtn').addEventListener('click', async () => {
  render(await callApi('/api/next-bet', 'POST'));
});

document.getElementById('flipCoinBtn').addEventListener('click', async () => {
  render(await callApi('/api/flip-coin', 'POST'));
});

document.getElementById('newCoinBtn').addEventListener('click', async () => {
  render(await callApi('/api/new-coin', 'POST'));
});

refresh();
