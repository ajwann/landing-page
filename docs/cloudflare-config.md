# Cloudflare configuration for awanninger.com

GitHub Pages can't set response headers, so security headers, edge caching and
bot settings live in the Cloudflare dashboard for the `awanninger.com` zone.
Nothing in this file is applied automatically.

Dashboard menu names move around between Cloudflare releases. If a path below
doesn't match, search the dashboard for the rule type named in **bold**.

## Status (2026-10-31)

Steps 1–5 below were applied through the Cloudflare API with the `cf` CLI and
checked with the `curl` commands at the end of this file.

| Step | State |
|---|---|
| 1. Bot settings | Done. JavaScript Detections off (`enable_js: false`). Bot Fight Mode, Block AI bots and Cloudflare-managed robots.txt were already off. |
| 2. Security headers | Done. Rule `Security headers` in `http_response_headers_transform`, CSP still **Report-Only**. |
| 3. HSTS | Done. `max-age=31536000; includeSubDomains`, no preload. |
| 4. Cache Rules | Done. Two rules in `http_request_cache_settings`. HTML edge TTL is **2 hours**, the Free plan minimum. |
| 5. Redirect Rule | Done. Rule in `http_request_dynamic_redirect`. |
| 6. Enforce CSP | **Pending.** Due around 2026-11-07 if no `[Report Only]` violations show up. |
| 7. Analytics | Decided: keep both GA and Cloudflare Web Analytics. The CSP allows both. |
| 8. Markdown for agents | Done. URL Rewrite Rule serves `/index.md` for `/` when `Accept` contains `text/markdown`. ([§7](#7-markdown-for-agents)) |
| 9. API catalog | Done. Rule `API catalog content type` sets `application/linkset+json` on `/.well-known/api-catalog`. ([§8](#8-api-catalog)) |

The rules match only `http.host eq "awanninger.com"`, so the `browse` and
`cats` tunnel subdomains don't get the CSP or caching rules. HSTS is a zone-wide
setting and covers them; both serve valid HTTPS.

## Apply in this order

1. **Turn off Bot Fight Mode / JavaScript Detections**, and make sure Block AI
   bots / AI Crawl Control blocking is off. The CSP below would block the
   inline script that JS Detections injects. ([§3](#3-bot-settings))
2. **Response Header Transform Rule**: CSP as *Report-Only*, plus
   Referrer-Policy, Permissions-Policy and X-Frame-Options. ([§1](#1-security-headers))
3. **HSTS**: one year plus includeSubDomains. ([§2](#2-hsts))
4. **Cache Rules**: HTML at the edge, longer browser TTL for images. ([§5](#5-caching))
5. **Redirect Rule**: `/index.html` → `/`. ([§6](#6-redirect-indexhtml-to-))
6. After a week with no unexpected reports, **switch the CSP header to
   enforcing**, then remove the `<meta http-equiv="Content-Security-Policy">`
   line from `index.html`. ([§1](#1-security-headers))
7. Optional: **pick one analytics product**. ([§4](#4-analytics))

---

## 1. Security headers

**Rules → Overview → Create rule → Response Header Transform Rule**

- Rule name: `Security headers`
- If incoming requests match: **Custom filter expression**
  ```
  (http.host eq "awanninger.com")
  ```
- Then: **Modify response header**. Add one **Set static** row per header:

| Header name | Value |
|---|---|
| `Content-Security-Policy-Report-Only` | *(policy below)* |
| `Referrer-Policy` | `strict-origin-when-cross-origin` |
| `Permissions-Policy` | `camera=(), microphone=(), geolocation=(), interest-cohort=()` |
| `X-Frame-Options` | `DENY` |

The policy, on one line:

```
default-src 'self'; script-src 'self' https://www.googletagmanager.com https://static.cloudflareinsights.com; connect-src 'self' https://www.google-analytics.com https://*.google-analytics.com https://www.googletagmanager.com https://cloudflareinsights.com; img-src 'self' data: https://www.google-analytics.com https://www.googletagmanager.com; style-src 'self'; font-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'none'; object-src 'none'; upgrade-insecure-requests
```

How this differs from the starting point in the audit:

- **`connect-src` adds `https://www.googletagmanager.com`.** gtag.js can make
  fetch/beacon calls back to that host. GA4 sends its hits to
  `www.google-analytics.com` or regional hosts such as
  `region1.google-analytics.com`, which `*.google-analytics.com` covers.
- **No `'unsafe-inline'` anywhere.** The page has no inline scripts (the GA
  bootstrap is now `/analytics.js`) and no inline styles. The JSON-LD block is
  `type="application/ld+json"`, which browsers never execute, so CSP ignores it.
- **`style-src 'self'` / `font-src 'self'` are enough** now that Material Icons
  is an inline SVG sprite and the Google Fonts requests are gone.
- **No `frame-src`.** The page embeds no iframes. Cloudflare's JS Detections
  adds a hidden iframe *and an inline bootstrap script*, and this policy blocks
  both, which is why step 1 turns JS Detections off first. If you keep JS
  Detections, you'd need to allow its inline script (Cloudflare documents a
  nonce-based approach), which weakens the policy.

This policy was tested locally with the header set (no CSP violations, and GA
loaded and sent its page_view). Cloudflare Web Analytics wasn't exercised
locally, because Cloudflare injects that beacon only at the edge. The
Report-Only week covers it.

**Rollout:**

1. Ship as `Content-Security-Policy-Report-Only` (above). For a week, check
   DevTools → Console on the live page in a couple of browsers. Report-Only
   violations show up as `[Report Only]` messages. Also check **Security →
   Page Shield** (or **Client-side security**) if it's on your plan.
2. Then edit the rule and rename the header to `Content-Security-Policy`, with
   the same value.
3. Delete `<meta http-equiv="Content-Security-Policy" content="upgrade-insecure-requests">`
   from `index.html`, because the header now carries `upgrade-insecure-requests`.

Optional Terraform (Cloudflare provider v4), if you'd rather keep this in code:

```hcl
resource "cloudflare_ruleset" "security_headers" {
  zone_id = var.zone_id
  name    = "Security headers"
  kind    = "zone"
  phase   = "http_response_headers_transform"

  rules {
    description = "Security headers"
    expression  = "(http.host eq \"awanninger.com\")"
    action      = "rewrite"
    action_parameters {
      headers {
        name      = "Content-Security-Policy-Report-Only"
        operation = "set"
        value     = "default-src 'self'; script-src 'self' https://www.googletagmanager.com https://static.cloudflareinsights.com; connect-src 'self' https://www.google-analytics.com https://*.google-analytics.com https://www.googletagmanager.com https://cloudflareinsights.com; img-src 'self' data: https://www.google-analytics.com https://www.googletagmanager.com; style-src 'self'; font-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'none'; object-src 'none'; upgrade-insecure-requests"
      }
      headers {
        name      = "Referrer-Policy"
        operation = "set"
        value     = "strict-origin-when-cross-origin"
      }
      headers {
        name      = "Permissions-Policy"
        operation = "set"
        value     = "camera=(), microphone=(), geolocation=(), interest-cohort=()"
      }
      headers {
        name      = "X-Frame-Options"
        operation = "set"
        value     = "DENY"
      }
    }
  }
}
```

## 2. HSTS

**SSL/TLS → Edge Certificates → HTTP Strict Transport Security (HSTS) → Change settings**

- Enable HSTS: **On**
- Max Age: **12 months** (`31536000`)
- Apply HSTS policy to subdomains (includeSubDomains): **On**
- Preload: **Off** for now
- No-Sniff header: **On** (this is what already sends `x-content-type-options: nosniff`)

`includeSubDomains` makes browsers refuse plain HTTP on every
`*.awanninger.com` host for a year. Before turning it on, check under **DNS →
Records** that every subdomain (`www` and anything else) serves valid HTTPS.

**Preload:** add it only once includeSubDomains has been live for a while
without problems, then submit at <https://hstspreload.org>. Preload is hard to
undo. The domain is compiled into Chrome, Firefox and Safari, so removal takes
a request, then a browser release cycle, and then users updating their
browsers. That's months, during which no subdomain can serve HTTP. For a
personal site the benefit over a one-year HSTS header is small. It's fine to
never preload.

## 3. Bot settings

**JavaScript Detections and Bot Fight Mode.** The
`/cdn-cgi/challenge-platform/scripts/jsd/main.js` request, the hidden iframe
and the two or three extra requests on every page load come from Cloudflare's
**JavaScript Detections** (on by default with **Bot Fight Mode**). It injects an
inline `<script>` into the HTML on every visit to fingerprint the browser. On a
static page with no forms, logins or API, there's nothing for it to protect.

- **Security → Bots** (or **Security → Settings → Bot traffic**):
  - **Bot Fight Mode**: Off
  - **JavaScript Detections**: Off. On some plans this is tied to Bot Fight
    Mode and switches off with it.
- Same page, **Block AI bots**: **Do not block**. Also open **AI Crawl Control**
  (formerly AI Audit) and make sure no crawler is set to Block. `robots.txt` and
  `llms.txt` explicitly invite AI crawlers, and blocking them at the edge
  contradicts that.
- Under **Security → Events**, filter the last 24h by action *Managed
  Challenge / JS Challenge / Block*. Confirm that Googlebot, Bingbot, GPTBot,
  ClaudeBot and PerplexityBot aren't being challenged.

If you'd rather keep Bot Fight Mode on, still do that Security → Events check.
Then keep the CSP in Report-Only, or allow the JSD inline script, because the
enforced CSP would block it.

## 4. Analytics

Both run today: Google Analytics 4 (`gtag.js`, ~180 KB, sets cookies) and
Cloudflare Web Analytics (beacon injected at the edge, cookieless).

| | Google Analytics 4 | Cloudflare Web Analytics |
|---|---|---|
| Cookies / consent banner | Sets `_ga` cookies; consent needed in the EU/UK | Cookieless, no consent banner needed |
| Weight | ~180 KB script + collect calls | Small beacon (~6 KB) |
| Referrers, pages, countries, devices | Yes | Yes |
| Acquisition / campaign (UTM) reports, audiences, events, funnels, retention | Yes | No |
| Google Search Console / Ads integration | Yes | No |
| Core Web Vitals from real visitors | No (not out of the box) | Yes |
| Counts visitors who block GA | No | Mostly yes (served from your own zone) |

**Recommendation:** for a personal landing page, keep **Cloudflare Web
Analytics** and drop GA. You'd lose UTM campaign reporting and the Search
Console link; you'd gain no cookies, ~180 KB less script and a shorter CSP. To
drop GA:

1. Delete the two GA `<script>` tags in `index.html` and delete `analytics.js`.
2. CSP: remove `https://www.googletagmanager.com` and both
   `google-analytics.com` entries from `script-src`, `connect-src` and `img-src`.

If you'd rather keep GA (for campaign reporting), turn off Cloudflare Web
Analytics under **Analytics & Logs → Web Analytics → awanninger.com → Manage
site → disable automatic setup**. Then drop `static.cloudflareinsights.com` and
`cloudflareinsights.com` from the CSP.

## 5. Caching

Today the HTML is `cf-cache-status: DYNAMIC` (never cached at the edge), and
CSS/JS/images get a 4-hour browser TTL from GitHub Pages.

**Caching → Cache Rules → Create rule**

**Rule 1: Edge-cache HTML, text and Markdown**

- Expression:
  ```
  (http.host eq "awanninger.com" and (http.request.uri.path eq "/" or ends_with(http.request.uri.path, ".html") or ends_with(http.request.uri.path, ".txt") or ends_with(http.request.uri.path, ".xml") or ends_with(http.request.uri.path, ".md")))
  ```
- Cache eligibility: **Eligible for cache**
- Edge TTL: **Ignore cache-control header and use this TTL → 2 hours** (the Free plan minimum; 1 hour needs Pro)
- Browser TTL: **Respect origin TTL** (GitHub Pages sends `max-age=600`)

After each deploy, either wait up to two hours or run **Caching → Configuration →
Purge Cache → Purge Everything**.

**Rule 2: Longer browser TTL for images**

- Expression:
  ```
  (http.host eq "awanninger.com" and http.request.uri.path.extension in {"jpg" "jpeg" "png" "webp" "svg" "ico"})
  ```
- Cache eligibility: **Eligible for cache**
- Edge TTL: **Respect origin** (or 1 day)
- Browser TTL: **Override origin → 30 days**

Images rarely change, and when they do they'll get a new filename (as `aw.png`
→ `aw-200.*` did).

**CSS/JS:** leave at the current 4 hours. Filenames aren't fingerprinted and
`index.html` doesn't use `?v=` query strings, so a long TTL would leave
returning visitors on stale styles after a change. If you later add
`?v=<n>` to the `<link>`/`<script>` URLs in `index.html` (and bump it on each
change), a third rule matching `.css`/`.js` can set Browser TTL to 1 year with
`Cache-Control: public, max-age=31536000, immutable`.

## 6. Redirect `/index.html` to `/`

The canonical tag already tells search engines `/` is the real URL. This
removes the duplicate entirely.

**Rules → Redirect Rules → Create rule**

- Expression:
  ```
  (http.host eq "awanninger.com" and http.request.uri.path eq "/index.html")
  ```
- Then: **Static**, URL `https://awanninger.com/`, status **301**,
  **Preserve query string** on.

## 7. Markdown for agents

Cloudflare's built-in **Markdown for Agents** (AI Crawl Control, setting
`content_converter`) converts HTML to Markdown at the edge, but it needs a Pro
or Business plan. On this Free zone the setting reports `editable: false`. The
same result comes from a hand-written `/index.md` plus a URL rewrite:

- `index.md` is the Markdown version of the page. GitHub Pages serves it as
  `text/markdown; charset=utf-8`. It must **not** start with YAML front matter
  (`---`), or Jekyll will render it to HTML and collide with `index.html`.
  Keep it in step with `index.html` when the page changes.

**Rules → Overview → Create rule → URL Rewrite Rule**

- Rule name: `Markdown for agents`
- Expression:
  ```
  (http.host eq "awanninger.com" and http.request.uri.path eq "/" and any(lower(http.request.headers["accept"][*])[*] contains "text/markdown"))
  ```
- Path: **Rewrite to → Static → `/index.md`**. Query: **Preserve**.

Requests without `text/markdown` in `Accept`, which includes all browsers, get
the HTML as before. The edge cache keys on the rewritten path, so the HTML and
Markdown variants are cached separately. The cache rule in §5 also covers
`.md`.

**Response Header Transform Rule** `Vary on Accept for /` sets
`Vary: Accept, Accept-Encoding` on `/`. Browsers and any shared caches outside
Cloudflare then keep the two variants apart:

- Expression: `(http.host eq "awanninger.com" and raw.http.request.uri.path eq "/")`

If the zone moves to Pro, switch the built-in feature on instead and delete both
rules and `index.md`.

## 8. API catalog

`/.well-known/api-catalog` ([RFC 9727](https://www.rfc-editor.org/rfc/rfc9727))
lets agents discover a site's APIs. This site has none, so the catalog is an
empty linkset, `{"linkset": []}`. If you publish an API later, add an entry
with an `anchor` and `service-desc` / `service-doc` links.

Two pieces make it work on GitHub Pages:

- `_config.yml` has `include: [".well-known"]`, because Jekyll skips
  dot-directories by default.
- GitHub Pages serves the extensionless file as `application/octet-stream`.
  A third rule in the Response Header Transform ruleset fixes the type:
  - Rule name: `API catalog content type`
  - Expression: `(http.host eq "awanninger.com" and http.request.uri.path eq "/.well-known/api-catalog")`
  - Set static `Content-Type` = `application/linkset+json; profile="https://www.rfc-editor.org/info/rfc9727"`

---

## Verification checklist

Run each block after applying the matching step. `-H 'Cache-Control: no-cache'`
isn't needed for headers, but purge the cache first if a step touches HTML.

**Step 1: bot settings.** The challenge-platform script is gone:

```sh
curl -s https://awanninger.com/ | grep -c challenge-platform
# expect: 0
```

**Step 2: security headers (Report-Only)**

```sh
curl -sI https://awanninger.com/ | grep -iE '^(content-security-policy|referrer-policy|permissions-policy|x-frame-options)'
# expect:
# content-security-policy-report-only: default-src 'self'; script-src 'self' https://www.googletagmanager.com ...
# referrer-policy: strict-origin-when-cross-origin
# permissions-policy: camera=(), microphone=(), geolocation=(), interest-cohort=()
# x-frame-options: DENY
curl -sI https://awanninger.com/styles.css | grep -i referrer-policy   # rule covers every path
```

**Step 3: HSTS**

```sh
curl -sI https://awanninger.com/ | grep -i strict-transport-security
# expect: strict-transport-security: max-age=31536000; includeSubDomains
curl -sI https://www.awanninger.com/ | grep -iE '^(HTTP|location|strict-transport-security)'
# expect: HTTP/2 301, location: https://awanninger.com/, plus the HSTS header
```

**Step 4: caching.** Run twice; the second one should be a HIT:

```sh
curl -sI https://awanninger.com/ | grep -iE '^(cf-cache-status|cache-control|age)'
curl -sI https://awanninger.com/ | grep -iE '^(cf-cache-status|cache-control|age)'
# expect on the 2nd: cf-cache-status: HIT, cache-control: max-age=600
curl -sI https://awanninger.com/aw-200.webp | grep -iE '^(cf-cache-status|cache-control)'
# expect: cache-control: max-age=2592000
curl -sI https://awanninger.com/styles.css | grep -i cache-control
# expect: cache-control: max-age=14400 (unchanged)
```

**Step 5: redirect**

```sh
curl -sI https://awanninger.com/index.html | grep -iE '^(HTTP|location)'
# expect: HTTP/2 301 and location: https://awanninger.com/
curl -sI http://awanninger.com/ | grep -iE '^(HTTP|location)'
# expect: HTTP/1.1 301 and location: https://awanninger.com/ (already the case)
```

**Step 6: CSP enforcing**

```sh
curl -sI https://awanninger.com/ | grep -i '^content-security-policy:'
# expect: content-security-policy: default-src 'self'; ... upgrade-insecure-requests
curl -s https://awanninger.com/ | grep -c 'http-equiv="Content-Security-Policy"'
# expect: 0 (after removing the meta tag)
```

Then load the page in a browser with DevTools open: no CSP errors in the
console, and GA (Network → `collect`) and/or the Cloudflare beacon
(`cloudflareinsights.com/cdn-cgi/rum`) requests succeed.

**Markdown for agents**

```sh
curl -sI -H 'Accept: text/markdown' https://awanninger.com/ | grep -iE '^(HTTP|content-type|vary)'
# expect: HTTP/2 200, content-type: text/markdown; charset=utf-8, vary: Accept, Accept-Encoding
curl -sI https://awanninger.com/ | grep -i '^content-type'
# expect: content-type: text/html; charset=utf-8
```

**API catalog**

```sh
curl -sI https://awanninger.com/.well-known/api-catalog | grep -iE '^(HTTP|content-type)'
# expect: HTTP/2 200 and content-type: application/linkset+json; profile="https://www.rfc-editor.org/info/rfc9727"
```

**Step 7: analytics (if you drop GA)**

```sh
curl -s https://awanninger.com/ | grep -c googletagmanager
# expect: 0
```
