---
title: "Landing Pages API"
excerpt: "Create and manage Scalev landing pages through API v3."
deprecated: false
hidden: false
metadata:
  robots: index
---
Use the Landing Pages API when your backend needs to create, list, update, publish, or delete Scalev landing pages. These are authenticated business endpoints. Do not call them from browser JavaScript because they require a business API key or OAuth access token.

The endpoints can return Builder and HTML Mode pages. This guide documents the HTML Mode payload because it is the recommended API payload for creating page code directly. Builder request payloads are intentionally not documented and will remain that way.

## Builder order-bump compatibility

When you read a Builder page, its `form_display.order_bumps` response can contain
up to three offers. Each offer has a stable `key`, its product variant or bundle
price option, and its presentation settings. Use `enabled` and `available` to
check whether an offer is enabled and its catalog item is available.

Treat the response values separately:

- `null` identifies a legacy single-bump form. Retain the legacy singleton fields
  when reading this response.
- `[]` means the form has no configured order bumps.
- A non-empty array contains the configured offers, including disabled offers.

`form_display.form_position` identifies each collection offer as
`order_bump:<key>`. Preserve these stable keys when processing page versions or
checkout recovery data. Checkout-intent `selected_order_bump_keys` records the
selected offers for recovery; the keys do not authorize products or set prices.
Selected items and their quantities remain part of the checkout items.

This collection is Builder-only. Do not send `order_bumps` in an HTML Mode
payload; HTML Mode keeps its existing singleton behavior. This guide continues
to cover HTML Mode authoring rather than Builder layout payloads.

## Auth

Send a business API key or OAuth access token in the `Authorization` header:

```bash
curl https://api.scalev.com/v3/pages \
  -H "Authorization: Bearer $SCALEV_API_KEY"
```

Required scopes:

| Action | Scope |
| --- | --- |
| List pages and displays | `page:list` |
| Read one page or display | `page:read` |
| Create a page | `page:create` |
| Update metadata, publish state, tags, and displays | `page:update` |
| Delete a page | `page:delete` |
| List stores | `store:list` |
| List payment methods, sales people, and product knowledge | `store:read` |
| List store products and variants | `product:list`, `product:read` |
| List store bundles and bundle price options | `bundle:list`, `bundle:read` |
| List payment accounts | `payment_account:list` |
| Manage analytics pixels and GTM containers | `fb_pixel:*`, `tiktok_pixel:*`, `kwai_pixel:*`, `gtm:*` |

## Endpoints

```text
GET    /v3/pages
POST   /v3/pages
GET    /v3/pages/simplified
GET    /v3/pages/tags
GET    /v3/pages/{page_id}
PATCH  /v3/pages/{page_id}
DELETE /v3/pages/{page_id}
GET    /v3/pages/{page_id}/public
POST   /v3/pages/{page_id}/update-tags

GET    /v3/pages/{page_id}/page-displays
POST   /v3/pages/{page_id}/page-displays
GET    /v3/pages/{page_id}/page-displays/{display_id}
DELETE /v3/pages/{page_id}/page-displays/{display_id}

GET    /v3/stores/simplified
GET    /v3/stores/{store_id}/products
GET    /v3/stores/{store_id}/variants/{variant_id}
GET    /v3/stores/{store_id}/bundles
GET    /v3/stores/{store_id}/bundles/{bundle_id}
GET    /v3/stores/{store_id}/bundle-price-options/{id}
GET    /v3/stores/{store_id}/sales-people
GET    /v3/stores/{store_id}/payment-methods
GET    /v3/stores/{store_id}/payment-accounts
GET    /v3/stores/{store_id}/pages

GET    /v3/fb-standard-events
GET    /v3/tiktok-standard-events
GET    /v3/kwai-standard-events
GET    /v3/fb-pixels
POST   /v3/fb-pixels
GET    /v3/fb-pixels/{id}
PATCH  /v3/fb-pixels/{id}
DELETE /v3/fb-pixels/{id}
GET    /v3/tiktok-pixels
POST   /v3/tiktok-pixels
GET    /v3/tiktok-pixels/{id}
PATCH  /v3/tiktok-pixels/{id}
DELETE /v3/tiktok-pixels/{id}
GET    /v3/kwai-pixels
POST   /v3/kwai-pixels
GET    /v3/kwai-pixels/{id}
PATCH  /v3/kwai-pixels/{id}
DELETE /v3/kwai-pixels/{id}
GET    /v3/gtm
POST   /v3/gtm
GET    /v3/gtm/{id}
PATCH  /v3/gtm/{id}
DELETE /v3/gtm/{id}
```

List endpoints use cursor pagination. If `has_next` is `true`, send `next_cursor` on the next request. If `has_previous` is `true`, send `previous_cursor` to move backward.

## Complete setup flow

1. List stores with `GET /v3/stores/simplified`. Use the returned numeric store `id` as `{store_id}` for authenticated business-scoped setup endpoints.
2. List sellable items for the store with `GET /v3/stores/{store_id}/products` and `GET /v3/stores/{store_id}/bundles`. Use product `variants[].id` for `form_display.variant_ids`, or bundle `bundle_price_options[].id` for `form_display.bundle_price_option_ids`.
3. Fetch one item if you need details with `GET /v3/stores/{store_id}/variants/{variant_id}` or `GET /v3/stores/{store_id}/bundle-price-options/{id}`.
4. List existing analytics records with `GET /v3/fb-pixels`, `GET /v3/tiktok-pixels`, `GET /v3/kwai-pixels`, and `GET /v3/gtm`. Create missing records with the matching `POST` endpoint.
5. List valid event names with `GET /v3/fb-standard-events`, `GET /v3/tiktok-standard-events`, and `GET /v3/kwai-standard-events?type=client|server`.
6. If `after_submit_event` is `direct_to_whatsapp` with fixed assignment, list handlers with `GET /v3/stores/{store_id}/sales-people` and send the selected `id` as `store_sales_person_id`.
7. Create or update the page display. Send Scalev record IDs in `*_pixel_ids`, `gtm_id`, `variant_ids`, `bundle_price_option_ids`, and `store_sales_person_id`.
8. Publish by creating the page with `is_published: true`, or by patching `current_page_display_id` on `PATCH /v3/pages/{page_id}`.

Custom domain setup and business-user assignment management are not part of this public v3 Landing Pages release.

## HTML Mode display payload

HTML Mode uses `render_mode: "html_mode"`, one authoritative `html_document`, and a separately stored `csp_policy`.

Send a complete document with its head, body, styles, and scripts. A non-whitespace `html_document` is rendered exclusively; accompanying legacy code is not appended. Reads return the authored source without the injected runtime, analytics, or capability tokens.

Older pages can have null, empty, or whitespace-only `html_document`. Those pages still render `additional_head_code`, `html_code`, `css_code`, and `js_code`. Reading or validating them does not migrate storage. Every HTML Mode content save using a legacy display snapshot automatically assembles a new unified document; no opt-in is required. Historical versions keep their own source. New integrations should write `html_document` directly.

Existing apps and AI agents can keep sending `html_code`, `css_code`, and `js_code`, including when the preceding version uses `html_document`. These request fields remain supported. Send all three for a complete legacy snapshot, using an empty string for a blank section, and include `additional_head_code` when you need head content. Omitted code sections in a new display snapshot are empty. Do not include a nonempty `html_document` with a legacy edit: the unified document takes precedence. Reading a page does not backfill legacy fields from its unified source.

For example, send this content alongside the existing display settings when creating a version:

```json
{
  "render_mode": "html_mode",
  "html_code": "<main>Updated by an existing integration</main>",
  "css_code": "main { padding: 24px; }",
  "js_code": "console.log(Scalev.data.get());",
  "additional_head_code": "<meta name=\"theme-color\" content=\"#09AFED\">"
}
```

Settings-only writes preserve the document. Clearing an already migrated document returns `422`. To save a deliberately blank page, send `<!doctype html><html><head></head><body></body></html>`.

External script URLs, stylesheet links, script attributes, import maps, and JSON data blocks are preserved. Permissions remain explicit and directive-specific in `csp_policy`. CSP meta tags in authored source are retained but excluded from execution with a validation warning. Reserved runtime IDs, such as `scalev-runtime` and `scalev-data`, cannot be authored.

Authored SEO entries and document language take precedence over managed defaults. The dashboard's SEO/language controls update the corresponding source nodes. API callers changing authored SEO should edit those nodes in `html_document`.

Do not send Builder-only display fields such as `schema_version`, `banner`, `header`, `general`, `sidebar`, or `main` for HTML Mode. Scalev fills acceptable defaults internally. Responses can still include those fields.

Include the analytics event fields even when they are empty:

```json
{
  "render_mode": "html_mode",
  "html_document": "<!doctype html><html lang=\"id\"><head><meta name=\"theme-color\" content=\"#09AFED\"><style>main { padding: 32px; }</style></head><body><main><h1>Launch offer</h1></main></body></html>",
  "csp_policy": {},
  "meta": {
    "lang": "id",
    "title": "Launch offer",
    "description": "A short offer description",
    "favicon": "https://cdn.example.com/favicon.ico",
    "thumbnail": "https://cdn.example.com/social-image.jpg",
    "isDisabledSearchEngineCrawler": false
  },
  "fb_pixel_ids": [],
  "tiktok_pixel_ids": [],
  "kwai_client_pixel_ids": [],
  "kwai_server_pixel_ids": [],
  "gtm_id": null,
  "onload_fb_events": [],
  "onload_tiktok_events": [],
  "onload_kwai_client_events": [],
  "onload_kwai_server_events": [],
  "fb_events_onload_parameters": {},
  "tiktok_events_onload_parameters": {},
  "kwai_client_events_onload_parameters": {},
  "kwai_server_events_onload_parameters": {}
}
```

Use the [HTML Mode runtime](/docs/html-mode-runtime) for checkout, analytics,
prefill, and page context.

## Analytics pixels and events

Attach existing analytics pixels to a page display by sending the Scalev pixel record IDs on the display payload. These are the numeric Scalev record IDs from `GET /v3/fb-pixels`, `GET /v3/tiktok-pixels`, and `GET /v3/kwai-pixels`, not the provider pixel code such as a Meta Pixel ID.

| Field | Meaning |
| --- | --- |
| `fb_pixel_ids` | Scalev record IDs for Meta/Facebook pixels |
| `tiktok_pixel_ids` | Scalev record IDs for TikTok pixels |
| `kwai_client_pixel_ids` | Scalev record IDs for SnackVideo browser pixels |
| `kwai_server_pixel_ids` | Scalev record IDs for SnackVideo Events API pixels |

Use `POST /v3/fb-pixels`, `POST /v3/tiktok-pixels`, `POST /v3/kwai-pixels`, and `POST /v3/gtm` when the business does not already have the record. Use `GET /v3/gtm` to find the `gtm_id` to send on the display payload.

Only pixels owned by the same business are attached. IDs from another business or missing pixel records are ignored and will not appear in the response. Send an empty array when the new display should have no pixels for that provider.

Configure automatic page-load events on the same page display:

```json
{
  "fb_pixel_ids": [101],
  "tiktok_pixel_ids": [202],
  "kwai_client_pixel_ids": [303],
  "kwai_server_pixel_ids": [404],
  "gtm_id": 505,
  "onload_fb_events": ["PageView", "ViewContent"],
  "onload_tiktok_events": ["ViewContent"],
  "onload_kwai_client_events": ["contentView"],
  "onload_kwai_server_events": ["EVENT_CONTENT_VIEW"],
  "fb_events_onload_parameters": {
    "ViewContent": { "content_name": "Launch offer" }
  },
  "tiktok_events_onload_parameters": {},
  "kwai_client_events_onload_parameters": {},
  "kwai_server_events_onload_parameters": {}
}
```

HTML Checkout submit events are configured inside `page_display.form_display`, not on the top-level page display:

```json
{
  "form_display": {
    "store_id": 123,
    "variant_ids": [456],
    "bundle_price_option_ids": [],
    "after_submit_event": "success_page",
    "onsubmit_fb_events": ["InitiateCheckout"],
    "onsubmit_tiktok_events": ["InitiateCheckout"],
    "onsubmit_kwai_client_events": ["formSubmit"],
    "onsubmit_kwai_server_events": ["EVENT_FORM_SUBMIT"],
    "fb_events_onsubmit_parameters": {},
    "tiktok_events_onsubmit_parameters": {},
    "kwai_client_events_onsubmit_parameters": {},
    "kwai_server_events_onsubmit_parameters": {}
  }
}
```

Read responses return full pixel objects under `fb_pixels`, `tiktok_pixels`, `kwai_client_pixels`, and `kwai_server_pixels`, not the ID arrays. When creating another display from a read response, use each pixel object's `id` value in the matching `*_pixel_ids` request field.

## Create an HTML Sales page

Omit `form_display` for a regular HTML landing page without checkout.

```bash
curl -X POST https://api.scalev.com/v3/pages \
  -H "Authorization: Bearer $SCALEV_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "API HTML Sales Page",
    "slug": "api-html-sales-page",
    "is_published": true,
    "page_display": {
      "render_mode": "html_mode",
      "html_document": "<!doctype html><html lang=\"id\"><head><style>main { padding: 32px; }</style></head><body><main><h1>Launch offer</h1></main></body></html>",
      "csp_policy": {},
      "meta": { "lang": "id" },
      "fb_pixel_ids": [],
      "tiktok_pixel_ids": [],
      "kwai_client_pixel_ids": [],
      "kwai_server_pixel_ids": [],
      "gtm_id": null,
      "onload_fb_events": [],
      "onload_tiktok_events": [],
      "onload_kwai_client_events": [],
      "onload_kwai_server_events": [],
      "fb_events_onload_parameters": {},
      "tiktok_events_onload_parameters": {},
      "kwai_client_events_onload_parameters": {},
      "kwai_server_events_onload_parameters": {}
    }
  }'
```

The response returns the page directly, not inside the old `data` envelope.

## Create an HTML Checkout page

Add `page_display.form_display` when the page should create orders. Checkout pages require:

- `store_id`
- at least one `variant_ids` item or one `bundle_price_option_ids` item

After a page has a saved `store_id`, every new display for that page must keep the same checkout store. A display with a different `form_display.store_id`, or a display without store context, is rejected.

```json
{
  "name": "API HTML Checkout Page",
  "slug": "api-html-checkout-page",
  "is_published": true,
  "page_display": {
    "render_mode": "html_mode",
    "html_document": "<!doctype html><html lang=\"id\"><head></head><body><main><h1>Checkout offer</h1><button id=\"buy\">Buy now</button></main></body></html>",
    "csp_policy": {},
    "meta": { "lang": "id" },
    "fb_pixel_ids": [101],
    "tiktok_pixel_ids": [202],
    "kwai_client_pixel_ids": [303],
    "kwai_server_pixel_ids": [404],
    "gtm_id": 505,
    "onload_fb_events": [],
    "onload_tiktok_events": [],
    "onload_kwai_client_events": [],
    "onload_kwai_server_events": [],
    "fb_events_onload_parameters": {},
    "tiktok_events_onload_parameters": {},
    "kwai_client_events_onload_parameters": {},
    "kwai_server_events_onload_parameters": {},
    "form_display": {
      "store_id": 123,
      "variant_ids": [456],
      "bundle_price_option_ids": [],
      "after_submit_event": "success_page",
      "onsubmit_fb_events": ["InitiateCheckout"],
      "onsubmit_tiktok_events": ["InitiateCheckout"],
      "onsubmit_kwai_client_events": ["formSubmit"],
      "onsubmit_kwai_server_events": ["EVENT_FORM_SUBMIT"],
      "fb_events_onsubmit_parameters": {},
      "tiktok_events_onsubmit_parameters": {},
      "kwai_client_events_onsubmit_parameters": {},
      "kwai_server_events_onsubmit_parameters": {}
    }
  }
}
```

For checkout behavior after order creation, use these `after_submit_event` values:

| Value | Required fields |
| --- | --- |
| `success_page` | None |
| `direct_to_whatsapp` | None for rotator; when `handler_assignment` is `fixed`, send `store_sales_person_id` |
| `direct_to_custom_whatsapp` | `custom_phone` |
| `other_page` | `other_page_id` |
| `custom_url` | `custom_url` |
| `order_page` | None |

For a new checkout form, omitting `after_submit_event` selects `success_page` (payment instructions), and omitting `handler_assignment` selects `rotator`. When you create a new form display for an existing page, omitted destination, WhatsApp recipient, assignment, and chat-template settings retain the latest saved display's values. Explicit values take precedence.

The separate page-level `is_sending_email_invoice` boolean is deprecated and ignored. It remains accepted and is echoed as stored for compatibility, but it no longer suppresses invoice email. Store notification settings still control email delivery. The legacy `is_sending_email_invoice` value in the `after_submit_event` enum is also retained for compatibility; use one of the destinations above for new forms.

Read [HTML Mode checkout success paths](/docs/html-mode-checkout-success-paths) for the runtime behavior of each path.

## Update a page

`PATCH /v3/pages/{page_id}` updates page metadata and publish state.

```json
{
  "name": "Updated page name",
  "slug": "updated-page-slug"
}
```

To publish a specific display:

```json
{
  "is_published": true,
  "current_page_display_id": 987
}
```

To unpublish:

```json
{
  "is_published": false,
  "current_page_display_id": null
}
```

## Create and publish a new display

To change HTML, CSS, JavaScript, pixels, or checkout context, create a new page display:

If the page already has a saved store, the new display must include the same `form_display.store_id`; omitting store context is rejected.

```bash
curl -X POST https://api.scalev.com/v3/pages/123/page-displays \
  -H "Authorization: Bearer $SCALEV_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "render_mode": "html_mode",
    "html_document": "<!doctype html><html lang=\"id\"><head></head><body><main><h1>New version</h1></main></body></html>",
    "csp_policy": {},
    "meta": { "lang": "id" },
    "fb_pixel_ids": [],
    "tiktok_pixel_ids": [],
    "kwai_client_pixel_ids": [],
    "kwai_server_pixel_ids": [],
    "gtm_id": null,
    "onload_fb_events": [],
    "onload_tiktok_events": [],
    "onload_kwai_client_events": [],
    "onload_kwai_server_events": [],
    "fb_events_onload_parameters": {},
    "tiktok_events_onload_parameters": {},
    "kwai_client_events_onload_parameters": {},
    "kwai_server_events_onload_parameters": {}
  }'
```

The response includes the new display `id`. Publish it with:

```bash
curl -X PATCH https://api.scalev.com/v3/pages/123 \
  -H "Authorization: Bearer $SCALEV_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "is_published": true,
    "current_page_display_id": 987
  }'
```

## Tags and delete

Replace tags with:

```json
{
  "tags": ["Promo", "Checkout"]
}
```

Call:

```text
POST /v3/pages/{page_id}/update-tags
```

Delete a page with:

```text
DELETE /v3/pages/{page_id}
```

Successful delete responses return `204 No Content`.
