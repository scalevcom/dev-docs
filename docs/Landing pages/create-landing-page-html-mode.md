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
5. Review the split code in **Body HTML**, **CSS**, **JavaScript**, and **Additional Head Code**. You can edit any field directly; the preview pane updates as you type.
6. Open the **Security** tab and add every external domain the page uses. Requests to domains that are not listed are blocked.
7. Upload images in the **Media** tab and copy each file URL into your HTML.
8. Set the page name, slug, and SEO fields in the **Setting** tab, then save and publish.

**Export** downloads the current page as one merged HTML document, which is useful for handing the page back to an AI tool for another round of edits.

### What Import HTML keeps

Import accepts one complete document and splits it into the page display fields:

| Source in your document | Where it lands |
| --- | --- |
| Body markup | **Body HTML** |
| `<style>` inside `<body>` | **CSS** |
| `<script>` inside `<body>` | **JavaScript** |
| Anything left in `<head>` | **Additional Head Code** |
| `<title>`, `meta description`, `og:title`, `og:description`, `og:image`, favicon `link`, `meta robots`, `<html lang>` | Page settings |

Scalev removes the head tags it recognizes so they do not compete with managed tags. A `<style>` block that stays in `<head>` is kept in **Additional Head Code** and still renders; move it into the body if you want it in the CSS field.

## Create the page with the API

`POST /v3/pages` creates the page and its first display in one call. HTML Mode uses `render_mode: "html_mode"` with `html_code`, `css_code`, `js_code`, `additional_head_code`, and `csp_policy`.

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
      "html_code": "<main><h1>Launch offer</h1></main>",
      "css_code": "main { padding: 32px; }",
      "js_code": "",
      "csp_policy": {},
      "meta": { "lang": "id" }
    }
  }'
```

`html_code` is body-only. Add `page_display.form_display` with `store_id` and the selected items when the page must create orders. This example leaves out the analytics fields; send them as shown in [Landing Pages API](/docs/landing-pages-api), including when they are empty. That guide also covers the full payload and how to publish a new display.

## Write the page code

Keep these rules so the document imports cleanly and runs on the hosted page:

- Put page markup in the body. Do not send `<!doctype>`, `<html>`, `<head>`, or `<body>` in `html_code`.
- Keep extra head tags in **Additional Head Code**. Scalev owns SEO tags, favicon, crawler settings, pixels, domains, slug, and publishing.
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

Scalev's own domains are already allowed, so a page that only uses `window.Scalev` needs no entries.

## Next steps

- [HTML Mode runtime](/docs/html-mode-runtime) documents every `window.Scalev` method, its payload, and its response.
- [HTML Mode checkout success types](/docs/html-mode-checkout-success-paths) covers where to send the buyer after `Scalev.checkout.createOrder()` succeeds.
- [Example prompt](/docs/example-prompt) is the prompt the dashboard generates for AI tools.
