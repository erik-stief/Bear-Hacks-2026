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
    const forensicEntry = {
      scanTime: new Date().toISOString(),
      messageId: msg.id,
      headers: msg.headers
    };

    // 1. Print JSON to Service Worker Console
    console.log("[Secondary Scan] Forensic JSON Payload:", forensicEntry);

    // 2. Send to Django Webapp via POST
    const DJANGO_ENDPOINT = "<ERIK'S DJANGO ENGPOINT HERE>"; // Replace with actual endpoint

    fetch(DJANGO_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(forensicEntry)
    })
    .then(response => response.json())
    .then(data => {
      console.log("Sent to Django:", data);
      sendResponse({ ok: true });
    })
    .catch(error => {
      console.error("Django POST failed:", error);
      sendResponse({ ok: false, error: error.message });
    });

    return true; 
  }
});