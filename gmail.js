self.PT_GMAIL = {
  authHeaders: (token) => ({
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  }),

  decodeBase64UrlSafe: (str) => {
    if (!str) return "";
    str = str.replace(/-/g, "+").replace(/_/g, "/");
    while (str.length % 4) { str += "="; }
    try { return atob(str); } catch (e) { return ""; }
  },

  parseMessageFull: (msg) => {
    const headers = msg.payload.headers || [];
    let from = headers.find(h => h.name === "From")?.value || "Unknown";
    let subject = headers.find(h => h.name === "Subject")?.value || "(No subject)";
    let body = "";
    let hasSensitiveAttachment = false;

    const findParts = (parts) => {
      for (let part of parts) {
        if (part.mimeType === "text/plain" && part.body.data) {
          body = self.PT_GMAIL.decodeBase64UrlSafe(part.body.data);
        }
        if (part.filename && /\.(html|js|exe|scr|zip)$/i.test(part.filename)) {
          hasSensitiveAttachment = true;
        }
        if (part.parts) findParts(part.parts);
      }
    };

    if (msg.payload.parts) findParts(msg.payload.parts);
    else if (msg.payload.body?.data) body = self.PT_GMAIL.decodeBase64UrlSafe(msg.payload.body.data);

    return { from, subject, body, hasSensitiveAttachment };
  },

  scorePhishingRisk: (parsed) => {
    let score = 0;
    let indicators = [];
    const CFG = self.PT_CONFIG;
    const scanText = (parsed.subject + " " + parsed.body).toLowerCase();

    if (CFG.PATTERNS.URGENCY.test(scanText)) {
      score += CFG.WEIGHTS.URGENT_KEYWORDS;
      indicators.push("Urgent language detected");
    }
    if (parsed.hasSensitiveAttachment) {
      score += CFG.WEIGHTS.SENSITIVE_ATTACHMENT;
      indicators.push("Suspicious attachment type");
    }
    if (CFG.PATTERNS.HOMOGRAPH.test(parsed.body)) {
      score += 50;
      indicators.push("Potential Homograph (non-ASCII) characters");
    }

    let risk = { label: "Low Risk", css: "low" };
    if (score >= CFG.DANGER_THRESHOLD) risk = { label: "High Risk", css: "high" };
    else if (score >= CFG.WARNING_THRESHOLD) risk = { label: "Medium Risk", css: "mid" };

    return { score, risk, indicators };
  }
};