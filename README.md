# Bear-Hacks-2026
This repo is for a Hackathon that runs from April 24th to April 26th 2026. My group consists of myself Erik Stiefeling, and two classmates Nick McClure and Lyndon Wagg.


![ER Diagram](ER_Diagram.png)
![Project Flow chart](Flowchart.png)

---

## King Phisher — Project Overview

**King Phisher** is a phishing email detection and counter-attack web application built with Django. It works alongside a Chrome extension that reads a Gmail inbox  and submits their raw headers to the Django backend for analysis.

### How It Works

1. The **Chrome extension** monitors a user's Gmail inbox and sends suspicious email headers to the Django API using a per-user Bearer token.
2. The **Django backend** parses those headers, evaluates SPF, DKIM, and DMARC authentication results, detects domain mismatches, and assigns a risk level: `safe`, `suspicious`, or `phishing`.
3. Flagged emails appear in a **web dashboard** where the user can trigger a full analysis or dismiss the alert.
4. Confirmed phishing/suspicious senders can be targeted with a **counter-attack** that streams 100 emails back to the sender in real time via a terminal-styled UI.

### Django Apps

#### `analyzer` — Email Analysis Engine
The core of the project. Exposes a REST-style API consumed by the Chrome extension.

- **`/analyzer/analyze/`** — Accepts raw email headers (Bearer token auth), runs the analysis pipeline, and stores results with a risk level.
- **`/analyzer/flag/`** — Accepts a "pre-flagged" email from the extension (before full analysis) and queues it for dashboard review.
- **`/analyzer/flagged/<id>/analyze/`** — Triggers a full analysis on a queued email from the dashboard.
- **`/analyzer/flagged/<id>/dismiss/`** — Discards a queued email without analyzing it.
- **`/analyzer/result/<id>/delete/`** — Removes a saved analysis result.

**Risk logic:**
- 2+ auth failures (SPF/DKIM/DMARC) → **phishing**
- 1 auth failure + reply-to/sender domain mismatch → **phishing**
- 1 auth failure or domain mismatch → **suspicious**
- Extension flagged as mid/high risk → **suspicious**
- Otherwise → **safe**

**Models:**
- `APIToken` — Per-user tokens that authenticate the Chrome extension.
- `AnalysisResult` — Stores analyzed emails with full SPF/DKIM/DMARC results, provider, risk level, and raw analysis JSON.
- `FlaggedEmail` — Staging table for emails the extension flagged but that haven't been fully analyzed yet.

**Services (`analyzer/services/`):**
- `header_analyzer.py` — Main orchestrator: parses received chains, addresses, auth headers, and provider-specific headers.
- `auth_parser.py` — Regex-based extraction of SPF/DKIM/DMARC pass/fail/softfail from `Authentication-Results` headers.
- `provider_check.py` — Detects Gmail, Microsoft, or Yahoo based on provider-specific headers.
- `header_extractors.py` — MIME decoding and email address parsing utilities.

#### `dashboard` — Web UI
A login-protected interface for reviewing analysis results.

- **`/dashboard/`** — Shows two tabs:
  - **Pending Review**: Emails flagged by the extension awaiting analysis. Each row has "Send for Analysis" and "Dismiss" actions.
  - **Analysis Results**: Fully analyzed emails showing SPF/DKIM/DMARC status, risk badge, and a "Remove" option.
- All actions are handled client-side via `fetch()` with AJAX and CSRF tokens; rows are removed from the DOM on success without a page reload.
- Styled with an ocean/kingfisher theme (animated GIF, seaweed, floating particles).

#### `spammer` — Counter-Attack Module
Accessible from the dashboard for any confirmed phishing or suspicious sender.

- **`/dashboard/spammer/`** — Lists all phishing/suspicious `AnalysisResult` entries as targets.
- **`/dashboard/spammer/send/<id>/`** — Launches a counter-attack: sends 100 emails to the sender via Gmail SMTP and streams real-time progress back to the browser using `StreamingHttpResponse`.
- The UI renders a full-screen terminal overlay (green-on-black, monospace) showing each email's delivery status as it happens. A confirmation modal warns the user before initiating.

### Infrastructure & Configuration

| Setting | Value |
|---|---|
| Framework | Django 4.2.11 |
| Database | SQLite3 (`db.sqlite3`) |
| Email (SMTP) | Gmail — `kingphisher194@gmail.com`, port 587 TLS |
| Auth enforcement | Custom `LoginRequiredMiddleware` (exempts `/accounts/`, `/admin/`, `/analyzer/`, `/api/`) |
| CORS | Enabled for `/analyzer/` and `/api/` so the Chrome extension can call the API cross-origin |
| Timezone | America/New_York |

The `/api/` URL prefix mirrors `/analyzer/` entirely and exists specifically for the Chrome extension to call without being blocked by CORS or login middleware.
