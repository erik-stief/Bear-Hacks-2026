const listEl = document.getElementById("list");
const loginBtn = document.getElementById("login");
const refreshBtn = document.getElementById("refresh");

loginBtn.addEventListener("click", async () => {
  const resp = await chrome.runtime.sendMessage({ type: "PT_LOGIN" });
  if (resp?.ok) await loadList();
});

refreshBtn.addEventListener("click", () => loadList());

async function loadList() {
  listEl.innerHTML = "<li>Analyzing Inbox...</li>";

  const msgs = await chrome.runtime.sendMessage({ type: "PT_LIST_MESSAGES" });
  if (!msgs?.ok) {
    listEl.innerHTML = "<li>Connect Gmail to start scanning.</li>";
    return;
  }

  const rows = await Promise.all(
    (msgs.items || []).map(async (m) => {
      const scored = await chrome.runtime.sendMessage({ type: "PT_FETCH_AND_SCORE", id: m.id });
      if (!scored?.ok) return null;

      const { parsed, score, rawHeaders } = scored;

      // SECONDARY SCAN: If Risk is Mid or High, print and POST headers
      if (score.risk.css === "mid" || score.risk.css === "high") {
        chrome.runtime.sendMessage({
          type: "PT_COLLECT_HEADERS",
          id: m.id,
          headers: rawHeaders
        });
      }

      return {
        id: m.id,
        from: parsed.from,
        subject: parsed.subject,
        score: score.score,
        risk: score.risk,
        reasons: score.reasons
      };
    })
  );

  listEl.innerHTML = "";
  rows.filter(Boolean).forEach(row => {
    const li = document.createElement("li");
    li.className = "item";
    const reasons = row.reasons.length > 0 ? row.reasons.join(" • ") : "No forensic flags";
    
    li.innerHTML = `
      <div class="meta">
        ${row.from} <span class="score ${row.risk.css}">${Math.round(row.score)} (${row.risk.label})</span>
      </div>
      <div class="subj">${row.subject}</div>
      <div class="reasons">${reasons}</div>
    `;
    listEl.appendChild(li);
  });
}

if (self.PT_CONFIG?.AUTO_SCAN_ON_OPEN) {
    loadList();
}