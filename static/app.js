const SUIT_SYMBOL = { h: "♥", d: "♦", c: "♣", s: "♠" };
const RED_SUITS = new Set(["h", "d"]);
const RANK_DISPLAY = { T: "10" };

function cardEl(label) {
  const rank = label[0];
  const suit = label[1];
  const el = document.createElement("div");
  el.className = "playing-card" + (RED_SUITS.has(suit) ? " red" : "");
  el.innerHTML = `<div class="rank">${RANK_DISPLAY[rank] || rank}</div><div class="suit">${SUIT_SYMBOL[suit] || suit}</div>`;
  return el;
}

function placeholderEl() {
  const el = document.createElement("div");
  el.className = "playing-card placeholder";
  return el;
}

function renderCards(containerId, cards, slotCount) {
  const container = document.getElementById(containerId);
  container.innerHTML = "";
  for (let i = 0; i < slotCount; i++) {
    container.appendChild(i < cards.length ? cardEl(cards[i]) : placeholderEl());
  }
}

function renderSeats(seats) {
  const container = document.getElementById("seats");
  container.innerHTML = "";
  seats
    .slice()
    .sort((a, b) => a.seat - b.seat)
    .forEach((s) => {
      const el = document.createElement("div");
      el.className = "seat";
      const stack = s.stack != null ? s.stack.toLocaleString("pt-PT") : "?";
      const blind = s.blind != null ? s.blind.toLocaleString("pt-PT") : "?";
      el.innerHTML = `
        <div class="seat-label">Seat ${s.seat}</div>
        <div class="seat-values">
          <span class="stack">${stack}</span>
          <span class="blind">blind ${blind}</span>
        </div>`;
      container.appendChild(el);
    });
}

function setStatus(ok, message) {
  const el = document.getElementById("status");
  el.textContent = message;
  el.className = "status " + (ok ? "ok" : "error");
}

async function poll() {
  try {
    const res = await fetch("/api/state", { cache: "no-store" });
    const data = await res.json();

    if (data.error) {
      setStatus(false, data.error);
    } else {
      setStatus(true, "em direto");
    }

    renderCards("hole", data.hole_cards || [], 2);
    renderCards("board", data.board_cards || [], 5);
    renderSeats(data.seats || []);

    const banner = document.getElementById("hand-banner");
    banner.textContent = data.hand || "--";
  } catch (err) {
    setStatus(false, "sem ligação ao servidor");
  }
}

poll();
setInterval(poll, 1000);
