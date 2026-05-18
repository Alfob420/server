"use strict";

const log = document.getElementById("log");
const form = document.getElementById("form");
const input = document.getElementById("input");
const button = form.querySelector("button");
const statusEl = document.getElementById("status");

function addMessage(kind, who, text, sources) {
  const el = document.createElement("div");
  el.className = `msg msg--${kind}`;

  const whoEl = document.createElement("span");
  whoEl.className = "who";
  whoEl.textContent = who;
  el.appendChild(whoEl);

  const p = document.createElement("p");
  p.textContent = text;
  el.appendChild(p);

  if (sources && sources.length) {
    const s = document.createElement("div");
    s.className = "sources";
    s.textContent = "fuentes: " + sources.join(", ");
    el.appendChild(s);
  }

  log.appendChild(el);
  log.scrollTop = log.scrollHeight;
}

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

form.addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const message = input.value.trim();
  if (!message) return;

  addMessage("user", "VOS", message);
  input.value = "";
  button.disabled = true;

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ message }),
    });
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    addMessage("bot", `NODO · ${data.model}`, data.reply, data.sources);
  } catch (err) {
    addMessage("sys", "ERROR", String(err));
  } finally {
    button.disabled = false;
    input.focus();
  }
});

refreshStatus();
setInterval(refreshStatus, 10000);
