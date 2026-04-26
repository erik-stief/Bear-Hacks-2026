const listEl = document.getElementById("list");
const loginBtn = document.getElementById("login");
const refreshBtn = document.getElementById("refresh");

loginBtn.addEventListener("click", async () => {
  const resp = await chrome.runtime.sendMessage({ type: "PT_LOGIN" });
  if (resp?.ok) await loadList();
});

refreshBtn.addEventListener("click", () => loadList());

function emptyTable(message) {
  return `<div class="table-wrapper"><table><tbody><tr><td colspan="3">${message}</td></tr></tbody></table></div>`;
}

async function loadList() {
  listEl.innerHTML = emptyTable("Analyzing Inbox...");

  const msgs = await chrome.runtime.sendMessage({ type: "PT_LIST_MESSAGES" });
  if (!msgs?.ok) {
    listEl.innerHTML = emptyTable("Connect Gmail to start scanning.");
    return;
  }

  const rows = await Promise.all(
    (msgs.items || []).map(async (m) => {
      const scored = await chrome.runtime.sendMessage({ type: "PT_FETCH_AND_SCORE", id: m.id });
      if (!scored?.ok) return null;

      const { parsed, score, rawHeaders } = scored;

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

  const filtered = rows.filter(Boolean);
  if (filtered.length === 0) {
    listEl.innerHTML = emptyTable("No emails found.");
    return;
  }

  const tbody = filtered.map(row => {
    const reasons = row.reasons.length > 0 ? row.reasons.join(" • ") : "No forensic flags";
    return `
      <tr>
        <td>
          <div class="from-cell">${row.from}</div>
          <div class="reasons">${reasons}</div>
        </td>
        <td class="subj">${row.subject}</td>
        <td><span class="score ${row.risk.css}">${Math.round(row.score)}<br><span class="risk-label">${row.risk.label}</span></span></td>
      </tr>`;
  }).join("");

  listEl.innerHTML = `
    <div class="table-wrapper">
      <table>
        <thead>
          <tr><th>From</th><th>Subject</th><th>Risk</th></tr>
        </thead>
        <tbody>${tbody}</tbody>
      </table>
    </div>`;
}

if (self.PT_CONFIG?.AUTO_SCAN_ON_OPEN) {
    loadList();
}