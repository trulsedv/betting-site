// Connect to WebSocket
const ws = new WebSocket("ws://localhost:8000/ws");

// Update UI with real-time data
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    document.getElementById("home-price").textContent = data.prices.Home;
    document.getElementById("draw-price").textContent = data.prices.Draw;
    document.getElementById("away-price").textContent = data.prices.Away;
    document.getElementById("user-tokens").textContent = data.tokens.user;
    document.getElementById("algorithm-tokens").textContent = data.tokens.algorithm;
};

// Place a bet
document.getElementById("bet-form").addEventListener("submit", (e) => {
    e.preventDefault();
    const outcome = document.getElementById("outcome").value;
    const stake = document.getElementById("stake").value;
    ws.send(JSON.parse({ outcome, stake }));
});
