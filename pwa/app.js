"use strict";

// --- utilidades ------------------------------------------------------------
function el(id) { return document.getElementById(id); }

function addMessage(logEl, kind, who, text, sources) {
  const node = document.createElement("div");
  node.className = `msg msg--${kind}`;

  const whoEl = document.createElement("span");
  whoEl.className = "who";
  whoEl.textContent = who;
  node.appendChild(whoEl);

  const p = document.createElement("p");
  p.textContent = text;
  node.appendChild(p);

  if (sources && sources.length) {
    const s = document.createElement("div");
    s.className = "sources";
    s.textContent = "fuentes: " + sources.join(", ");
    node.appendChild(s);
  }

  logEl.appendChild(node);
  logEl.scrollTop = logEl.scrollHeight;
}

async function postJSON(url, body) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

// --- pestañas --------------------------------------------------------------
document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((t) => t.classList.remove("tab--active"));
    document.querySelectorAll(".view").forEach((v) => v.classList.remove("view--active"));
    tab.classList.add("tab--active");
    el("view-" + tab.dataset.view).classList.add("view--active");
  });
});

// --- estado / health -------------------------------------------------------
const statusEl = el("status");

async function refreshStatus() {
  try {
    const res = await fetch("/api/health");
    const data = await res.json();
    statusEl.textContent = `● ONLINE · ${data.llm}`;
    statusEl.className = "status status--up";
  } catch {
    statusEl.textContent = "● OFFLINE";
    statusEl.className = "status status--down";
  }
}

// --- vista asistente (LLM + RAG) ------------------------------------------
const chatForm = el("chat-form");
const chatInput = el("chat-input");
const chatLog = el("log");

chatForm.addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const message = chatInput.value.trim();
  if (!message) return;

  addMessage(chatLog, "user", "VOS", message);
  chatInput.value = "";
  const btn = chatForm.querySelector("button");
  btn.disabled = true;

  try {
    const data = await postJSON("/api/chat", { message });
    addMessage(chatLog, "bot", `NODO · ${data.model}`, data.reply, data.sources);
  } catch (err) {
    addMessage(chatLog, "sys", "ERROR", String(err));
  } finally {
    btn.disabled = false;
    chatInput.focus();
  }
});

// --- vista mesh ------------------------------------------------------------
const meshForm = el("mesh-form");
const meshTo = el("mesh-to");
const meshText = el("mesh-text");
const meshLog = el("mesh-log");
let lastInboxId = 0;

async function refreshMesh() {
  try {
    const status = await (await fetch("/api/mesh/status")).json();
    el("mesh-name").textContent = status.name || "—";
    el("mesh-addr").textContent = status.address || "—";
  } catch {
    el("mesh-addr").textContent = "servicio mesh no disponible";
  }

  try {
    const peers = await (await fetch("/api/mesh/peers")).json();
    renderPeers(peers);
  } catch {
    renderPeers([]);
  }

  try {
    const msgs = await (await fetch(`/api/mesh/inbox?since=${lastInboxId}`)).json();
    for (const m of msgs) {
      lastInboxId = Math.max(lastInboxId, m.id);
      const who = `${m.name || "desconocido"} · ${m.from.slice(0, 12)}`;
      addMessage(meshLog, "bot", who, m.text);
    }
  } catch {
    /* servicio mesh caído: se reintenta en el próximo ciclo */
  }
}

function renderPeers(peers) {
  el("peer-count").textContent = peers.length;
  const list = el("peer-list");
  list.innerHTML = "";
  if (!peers.length) {
    const li = document.createElement("li");
    li.className = "peer-empty";
    li.textContent = "Ningún nodo a la vista todavía.";
    list.appendChild(li);
    return;
  }
  for (const p of peers) {
    const li = document.createElement("li");
    const name = document.createElement("div");
    name.className = "peer-name";
    name.textContent = p.name || "(sin nombre)";
    const addr = document.createElement("div");
    addr.className = "peer-addr";
    addr.textContent = p.address;
    li.appendChild(name);
    li.appendChild(addr);
    li.addEventListener("click", () => {
      meshTo.value = p.address;
      meshText.focus();
    });
    list.appendChild(li);
  }
}

meshForm.addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const to = meshTo.value.trim();
  const text = meshText.value.trim();
  if (!to || !text) return;

  const btn = meshForm.querySelector("button");
  btn.disabled = true;
  try {
    await postJSON("/api/mesh/send", { to, text });
    addMessage(meshLog, "user", `VOS → ${to.slice(0, 12)}`, text);
    meshText.value = "";
  } catch (err) {
    addMessage(meshLog, "sys", "ERROR", String(err));
  } finally {
    btn.disabled = false;
    meshText.focus();
  }
});

// --- ciclos de actualización ----------------------------------------------
refreshStatus();
refreshMesh();
setInterval(refreshStatus, 10000);
setInterval(refreshMesh, 5000);
