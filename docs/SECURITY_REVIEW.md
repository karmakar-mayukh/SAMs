# Security Review

This document records the findings from a security scan of the repository
covering hardcoded secrets, SQL injection, unvalidated user input, insecure
dependencies, CORS configuration, exposed debug endpoints, and missing
authentication checks. Items marked **Fixed** are addressed by the
accompanying code changes; remaining items are documented here for the
maintainers to triage.

## Critical — fixed in this PR

### 1. Hardcoded Alpha Vantage API key

- **File:** `main.py` (previously line 1186)
- **Issue:** The Alpha Vantage API key `N6A6QT6IBFJOPJ70` was committed to the
  repository and used as a fallback data source. Anyone with repo access (or
  scraping GitHub) can harvest the key, exhaust its quota, or use it to
  masquerade as the project.
- **Fix:** The key is now read from the `ALPHA_VANTAGE_API_KEY` environment
  variable. If it is missing, the Alpha Vantage fallback is skipped entirely
  and the request fails loudly instead of silently using a shared key. The
  original key should be considered compromised and **rotated in the Alpha
  Vantage console**.

### 2. Weak default `SECRET_KEY`

- **File:** `main.py`
- **Issue:** The Flask `SECRET_KEY` fell back to the literal string
  `CHANGE_ME_IN_PRODUCTION` whenever the environment variable was unset.
  Attackers who guess this fallback can forge session cookies (used for
  authentication, admin role, CSRF tokens) and take over any account.
- **Fix:** The fallback now generates a random per-process key via
  `secrets.token_urlsafe(32)` and logs a warning. When `FLASK_ENV=production`
  the app refuses to start without an explicit `SECRET_KEY`.
  `SESSION_COOKIE_SECURE` is also enabled automatically in production so the
  session cookie is only transmitted over HTTPS.

### 3. Flask debug mode enabled by default

- **File:** `main.py` (bottom of file)
- **Issue:** `app.run(debug=True)` launches the Werkzeug debugger, which
  exposes an interactive Python shell on any unhandled exception. A single
  5xx response from a deployed instance is enough for an attacker to run
  arbitrary code on the host.
- **Fix:** Debug mode is now controlled by the `FLASK_DEBUG` environment
  variable and defaults to off.

### 4. Path traversal / arbitrary file overwrite via `/predict`

- **File:** `main.py`, `predict` route
- **Issue:** The ticker symbol submitted to `/predict` was used directly as a
  filename (`f'{quote}.csv'`) and passed to third-party HTTP APIs. A crafted
  value such as `../../etc/passwd` would cause `pd.read_csv` to read outside
  the app directory, and a `quote` that collides with an existing CSV (for
  example `AAPL`) caused the downloaded CSV to overwrite the committed
  dataset.
- **Fix:** A new `_sanitize_ticker` helper rejects anything that is not
  `[A-Z0-9.\-]{1,10}`. Invalid input renders the "not found" page instead of
  touching the filesystem.

### 5. Hardcoded admin credentials

- **File:** `create_admin.py`
- **Issue:** The bootstrap script hard-coded `admin@example.com` /
  `admin123`. Anyone who runs the script (including automated deployment
  workflows) ends up with a predictable, well-known admin account. The same
  credentials were also visible in `README.md` under "Default Credentials".
- **Fix:** `create_admin.py` now requires `ADMIN_EMAIL`, `ADMIN_USERNAME` and
  `ADMIN_PASSWORD` environment variables, enforces a 12-character minimum
  password, and refuses to run without them. The README still needs to be
  updated to remove the old default credentials (tracked below).

### 6. Leaked credential artifacts in the repository

- **Files:**
  - `admin_login_credentials_2025-12-05_09-23-18.png` — screenshot
  - `admin@example.comadmin123.csv` — empty CSV whose filename embeds the
    admin credentials
- **Fix:** Both files are removed from the working tree. Because they were
  previously committed, their contents remain in git history; to fully scrub
  them the maintainers should rewrite history (e.g. with
  `git filter-repo --path '<file>' --invert-paths`) and rotate any admin
  account that shared those credentials.

## Findings reported but not fixed

These require design decisions or content changes beyond the scope of a
security hotfix. They are listed in descending severity.

### 7. `README.md` still publishes default admin credentials

Sections "Quick Start for New Users" and "Default Credentials" in
`README.md` publish `admin@example.com` / `admin123` and
`stockpredictorapp@gmail.com` / `Samplepass@123`. Those values must be
removed or replaced with placeholders once the maintainers agree on the new
bootstrap instructions. Left as-is to avoid a merge conflict with the
maintainers' documentation.

### 8. Unpinned / outdated dependencies

`requirements.txt` pins only a handful of versions. The rest install the
latest available wheel at build time, which breaks reproducibility and makes
CVE triage impossible. Recommended actions:

- Pin every dependency with a lockfile (`pip-compile`, `uv`, or
  `poetry lock`).
- Replace `newspaper3k` with the maintained `newspaper4k` fork;
  `newspaper3k` has been unmaintained since 2020 and depends on vulnerable
  versions of `lxml`.
- `alpha_vantage==2.3.1`, `textblob==0.15.3`, `seaborn==0.11.1` are all
  several majors behind; review their changelogs for security updates.
- `selenium` + `webdriver-manager` download Chromedrivers at runtime. This
  is fine in a dev environment but should not run as root in production.

### 9. `/predict` endpoint is unauthenticated and CSRF-unprotected

`/predict` accepts `POST` without authentication or CSRF validation and has
side-effects (downloads and writes CSV files to the application directory,
triggers outbound HTTP calls). After fix #4 the blast radius is limited to
exhausting outbound quota and filling up the disk with CSVs for attacker-
chosen tickers, but the endpoint should ideally require a session and a
CSRF token consistent with the rest of the app. Changing this would require
updating `templates/index.html` to emit a CSRF input and gating access
behind `@login_required()`.

### 10. `/admin/datasets/upload` accepts arbitrary CSV content

The admin upload route correctly restricts the extension and sanitises the
filename, but it does not validate the CSV contents. A malicious admin
could upload a file that is interpreted as code by downstream consumers
(e.g. Excel formula injection via cells that start with `=`, `+`, `-`, `@`).
Because upload is gated on the `admin` role this is low severity, but worth
adding a CSV content validator or prefixing suspect cells with `'`.

### 11. `retrieving_news_polarity` and other external calls log exceptions as
plain strings

Exceptions from `requests`, `selenium`, `yfinance`, etc. are printed via
`print(f"... error: {e}")`. In production this can leak stack traces and
secrets (URL-embedded tokens, environment variables surfaced by libraries)
into stdout. Consider routing them through the existing logger and
scrubbing sensitive data.

### 12. `/health` is unauthenticated and exposes operational metrics

`/health` returns total request count, total errors, and average latency.
This is intentional for liveness/readiness probes but also provides
reconnaissance data to unauthenticated callers. Consider restricting it to
internal networks or adding a shared token.

## Areas that were checked and look OK

- **SQL injection:** All database access goes through SQLAlchemy ORM helpers
  (`Model.query.filter_by(...)`, `.first()`, `.count()`). No raw SQL is
  assembled from user input.
- **CORS:** No `flask-cors` or manual `Access-Control-Allow-Origin` headers
  are set; the app therefore rejects cross-origin requests by default.
- **Password storage:** User passwords are hashed via Werkzeug's
  `generate_password_hash` and verified with `check_password_hash`.
- **Template rendering:** Jinja auto-escapes by default and no
  `render_template_string`, `|safe`, `eval`, `exec`, or `subprocess(..., shell=True)`
  usage was found in application code.
- **Admin routes:** All `/admin/**` routes are decorated with
  `@login_required(role='admin')`; CSRF is verified on every state-changing
  admin action.
- **File download:** `/invoices/<id>/download` scopes the query to the
  logged-in user's id, preventing IDOR.

## Suggested environment variables

Set these before running the app in any environment beyond local
development:

| Variable                | Purpose                                                |
|-------------------------|--------------------------------------------------------|
| `SECRET_KEY`            | Flask session signing key (required in production).   |
| `FLASK_ENV`             | Set to `production` to enforce strict config checks.  |
| `FLASK_DEBUG`           | Opt-in for the Werkzeug debugger (`1`/`true`).        |
| `DATABASE_URL`          | SQLAlchemy URI (defaults to a local SQLite file).     |
| `ALPHA_VANTAGE_API_KEY` | Fallback market-data provider for `/predict`.         |
| `ADMIN_EMAIL`           | Required by `create_admin.py`.                        |
| `ADMIN_USERNAME`        | Required by `create_admin.py`.                        |
| `ADMIN_PASSWORD`        | Required by `create_admin.py`; minimum 12 characters. |
