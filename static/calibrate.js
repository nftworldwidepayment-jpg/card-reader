let names = [];
let index = 0;
let regions = {}; // name -> [x, y, w, h] in screenshot pixel coordinates
let pendingBox = null;
let drag = null; // { startX, startY }

const img = document.getElementById("screenshot");
const canvas = document.getElementById("overlay");
const ctx = canvas.getContext("2d");

function humanize(name) {
  if (name === "hole_1") return "A tua 1ª carta";
  if (name === "hole_2") return "A tua 2ª carta";
  const board = name.match(/^board_(\d)$/);
  if (board) return `Carta comunitária ${board[1]}`;
  const stack = name.match(/^seat(\d+)_stack$/);
  if (stack) return `Seat ${stack[1]} — stack (fichas)`;
  const blind = name.match(/^seat(\d+)_blind$/);
  if (blind) return `Seat ${blind[1]} — blind`;
  return name;
}

function buildNames(numSeats) {
  const list = ["hole_1", "hole_2", "board_1", "board_2", "board_3", "board_4", "board_5"];
  for (let s = 1; s <= numSeats; s++) {
    list.push(`seat${s}_stack`, `seat${s}_blind`);
  }
  return list;
}

function drawBox(box, color) {
  if (!box) return;
  const [x, y, w, h] = box;
  ctx.strokeStyle = color;
  ctx.lineWidth = Math.max(2, canvas.width * 0.003);
  ctx.strokeRect(x, y, w, h);
}

function redraw() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  const name = names[index];
  if (regions[name]) drawBox(regions[name], "#93a1b8"); // existing (dim)
  if (pendingBox) drawBox(pendingBox, "#f2b84b"); // new (accent)
}

function canvasPoint(evt) {
  const rect = canvas.getBoundingClientRect();
  const scaleX = canvas.width / rect.width;
  const scaleY = canvas.height / rect.height;
  return {
    x: (evt.clientX - rect.left) * scaleX,
    y: (evt.clientY - rect.top) * scaleY,
  };
}

canvas.addEventListener("mousedown", (evt) => {
  const p = canvasPoint(evt);
  drag = { startX: p.x, startY: p.y };
  pendingBox = [p.x, p.y, 0, 0];
});

canvas.addEventListener("mousemove", (evt) => {
  if (!drag) return;
  const p = canvasPoint(evt);
  const x = Math.min(drag.startX, p.x);
  const y = Math.min(drag.startY, p.y);
  const w = Math.abs(p.x - drag.startX);
  const h = Math.abs(p.y - drag.startY);
  pendingBox = [x, y, w, h];
  redraw();
});

window.addEventListener("mouseup", () => {
  drag = null;
});

async function loadScreenshot() {
  document.getElementById("calib-error").textContent = "";
  try {
    const res = await fetch("/api/screenshot", { cache: "no-store" });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      document.getElementById("calib-error").textContent = data.error || "Não consegui capturar o ecrã.";
      return;
    }
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    await new Promise((resolve) => {
      img.onload = resolve;
      img.src = url;
    });
    canvas.width = img.naturalWidth;
    canvas.height = img.naturalHeight;
    pendingBox = null;
    redraw();
  } catch (err) {
    document.getElementById("calib-error").textContent = "Sem ligação ao servidor.";
  }
}

function showStep() {
  const name = names[index];
  document.getElementById("region-title").textContent = humanize(name);
  document.getElementById("progress").textContent = `${index + 1} / ${names.length} — (${name})`;
  document.getElementById("back-btn").disabled = index === 0;
  pendingBox = null;
  redraw();
}

async function finish() {
  document.getElementById("calibrator").classList.add("hidden");
  const res = await fetch("/api/regions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ regions }),
  });
  if (res.ok) {
    document.getElementById("done").classList.remove("hidden");
  } else {
    document.getElementById("calibrator").classList.remove("hidden");
    document.getElementById("calib-error").textContent = "Erro ao guardar. Tenta novamente.";
  }
}

document.getElementById("confirm-btn").addEventListener("click", () => {
  const name = names[index];
  if (pendingBox && pendingBox[2] > 3 && pendingBox[3] > 3) {
    regions[name] = pendingBox.map((v) => Math.round(v));
  }
  if (!regions[name]) {
    document.getElementById("calib-error").textContent = "Desenha um retângulo antes de confirmar (ou usa Saltar).";
    return;
  }
  advance();
});

document.getElementById("skip-btn").addEventListener("click", () => advance());

document.getElementById("back-btn").addEventListener("click", () => {
  if (index > 0) {
    index -= 1;
    showStep();
  }
});

document.getElementById("recapture-btn").addEventListener("click", () => loadScreenshot());

function advance() {
  if (index < names.length - 1) {
    index += 1;
    showStep();
    loadScreenshot();
  } else {
    finish();
  }
}

document.getElementById("start-btn").addEventListener("click", async () => {
  const numSeats = parseInt(document.getElementById("num-seats").value, 10) || 6;
  names = buildNames(numSeats);
  index = 0;

  try {
    const res = await fetch("/api/regions");
    regions = await res.json();
  } catch (err) {
    regions = {};
  }

  document.getElementById("setup").classList.add("hidden");
  document.getElementById("calibrator").classList.remove("hidden");
  showStep();
  await loadScreenshot();
});
