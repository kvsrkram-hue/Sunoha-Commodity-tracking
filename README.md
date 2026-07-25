# The Agri Ledger — mobile app (PWA)

An installable mobile app for your agri commodities desk: price tracking, 30-day
forecasts, importer/exporter analytics, live news drivers, regulations lookup,
fact-checking, a macro reference strip (crude, gold, silver, copper, Fed funds,
US 10-yr, DXY, USD/INR) — locked behind a 6-digit passcode.

## Files

| File | Purpose |
|---|---|
| `index.html` | The whole app (UI + logic) |
| `manifest.webmanifest` | Makes it installable with name, icon, splash |
| `sw.js` | Service worker — offline support & caching |
| `icon-192.png`, `icon-512.png` | App icons |

## Step 1 — Put it online (2 minutes, free)

A PWA must be served over **HTTPS**. Easiest options:

**Option A — Netlify Drop (no account needed to try):**
1. Go to https://app.netlify.com/drop
2. Drag the whole `agri-ledger-app` folder onto the page.
3. You get a URL like `https://something.netlify.app` — that's your app.

**Option B — GitHub Pages:**
1. Create a repo, upload these 5 files.
2. Settings → Pages → deploy from branch → root.
3. Your app is at `https://<username>.github.io/<repo>/`.

## Step 2 — Install it on your phone

**Android (Chrome):** open the URL → Chrome shows an "Install app" prompt
(or menu ⋮ → *Add to Home screen* → *Install*). It gets its own icon, opens
full-screen without the browser bar, and works offline for the cached shell.

**iPhone (Safari):** open the URL → Share button → **Add to Home Screen**.

## Step 3 — First launch

1. **Create your 6-digit passcode.** It is hashed (SHA-256 + random salt) and
   stored only on that device. "reset" on the keypad wipes the device data if
   you forget it. Note: this is a device-level lock, like a phone PIN — see
   "Real multi-user login" below for cloud accounts.
2. **Add your Anthropic API key** (⚙ Settings) to power the AI features:
   Sync live, Why it moved, News desk, Regulations deep-dive, Fact check.
   Get a key at https://console.anthropic.com → API keys. The key is stored
   only on your device; calls go directly from your phone to Anthropic and
   are billed to your account (each scan costs roughly a cent or two).
   Without a key the app still works with the seed data, charts, forecasts
   and trade-flow analytics.

## What's inside

- **Core softs desk:** Arabica (USD/lb), Robusta (USD/MT), Cocoa (USD/MT),
  Cashew W320 kernels FOB Vietnam (USD/lb — no exchange exists for cashew).
- **Grains:** Wheat, Corn, Soybeans (CBOT).
- **10-year charts with zoom:** every commodity carries ~10 years of daily
  history. Preset ranges (6M / 1Y / 3Y / 5Y / 10Y), pinch-to-zoom and drag-to-pan
  on the chart, mouse-wheel zoom on desktop. Honest note: the long history is an
  approximate reconstruction — monthly anchor points taken from public price
  records (e.g. the 2021 Brazil frost, the 2022 wheat spike, the 2024-25 cocoa
  super-spike, the 2017 cashew peak), interpolated daily, with the last point
  pinned to the current/synced price. For contract-grade history, connect an
  exchange or data-vendor feed later.
- **India desk (Coffee Board):** fetches the Coffee Board of India's open
  *Daily Coffee Market Report* (coffeeboard.gov.in → Market Info) and renders
  grade-wise Indian prices (Arabica Plantation/Parchment/Cherry, Robusta
  Parchment/Cherry) plus ICE New York & London terminal levels as a table.
  Technical note: the Board's PDF sits behind a session postback (no fixed URL),
  so the app retrieves it through AI web search reading the published figures —
  which also sidesteps browser CORS limits. Requires the API key.
- **Forecast:** Holt double-exponential smoothing, 30 days, 80% band —
  statistical only; it cannot see frosts, decrees or tariffs.
- **Trade flows:** top exporter/importer shares + structural notes
  (EUDR dates, CIV/Tanzania cashew rules, Cocobod/CCC, Black Sea, etc.).
- **Macro strip:** WTI, Gold, Silver, Copper, Fed Funds, US 10Y, DXY, USD/INR.

## Real multi-user login (optional upgrade)

The passcode protects the device. If you later want team accounts with
email/password login from any device, the standard path is **Firebase
Authentication** (free tier):

1. console.firebase.google.com → create project → enable Email/Password auth.
2. Add the Firebase JS SDK to `index.html` and replace the passcode gate with
   `signInWithEmailAndPassword`.
3. Optionally store synced prices/notes per user in Firestore.

Ask Claude to wire this in when you're ready — it's ~50 lines of changes.

## Publishing to the Play Store (optional)

A PWA can be wrapped into a real Android package: go to https://www.pwabuilder.com,
paste your hosted URL, and it generates a signed APK/AAB you can upload to the
Play Store (Google developer account: one-time $25).

## Disclaimers

Prices, shares and projections are informational research tools — not
investment, trading or legal advice. Trade-flow shares are approximate;
verify with UN Comtrade / ITC Trade Map. Regulatory summaries are a starting
point; confirm with customs brokers and counsel per shipment.
