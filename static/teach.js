const CARD_REGION_ORDER = ["hole_1", "hole_2", "board_1", "board_2", "board_3", "board_4", "board_5"];

let names = [];
let index = 0;

const img = document.getElementById("crop");
const labelInput = document.getElementById("label-input");
const msg = document.getElementById("msg");

function humanize(name) {
  if (name === "hole_1") return "A tua 1ª carta";
  if (name === "hole_2") return "A tua 2ª carta";
  const board = name.match(/^board_(\d)$/);
  if (board) return `Carta comunitária ${board[1]}`;
  return name;
}

function setMsg(text, isError = true) {
  msg.textContent = text;
  msg.style.color = isError ? "var(--warn)" : "var(--good)";
}

async function loadCrop() {
  const name = names[index];
  try {
    const res = await fetch(`/api/card-crop?region=${encodeURIComponent(name)}`, { cache: "no-store" });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      setMsg(data.error || "Não consegui capturar esta carta.");
      img.removeAttribute("src");
      return;
    }
    const blob = await res.blob();
    img.src = URL.createObjectURL(blob);
  } catch (err) {
    setMsg("Sem ligação ao servidor.");
  }
}

function showStep() {
  const name = names[index];
  document.getElementById("region-title").textContent = humanize(name);
  document.getElementById("progress").textContent = `${index + 1} / ${names.length} — (${name})`;
  document.getElementById("back-btn").disabled = index === 0;
  labelInput.value = "";
  setMsg("", false);
  loadCrop();
  labelInput.focus();
}

function advance() {
  index = (index + 1) % names.length;
  if (index === 0) {
    setMsg("Ciclo completo — continua na próxima mão para ensinar mais cartas.", false);
  }
  showStep();
}

document.getElementById("save-btn").addEventListener("click", async () => {
  const label = labelInput.value.trim();
  const name = names[index];
  if (!/^[2-9TJQKA][hdcs]$/.test(label)) {
    setMsg("Etiqueta inválida. Usa rank+naipe, ex: Ah, Td, 9s.");
    return;
  }
  try {
    const res = await fetch("/api/teach", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ region: name, label }),
    });
    const data = await res.json();
    if (!res.ok) {
      setMsg(data.error || "Erro ao guardar.");
      return;
    }
    setMsg(`Guardado: ${data.label}`, false);
    setTimeout(advance, 400);
  } catch (err) {
    setMsg("Sem ligação ao servidor.");
  }
});

labelInput.addEventListener("keydown", (evt) => {
  if (evt.key === "Enter") document.getElementById("save-btn").click();
});

document.getElementById("skip-btn").addEventListener("click", advance);
document.getElementById("recapture-btn").addEventListener("click", loadCrop);
document.getElementById("back-btn").addEventListener("click", () => {
  if (index > 0) {
    index -= 1;
    showStep();
  }
});

(async function init() {
  let regions = {};
  try {
    const res = await fetch("/api/regions");
    regions = await res.json();
  } catch (err) {
    setMsg("Sem ligação ao servidor.");
    return;
  }

  names = CARD_REGION_ORDER.filter((n) => n in regions);
  if (names.length === 0) {
    document.querySelector(".tool-card").innerHTML =
      '<h2>Ainda não há regiões calibradas</h2><p class="hint">Vai primeiro a <a href="/calibrate">Calibrar</a> para definires onde ficam as cartas.</p>';
    return;
  }
  showStep();
})();
