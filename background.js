// background.js
importScripts('config.js', 'gmail.js');

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === "PT_LOGIN") {
    chrome.identity.getAuthToken({ interactive: true }, (token) => {
      sendResponse({ ok: !chrome.runtime.lastError, token });
    });
    return true;
  }

  if (msg.type === "PT_LIST_MESSAGES") {
    chrome.identity.getAuthToken({ interactive: false }, async (token) => {
      try {
        const res = await fetch(`${self.PT_CONFIG.GMAIL_BASE_URL}/messages?maxResults=${self.PT_CONFIG.MAX_SCAN_RESULTS}`, {
          headers: self.PT_GMAIL.authHeaders(token)
        });
        const data = await res.json();
        sendResponse({ ok: true, items: data.messages || [] });
      } catch (e) { sendResponse({ ok: false }); }
    });
    return true;
  }

  if (msg.type === "PT_FETCH_AND_SCORE") {
    chrome.identity.getAuthToken({ interactive: false }, async (token) => {
      try {
        const res = await fetch(`${self.PT_CONFIG.GMAIL_BASE_URL}/messages/${msg.id}?format=full`, {
          headers: self.PT_GMAIL.authHeaders(token)
        });
        const full = await res.json();
        const parsed = self.PT_GMAIL.parseMessageFull(full);
        const score = self.PT_GMAIL.scorePhishingRisk(parsed);
        
        sendResponse({ 
          ok: true, 
          parsed, 
          score: { ...score, reasons: score.indicators },
          rawHeaders: full.payload.headers
        });
      } catch (e) { sendResponse({ ok: false }); }
    });
    return true;
  }

  if (msg.type === "PT_COLLECT_HEADERS") {
    const rawHeaderString = (msg.headers || [])
      .map(h => `${h.name}: ${h.value}`)
      .join("\r\n");

    console.log("[Secondary Scan] Sending headers for message:", msg.id);

    fetch(self.PT_CONFIG.DJANGO_ENDPOINT, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Token ${self.PT_CONFIG.API_TOKEN}`
      },
      body: JSON.stringify({ raw_headers: rawHeaderString })
    })
    .then(response => {
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return response.json();
    })
    .then(data => {
      console.log("[Secondary Scan] Django response:", data);
      sendResponse({ ok: true, risk_level: data.risk_level });
    })
    .catch(error => {
      console.error("[Secondary Scan] Django POST failed:", error);
      sendResponse({ ok: false, error: error.message });
    });

    return true;
  }
});
