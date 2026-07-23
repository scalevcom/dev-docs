---
title: "Introduction"
excerpt: "Build a custom browser-only storefront with Scalev as the commerce backend."
deprecated: false
hidden: false
metadata:
  robots: index
---
Storefront API is the browser-facing API for custom storefronts. Use it when you want to create your own storefront frontend and use Scalev as the backend for catalog, cart, checkout, customer account, delivery location, order, and payment flows.

Storefront API is separate from hosted Storefront settings. Hosted Storefront settings control Scalev-rendered pages, custom domains, homepage and checkout builders, footer pages, OTP, custom HTML, and analytics. Storefront API setup is for API-only storefronts where you own the frontend 100%.

> **Call Storefront API v3 directly from the browser**
>
> Storefront API v3 is designed to be called directly from the browser or end-user client. Do not place Storefront API v3 behind your own backend proxy, reverse proxy, middleware, edge function, serverless function, or pass-through API layer.
>
> The rate limiter for Storefront API v3 is intentionally strict because this API is designed for direct client-side usage. If you proxy these requests, many users may appear to come from the same server IP, which can negatively affect rate limiting, spam detection, duplicate-order protection, and other validation logic.
>
> For headless storefront deployments, treat the browser as the intended caller of Storefront API v3. Use your own backend only for non-Scalev concerns such as admin settings, custom business logic, or private integrations.

> **Subscription requirement**
>
> Storefront API runtime requests are available on active Basic, Pro, or Ultimate plans. Merchants on Free or Lite can still configure the public Store ID, publishable API keys, and allowed origins, but API calls return the same `Store not found` response until the business upgrades or reactivates an eligible plan.

## Recommended reading order

1. Start with this page for the architecture, setup requirements, and endpoint map.
2. Read [Auth](/docs/storefront-api-auth) for Storefront API keys, guest cart tokens, and customer JWTs.
3. Read [Checkout and Payments](/docs/storefront-api-checkout-payments) for shipping, checkout summary, order creation, and payment rendering.
4. Read [Advertising conversion events](/docs/storefront-api-advertising-conversion-events) if the storefront runs Meta, TikTok, or SnackVideo ads.
5. Finish with [Build a storefront](/docs/build-a-browser-only-storefront) as the complete A-Z implementation guide.

## Architecture

A Storefront API storefront can be a static app deployed on Cloudflare Pages, Vercel, Netlify, or any CDN. The browser calls `https://api.scalev.com` directly.

Use `fetch` with `credentials: "omit"` for browser-only Storefront API calls:

```js
await fetch(`https://api.scalev.com/v3/stores/${storeId}/public/items`, {
  credentials: "omit",
  headers: {
    "X-Scalev-Storefront-Api-Key": storefrontApiKey,
  },
});
```

Guest cart continuity uses a browser-managed header token, not cross-site cookies. See [Auth](/docs/storefront-api-auth) for the Storefront API key, guest token, and customer JWT model.

## What to configure

In the dashboard, open the store configuration page and use the **Storefront API** section.

Copy the public Store ID. New integrations should use the store `unique_id`, for example:

```text
store_vlzpML8edzxO5roOdV7Oyfn6
```

Generate a publishable Storefront API key:

```text
sfpk_...
```

Register every browser origin that will call the API:

```text
https://demo.scalev.shop
http://localhost:3000
```

Allowed-origin CORS preflight includes `X-Scalev-Storefront-Api-Key`, `X-Scalev-Guest-Token`, `Authorization`, and `Content-Type`.

## Core endpoints

```text
GET  /v3/stores/{store_id}/public/items
GET  /v3/stores/{store_id}/public/items/count
GET  /v3/stores/{store_id}/public/products/{slug}
GET  /v3/stores/{store_id}/public/bundle-price-options/{slug}
GET  /v3/stores/{store_id}/public/categories
GET  /v3/stores/{store_id}/public/payment-methods

GET  /v3/stores/{store_id}/public/locations/provinces
GET  /v3/stores/{store_id}/public/locations/cities?province_id=31
GET  /v3/stores/{store_id}/public/locations/subdistricts?city_id=3171
GET  /v3/stores/{store_id}/public/locations?search=Cempaka%20Putih
GET  /v3/stores/{store_id}/public/locations/{location_id}/postal-codes

GET  /v3/stores/{store_id}/public/cart
POST /v3/stores/{store_id}/public/cart/items
PATCH /v3/stores/{store_id}/public/cart/items/{item_id}
DELETE /v3/stores/{store_id}/public/cart/items/{item_id}

POST /v3/stores/{store_id}/public/checkout/shipping-options
POST /v3/stores/{store_id}/public/checkout/summary
POST /v3/stores/{store_id}/public/checkout
GET  /v3/stores/{store_id}/public/orders/{secret_slug}
PATCH /v3/stores/{store_id}/public/orders/{secret_slug}
POST /v3/stores/{store_id}/public/orders/{secret_slug}/payment
POST /v3/stores/{store_id}/public/orders/{secret_slug}/transfer-proof-upload
POST /v3/stores/{store_id}/public/discount-codes/check

POST /v3/stores/{store_id}/public/analytics/meta/events
POST /v3/stores/{store_id}/public/analytics/tiktok/events
POST /v3/stores/{store_id}/public/analytics/snackvideo/events
```

Location search uses cursor pagination. When `has_next` is `true`, use `next_cursor` to fetch the next page.

## Browser-only checkout flow

1. Load catalog with `GET /public/items`, `GET /public/categories`, and detail routes.
2. Create or read the guest cart with `GET /public/cart`; store the returned `X-Scalev-Guest-Token`.
3. Send `X-Scalev-Guest-Token` on cart add, update, remove, checkout, and later cart reads.
4. Discover checkout options with `GET /public/payment-methods` and the public location/postal-code endpoints.
5. List shipping options with `POST /public/checkout/shipping-options`. Direct typed `items` are the item source when supplied; otherwise pass `X-Scalev-Guest-Token` for the guest cart.
6. Recompute totals with `POST /public/checkout/summary` after the shopper picks a courier service and payment method. The API ignores client-supplied `shipping_cost` and recomputes it from the selected courier service, warehouse, payment method, destination, and checkout items.
7. Optionally validate a discount code with `POST /public/discount-codes/check`. Send `{ "code": "..." }` in the request body, along with optional checkout context (`items`, `payment_method`, `destination`, `courier_service_id`, `warehouse_unique_id`, `courier_aggregator_code`, `net_product_price`, `gross_revenue`, `shipping_cost`). Unknown or ineligible codes return `is_eligible: false`; the route only returns `404` when the store cannot be resolved.
8. Create the order with `POST /public/checkout` using direct typed `items`, the guest cart token, or both.
9. Read the order through `GET /public/orders/{secret_slug}` and update buyer-facing fields such as `transferproof_url`, `transfer_time`, or `notes` with `PATCH /public/orders/{secret_slug}`.
10. For manual `bank_transfer`, request a transfer-proof upload URL with `POST /public/orders/{secret_slug}/transfer-proof-upload`, upload the image, then patch the order with the returned `file_url`.
11. Call `POST /public/orders/{secret_slug}/payment`; render the returned or existing payment instructions in your own payment page and use `payment_url` only as a hosted fallback.
12. For customer accounts, start with `/public/auth/login`, then call `/customers/me/*` with the customer JWT.

See [Checkout and Payments](/docs/storefront-api-checkout-payments) for shipping option, summary, and method-specific payment rendering guidance.

## Analytics Conversion API

Use Scalev as the server-side relay for Meta, TikTok, and SnackVideo conversion events from a browser storefront. These calls use the same pixels configured in hosted Storefront analytics, but the Storefront API route selects the store from `/v3/stores/{store_id}` and `X-Scalev-Storefront-Api-Key`; do not send a custom domain to identify the store.

```text
POST /v3/stores/{store_id}/public/analytics/meta/events
POST /v3/stores/{store_id}/public/analytics/tiktok/events
POST /v3/stores/{store_id}/public/analytics/snackvideo/events
```

The endpoints return `204 No Content` after accepting the payload for asynchronous delivery. See [Advertising conversion events](/docs/storefront-api-advertising-conversion-events) for client pixel setup, attribution cookies, event naming, payload examples, and Meta/TikTok deduplication.

## Payment responses

After guest checkout, public order reads, and public payment creation, the response includes the slim order data a storefront needs to show the buyer the next step: order identity, `public_order_url`, `payment_url`, status, totals, the existing `variants` and `bundle_price_options` object maps, line items, shipping details, and payment fields such as the canonical `payment_method`, `payment_account_holder`, `payment_account_number`, `transferproof_url`, and `pg_payment_info`. Virtual accounts use flat method codes such as `va_bca`. The response also includes `payment_link_income` when an E-Payment Link surcharge is charged to the buyer. It intentionally omits internal order IDs, dashboard-only revenue fields, platform fees, payment-status history, and affiliate attribution. In v3, those fields are returned directly in the JSON object, not inside the legacy `data` envelope.

Customer account order routes return a smaller buyer-safe order object for the signed-in customer. It keeps buyer-visible order data and removes dashboard-only details such as business analytics, internal fees, provider internals, CRM history, affiliate data, and raw metadata.

The public payment endpoint is idempotent when payment instructions or `payment_url` already exist.

Payment responses describe how the storefront should render the next payment step. Manual methods such as `bank_transfer` and `cod` can return an empty `pg_payment_info` while the public order carries the buyer-facing instructions to render. Virtual account methods expose provider reference and account details under the provider's `payment_method` object. QRIS responses expose QR data or a QR image payload. E-wallet, card, and invoice methods may expose provider actions or hosted provider URLs. Storefronts should render their own payment page from these fields and use `payment_url` only as a hosted fallback.

## Setup API

The setup endpoints require authenticated business access. Use the public store ID for new clients; legacy numeric store IDs remain accepted.

```text
GET    /v3/stores/{store_id}/public-api-keys
POST   /v3/stores/{store_id}/public-api-keys
DELETE /v3/stores/{store_id}/public-api-keys/{id}

GET    /v3/stores/{store_id}/storefront/allowed-origins
POST   /v3/stores/{store_id}/storefront/allowed-origins
DELETE /v3/stores/{store_id}/storefront/allowed-origins/{id}
```
