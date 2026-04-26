self.PT_CONFIG = {
  GMAIL_BASE_URL: "https://gmail.googleapis.com/gmail/v1/users/me",
  MAX_SCAN_RESULTS: 100, 
  DANGER_THRESHOLD: 60,
  WARNING_THRESHOLD: 30,
  WEIGHTS: {
    DOMAIN_MISMATCH: 40,
    LINK_TEXT_MISMATCH: 35,
    URGENT_KEYWORDS: 20,
    SENSITIVE_ATTACHMENT: 45,
    UNCOMMON_SENDER: 15
  },
  PATTERNS: {
    URGENCY: /\b(urgent|action required|suspended|unauthorized|security alert|login detected|verify|immediate|act now|click here|password reset|invoice|immediately|now)\b/gi,
    HOMOGRAPH: /[^\u0000-\u007F]/,
    LINK_EXTRACTOR: /<a\s+(?:[^>]*?\s+)?href="([^"]*)"/gi
  },
  ENABLE_CONSOLE_LOGGING: true,
  AUTO_SCAN_ON_OPEN: true,
  DJANGO_ENDPOINT: "http://localhost:8000/analyzer/analyze/",
  API_TOKEN: "REPLACE_WITH_TOKEN_FROM_DJANGO_ADMIN"
};