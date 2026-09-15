---
title: "Checkout intents"
excerpt: "Capture unfinished checkouts, recover customer details, and send follow-up emails."
deprecated: false
hidden: false
metadata:
  robots: index
---
A checkout intent records one checkout attempt before an order exists. Use it to save safe form fields as a buyer types, restore a returning buyer's selections, and follow up on contactable abandoned checkouts.

Checkout intent requires an active business subscription that includes the feature. An unavailable subscription returns `403 checkout_intent_not_allowed`. Capture failures should never prevent a buyer from editing a form or placing an order.

## Choose the capture source

| Checkout | Capture path | API key |
| --- | --- | --- |
| Your Storefront API checkout | `/v3/stores/{store_id}/public/checkout-intents` | `X-Scalev-Storefront-Api-Key` |
| Published Scalev page form | `/v3/pages/{page_unique_id}/checkout-intents` | `X-Scalev-Page-Api-Key` |

Use the store or page `unique_id` in the path. A page capture requires the ID of a `MainForm` widget in the current published page. Published HTML Mode pages with checkout form context use `form_widget_id: "html-mode-main-form"`. For your Storefront API checkout, choose one stable form identifier such as `storefront-checkout`.

Call the Scalev API directly from the browser with `credentials: "omit"`. Use the matching API key and an allowed browser origin. A guest-cart token identifies a cart; it does not identify or authorize a checkout intent. Do not start capture in a page editor or preview.

## Start or resume

Generate a random UUID for `client_session_id` and retain it in browser storage scoped to the checkout source. Reuse that UUID across reloads and return visits until the order succeeds. Different forms in the same checkout attempt should share it.

```http
POST /v3/stores/{store_id}/public/checkout-intents
X-Scalev-Storefront-Api-Key: sfpk_...
Content-Type: application/json
```

```json
{
  "client_session_id": "e9b73e6d-b9a6-4e24-9228-4ad39b63e8cc",
  "form_widget_id": "storefront-checkout",
  "recaptcha_token": "<recaptcha-token>",
  "source_url": "https://shop.example/checkout",
  "fields": {
    "customer_name": "Budi Santoso",
    "customer_email": "budi@example.com",
    "customer_phone": "08123456789"
  },
  "items": [{ "type": "variant", "variant_id": 101, "quantity": 2 }]
}
```

Start and resume both require a reCAPTCHA token for action `checkout_intent_start`. The assessment must be valid, match that action, and have a score of at least `0.6`; failures return `422 recaptcha_failed`.

A new intent and a resumed intent both return `201`:

```json
{
  "id": "019c9db5-0fcb-7df3-8c6b-1827b568a61c",
  "form_widget_id": "storefront-checkout",
  "checkout_intent_token": "cit_...",
  "status": "active",
  "last_sequence": 0,
  "started_at": "2026-09-16T01:00:00Z",
  "last_activity_at": "2026-09-16T01:00:00Z",
  "expires_at": "2026-09-17T01:00:00Z"
}
```

The `cit_` token authorizes updates for 24 hours. Start/resume refreshes that window for the same unfinished intent. It returns the existing snapshot sequence without replacing saved fields or items. Send your current snapshot with `last_sequence + 1` after resuming.

A completed session returns `409 checkout_intent_completed`. Rotate the session UUID after order creation succeeds or this conflict occurs. Store the session identity and write capability separately from customer form data. Never put the write capability in a URL, analytics event, or log.

## Save the form snapshot

```http
PATCH /v3/stores/{store_id}/public/checkout-intents/{checkout_intent_id}
X-Scalev-Storefront-Api-Key: sfpk_...
X-Scalev-Checkout-Intent-Token: cit_...
Content-Type: application/json
```

```json
{
  "sequence": 1,
  "fields": {
    "customer_name": "Budi Santoso",
    "customer_email": "budi@example.com",
    "shipping_address": "Jl. Merdeka No. 1",
    "shipping_location_id": 9089,
    "notes": null
  },
  "items": [{ "type": "variant", "variant_id": 101, "quantity": 2 }]
}
```

The same PATCH shape applies under the page capture path with its page API key. Successful updates return `204 No Content`. PATCH does not require reCAPTCHA.

Increment `sequence` for each snapshot. A sequence at or below the stored sequence returns `204` without changing fields or refreshing activity. This prevents delayed requests from overwriting newer input.

Omitted sections and omitted fields remain unchanged. Set a field to `null` to clear it; blank strings normalize to `null`. Present `items` and `custom_fields` arrays replace their previous values. Debounce edits and flush a pending snapshot before order submission where possible.

### Safe captured fields

`fields` accepts customer name, email and phone; shipping address, province, city, subdistrict, location ID and postal code; `payment_method`, `sub_payment_method`, `notes`, `discount_code_code`, and `custom_fields`. Unknown fields return `422 invalid_checkout_intent_fields`.

A custom-field entry has `key`, `label`, and a scalar `value`: string, number, boolean, or null. Up to 50 custom fields and 100 items are accepted. Do not capture passwords, OTPs, card details, CAPTCHA tokens, account credentials, or arbitrary objects inside `fields`.

Items use `{ "type": "variant", "variant_id": 101, "quantity": 2 }` or `{ "type": "bundle_price_option", "bundle_price_option_id": 55, "quantity": 1 }`. The Scalev API resolves eligible item names and prices. Client totals are not authoritative.

Optional `attribution` accepts the documented campaign and advertising attribution fields. Optional `source_url` identifies the checkout page; the Scalev API strips URL fragments and sensitive query parameters. Set it to the actual checkout URL on the configured page/store domain or allowed storefront origin so a recovery link can be issued.

## Complete with an order

Add the optional `checkout_intent_token` to the existing order request:

```json
{ "checkout_intent_token": "cit_..." }
```

Supported order paths:

- `POST /v3/stores/{store_id}/public/checkout`
- `POST /v3/stores/{store_id}/customers/me/checkout`
- `POST /v3/pages/{page_unique_id}/orders`

Use a matching store-scoped intent for storefront checkout and a matching page-scoped intent for a page order. A valid token links the intent when the order commits. Customer contact details from the order close the final autosave gap. A failed order leaves the intent unfinished.

A missing, invalid, expired, mismatched, or already consumed token never blocks an otherwise valid order. The first linked order wins. Checkout response shapes remain the same; clear the browser capture session after success.

## Read contactable intents as a merchant

Use a business API key or merchant OAuth access token in `Authorization: Bearer <token>`. Required scopes are:

| Operation | Scope |
| --- | --- |
| `GET /v3/checkout-intents` | `checkout_intent:list` |
| `GET /v3/checkout-intents/{checkout_intent_id}` | `checkout_intent:read` |
| `POST /v3/checkout-intents/{checkout_intent_id}/follow-up-email` | `checkout_intent:follow_up` |

The API returns only intents with a valid normalized email or phone, within the selected business. Use the normal `b_uid` business selector when an OAuth connection covers multiple businesses. Anonymous attempts are not returned.

Statuses describe the current attempt:

- `active`: unfinished, with activity less than 15 minutes ago.
- `abandoned`: unfinished, with no activity for at least 15 minutes.
- `completed`: an order was successfully created. This does not mean it has been paid.

An abandoned intent can become active again when the buyer resumes. Use `GET /v3/checkout-intents?status=abandoned` for follow-up work. Lists also accept customer search, store/page/form filters, started-at bounds, and timestamp sorting. Follow the returned cursor fields and keep `sort_by` and `sort_direction` unchanged while paging. For `sort_by=completed_at`, unfinished intents use `started_at` as the fallback timestamp. Do not derive page numbers.

The detail response adds safe captured fields, item snapshots, attribution, `recovery_url`, and `recovery_url_expires_at`. Customer contact fields are grouped under `customer`; store-scoped intents have `page: null`. The recovery fields are null for completed intents or when a trusted checkout source is unavailable.

The same merchant operations are discoverable through Scalev MCP. `get` reads the list and detail, and `execute_safe` sends the follow-up email.

## Restore a checkout

A merchant detail response or abandoned webhook can include a ready-to-use `recovery_url`. It preserves the trusted checkout source and includes `checkout_intent_prefill_token=cip_...`. The token expires 30 days after issuance; use `recovery_url_expires_at` from the response. Treat recovery URLs as private customer data.

When the buyer opens the URL:

1. Read the `checkout_intent_prefill_token` query parameter.
2. Call `GET /v3/checkout-intents/prefill?checkout_intent_prefill_token=cip_...`.
3. Restore safe fields from `data` and item references from `data.checkout_intent.items`.
4. Pass the same prefill token in the next start/resume request with a session UUID and fresh reCAPTCHA token. A valid token resumes the exact matching unfinished intent and returns its `cit_` write capability.

The prefill response keeps the top-level `{ "data": ... }` shape. Its `checkout_intent` object contains `id`, canonical `fields`, and enriched `items`. The response retains unavailable saved items with `is_available: false` and `unavailable_reason` of `deleted`, `disabled`, or `out_of_stock`. Recalculate checkout totals and let the buyer resolve unavailable items before submitting an order.

A `cip_` token only reads prefill and cannot authorize PATCH. Invalid or expired prefill reads return `401 invalid_checkout_intent_prefill_token`. An invalid, expired, completed, or mismatched token passed to start/resume falls back to the normal session identity so recovery failure does not block a new checkout.

## Send a follow-up email

Call `POST /v3/checkout-intents/{checkout_intent_id}/follow-up-email` without a request body. A captured customer email is required. Active, abandoned, and completed intents are accepted; select abandoned intents when you want to avoid emailing a buyer who is still editing the checkout.

A `204` response means the email was queued, not delivered. The record becomes `is_email_follow_up_already_sended: true`; another send returns `409 checkout_intent_follow_up_email_already_sended`. Missing email returns `422 checkout_intent_follow_up_email_unavailable`.

Scalev uses the store's customer-email identity and Reply-To rules. You can instead use `recovery_url` in your own follow-up flow when it is present.

## Receive lifecycle webhooks

Subscribe to `checkout_intent.abandoned` and `checkout_intent.completed` through the normal business or app webhook settings. See [webhook events](/docs/webhook-events) for payloads, eligibility, and delivery guarantees.
