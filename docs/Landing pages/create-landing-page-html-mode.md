---
title: "Create landing page (HTML Mode)"
excerpt: "Build a Scalev landing page from your own HTML, CSS, and JavaScript."
deprecated: false
hidden: false
metadata:
  robots: index
---
HTML Mode ships a landing page as plain HTML, CSS, and JavaScript instead of Builder components. You write the document, Scalev hosts it, and `window.Scalev` gives the page its data and checkout methods.

You can create the page two ways. Use the dashboard when a person writes or generates the HTML and wants a preview before publishing. Use the [Landing Pages API](/docs/landing-pages-api) when your own backend generates pages.

## Choose a page type

| Page type | Use it for | Checkout context |
| --- | --- | --- |
| HTML Sales Page | Content, lead capture, CTA links to another page | None. `Scalev.data.get().store` is unavailable |
| HTML Checkout Page | Pages that create orders from their own form | Required: one store plus at least one product variant or bundle price option |

The type is fixed when you create the page. A checkout page also locks its store after the first save, so pick the store you intend to sell from.

## Create the page in the dashboard

1. Open **Pages**, then choose **HTML Sales Page** or **HTML Checkout Page** from the new-page menu.
2. For a checkout page, open the **Context** tab and set **Store Context**, then **Products** and **Bundle Price Options**, and the action after checkout succeeds. Store Context is locked after the page is saved.
3. Open the **Code** tab and select **Open AI Prompt Builder** if you want an AI tool to write the document. Fill in what the page should be, its goal, and the visitor action, choose English or Indonesian, then copy the prompt. See [Example prompt](/docs/example-prompt) for the generated text.
4. Paste the prompt into ChatGPT or Claude, then bring the returned document back with **Import HTML**. Use **Upload File** for an `.html` file or **Paste HTML** for a full document.
5. Review the **HTML document** in the **Code** tab. HTML, CSS, and JavaScript stay together in one editor. The preview updates as you type.
6. Review **Dependencies and diagnostics**. Explicitly allow blocked origins for the relevant directive, or edit the permissions in **Security**. A script permission does not grant API connections.
7. Upload images in the **Media** tab and copy each file URL into your HTML.
8. Set the page name, slug, and SEO fields in the **Setting** tab, then save. Publish separately after reviewing the preview and diagnostics.

**Export** downloads the authored document without the runtime, platform analytics, or runtime tokens.

### What Import HTML keeps

Import retains the complete source, including document attributes, external scripts, stylesheet and font links, module scripts, import maps, JSON data, and integrity attributes. Scalev does not split or concatenate your scripts. Fragments gain document boundaries when saved.

Authored SEO and head entries override managed defaults. Editing SEO or language controls updates the matching document nodes. The document CSP remains a separate page setting: imported CSP meta tags stay in source but do not execute, and the editor reports a diagnostic.

Opening an older page assembles its legacy code in memory. Inspection, preview, and export do not save a migration. The next content save writes the unified document. Existing published content stays unchanged until you publish the saved version.

In **Product Page Studio**, an active original custom HTML template opens automatically in the same unified editor. You do not need a separate legacy import or test panel. Opening, previewing, and exporting leave the live page unchanged; **Save & Publish** saves the unified template and makes it live. An explicitly saved Builder or HTML Mode template takes precedence over the original fallback. The original source remains stored for compatibility, and existing product and bundle scripts retain their `#scalev[data-scalev]` data access after migration. New code should use the documented `Scalev.data.get()` accessor.

### Preview behavior

Preview runs on the public preview host in an isolated sandbox. Checkout, location, and prefill methods return simulated results, and platform analytics are suppressed. Network connections and embedded frames are intentionally restricted in preview. Diagnostics distinguish those restrictions from resource or execution failures.

Review unresolved errors before publishing. You can explicitly choose **Publish anyway** for unresolved resource or execution errors; invalid document structure and reserved runtime identifiers must be fixed. Static dependency discovery cannot prove that every dynamically loaded dependency will work.

## Create the page with the API

`POST /v3/pages` creates the page and its first display in one call. HTML Mode uses `render_mode: "html_mode"` with one `html_document` and a separate `csp_policy`.

```bash
curl -X POST https://api.scalev.com/v3/pages \
  -H "Authorization: Bearer $SCALEV_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Launch offer",
    "slug": "launch-offer",
    "is_published": true,
    "page_display": {
      "render_mode": "html_mode",
      "html_document": "<!doctype html><html lang=\"id\"><head><style>main { padding: 32px; }</style></head><body><main><h1>Launch offer</h1></main></body></html>",
      "csp_policy": {},
      "meta": { "lang": "id" }
    }
  }'
```

`html_document` is the complete authored document. Add `page_display.form_display` with `store_id` and the selected items when the page must create orders. This example leaves out the analytics fields; send them as shown in [Landing Pages API](/docs/landing-pages-api), including when they are empty. That guide also covers the full payload and how to publish a new display.

Existing integrations can continue sending complete `html_code`, `css_code`, and `js_code` payloads, with optional `additional_head_code`. You do not need to change an existing writer immediately. These fields remain accepted after a page has a unified version; the API assembles the legacy snapshot when saving. See [legacy request compatibility](/docs/landing-pages-api) before sending only some code sections.

## Write the page code

Keep these rules so the document imports cleanly and runs on the hosted page:

- Keep your complete HTML document in `html_document`, including `<head>`, stylesheets, styles, and scripts.
- Initialize code that accesses `window.Scalev` on `DOMContentLoaded` or later. The runtime is inserted near body-close, immediately before a trailing block of top-level scripts.
- Domain, slug, checkout, and publishing settings remain separate from the document.
- Use documented `window.Scalev` methods instead of calling Scalev URLs directly.
- Keep API keys, access tokens, and other credentials out of the page. Everything you ship is public browser code.
- Add every external asset, script, iframe, font, and API domain to the CSP policy.
- Render meaningful static content in the HTML so the first viewport is complete while runtime data loads, and keep the page usable when a `window.Scalev` call fails.

## Content Security Policy

The **Security** tab writes `csp_policy` on the page display. Each field takes the domains your page is allowed to reach:

| Field | Covers |
| --- | --- |
| `connect_src` | API calls from page JavaScript |
| `img_src` | Images |
| `media_src` | Audio and video |
| `font_src` | Fonts |
| `script_src` | External scripts |
| `style_src` | External stylesheets |
| `frame_src` | Iframes |
| `worker_src` | Web workers |
| `manifest_src` | Web app manifests |

Scalev's own domains are already allowed, so a page that only uses `window.Scalev` needs no entries. Use HTTPS dependencies, pin exact versions where possible, and retain integrity attributes. Relative assets resolve against the public page URL; importing HTML does not upload local CSS, JavaScript, font, or image files.

## Next steps

- [HTML Mode runtime](/docs/html-mode-runtime) documents every `window.Scalev` method, its payload, and its response.
- [HTML Mode checkout success types](/docs/html-mode-checkout-success-paths) covers where to send the buyer after `Scalev.checkout.createOrder()` succeeds.
- [Example prompt](/docs/example-prompt) is the prompt the dashboard generates for AI tools.
