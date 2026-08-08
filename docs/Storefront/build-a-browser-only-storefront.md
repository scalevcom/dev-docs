---
title: "Build a storefront"
excerpt: "Follow the complete implementation guide for a custom Storefront API frontend."
deprecated: false
hidden: false
metadata:
  robots: index
---
Storefront API v3 lets you build your own storefront UI while Scalev handles catalog, carts, checkout, customer accounts, delivery locations, orders, and payment instructions. Use this as the complete A-Z implementation guide after you understand the [Storefront API overview](/docs/storefront-api-overview), [auth model](/docs/storefront-api-auth), [checkout flow](/docs/storefront-api-checkout-payments), and optional [advertising conversion events](/docs/storefront-api-advertising-conversion-events).

A Storefront API storefront can be hosted as a static frontend, for example on Cloudflare Pages, Vercel, Netlify, or any CDN, without building a custom backend or same-origin proxy. The frontend calls `https://api.scalev.com` directly.

> **Call Storefront API v3 directly from the browser**
>
> Storefront API v3 is designed to be called directly from the browser or end-user client. Do not place Storefront API v3 behind your own backend proxy, reverse proxy, middleware, edge function, serverless function, or pass-through API layer.
>
> The rate limiter for Storefront API v3 is intentionally strict because this API is designed for direct client-side usage. If you proxy these requests, many users may appear to come from the same server IP, which can negatively affect rate limiting, spam detection, duplicate-order protection, and other validation logic.
>
> For headless storefront deployments, treat the browser as the intended caller of Storefront API v3. Use your own backend only for non-Scalev concerns such as admin settings, custom business logic, or private integrations.

## Architecture

Use these rules for storefront frontends:

- Use the store `unique_id` in public storefront runtime URLs.
- Use a publishable storefront public API key in frontend code.
- Send the key as `X-Scalev-Storefront-Api-Key` for `/public/*` endpoints.
- Send the customer JWT as `Authorization: Bearer <access>` for `/customers/me/*` endpoints.
- Store and resend `X-Scalev-Guest-Token` for guest cart flows.
- Do not expose business API keys in frontend code.
- Do not build a custom backend endpoint for catalog, cart, checkout, payment instructions, order tracking, or customer account flows.

All endpoint paths below are relative to:

```text
https://api.scalev.com/v3/stores/{store_id}
```

## Setup checklist

1. Create or retrieve a storefront public API key.
2. Register the storefront origin, for example `https://demo.example.com`, as an allowed origin.
3. Configure the frontend with:
   - `SCALEV_API_BASE=https://api.scalev.com`
   - `SCALEV_STORE_UNIQUE_ID=<store_unique_id>`
   - `SCALEV_STOREFRONT_API_KEY=<publishable_storefront_key>`
4. Serve the frontend from the registered origin.
5. Make API calls directly from the browser.
6. If the storefront runs ads, wire browser pixels and Scalev server conversion events with shared event IDs. See [Advertising conversion events](/docs/storefront-api-advertising-conversion-events).

Storefront runtime uses the store `unique_id`. Storefront setup endpoints are authenticated business endpoints. The setup endpoints may accept legacy numeric store IDs for compatibility, but the storefront frontend should be configured with the store `unique_id`.

## Minimal fetch helpers

Use one helper for anonymous public storefront routes:

```ts
const API_BASE = "https://api.scalev.com";
const STORE_ID = "store_xxx";
const STOREFRONT_KEY = "sfpk_xxx";

async function storefrontFetch(path: string, init: RequestInit = {}) {
  const headers = new Headers(init.headers);
  headers.set("Accept", "application/json");
  headers.set("X-Scalev-Storefront-Api-Key", STOREFRONT_KEY);

  return fetch(`${API_BASE}/v3/stores/${STORE_ID}${path}`, {
    ...init,
    credentials: "omit",
    headers,
  });
}
```

Use another helper for signed-in customer routes:

```ts
async function customerFetch(
  path: string,
  accessToken: string,
  init: RequestInit = {}
) {
  const headers = new Headers(init.headers);
  headers.set("Accept", "application/json");
  headers.set("Authorization", `Bearer ${accessToken}`);

  return fetch(`${API_BASE}/v3/stores/${STORE_ID}${path}`, {
    ...init,
    credentials: "omit",
    headers,
  });
}
```

Persist the guest cart token from the first guest cart response:

```ts
const response = await storefrontFetch("/public/cart");
const guestToken = response.headers.get("x-scalev-guest-token");

if (guestToken) {
  localStorage.setItem("scalev_guest_token", guestToken);
}
```

Resend the guest token on later guest cart and guest checkout calls:

```ts
const headers = new Headers({
  "Content-Type": "application/json",
});

const guestToken = localStorage.getItem("scalev_guest_token");

if (guestToken) {
  headers.set("X-Scalev-Guest-Token", guestToken);
}

await storefrontFetch("/public/cart/items", {
  method: "POST",
  headers,
  body: JSON.stringify({
    type: "variant",
    variant_id: 494535,
    quantity: 1,
  }),
});
```

## Catalog flow

Use this catalog sequence:

1. `GET /public/items/count`
2. `GET /public/items`
3. Use `entity_type` to distinguish:
   - `product`
   - `bundle_price_option`
4. For product details, call `GET /public/products/{slug}`.
5. For bundle price option details, call `GET /public/bundle-price-options/{slug}`.
6. For variant pricing, call `GET /public/variants/pricing?ids=...`.
7. For availability, call `GET /public/variants/{variant_id}/availability`.

Use `variant_id` for product variants. Use `bundle_price_option_id` for bundle price options. Both can be placed in cart and checkout payloads with the typed item union.

## Checkout item shapes

Use this shape for product variants:

```json
{
  "type": "variant",
  "variant_id": 494535,
  "quantity": 1
}
```

Use this shape for bundle price options:

```json
{
  "type": "bundle_price_option",
  "bundle_price_option_id": 31925,
  "quantity": 1
}
```

## Guest cart and guest checkout flow

Use this flow for anonymous buyers:

1. `GET /public/cart`
   - save `x-scalev-guest-token`
2. `POST /public/cart/items`
3. `PATCH /public/cart/items/{item_id}`
4. `DELETE /public/cart/items/{item_id}`
5. `POST /public/checkout/shipping-options`
6. `POST /public/checkout/summary`
7. `POST /public/checkout`
8. `GET /public/orders/{secret_slug}`
9. For manual `bank_transfer`, `POST /public/orders/{secret_slug}/transfer-proof-upload`, upload the image, then `PATCH /public/orders/{secret_slug}` with `transferproof_url`.
10. `POST /public/orders/{secret_slug}/payment`

Checkout source behavior:

- If `items` is supplied, the order is created from direct `items`.
- If `items` is omitted, the order is created from the guest cart referenced by `X-Scalev-Guest-Token`.
- If both direct `items` and `X-Scalev-Guest-Token` are supplied, direct `items` is the source and the guest cart is cleared after successful order creation.

For Meta, TikTok, and SnackVideo conversion tracking, fire checkout and purchase events only after the related checkout API call succeeds. See [Advertising conversion events](/docs/storefront-api-advertising-conversion-events).

## Customer auth flow

Call:

```text
POST /public/auth/login
```

If the response contains `access` and `refresh`, login is complete.

If the response is an OTP challenge, show an OTP input and call:

```text
POST /public/auth/otp/verify
```

Token handling:

- Store `access` for authenticated customer calls.
- Store `refresh` if you implement persistent sessions.
- Refresh tokens are single-use.
- After calling refresh, discard the old refresh token and store the new one.
- Logout uses `POST /public/auth/jwt/blacklist`.

Blacklist the customer tokens with:

```json
{
  "tokens": ["<access>", "<refresh>"]
}
```

## Customer account flow

Use these customer endpoints in the natural account UI order:

1. `GET /customers/me`
2. `PATCH /customers/me`
3. `POST /customers/me/set-new-password`
4. `GET /customers/me/addresses`
5. `POST /customers/me/addresses`
6. `GET /customers/me/addresses/{address_id}`
7. `PATCH /customers/me/addresses/{address_id}`
8. `DELETE /customers/me/addresses/{address_id}`

## Customer cart and checkout flow

Use this flow for signed-in customers:

1. `GET /customers/me/cart`
2. `POST /customers/me/cart/items`
3. `PATCH /customers/me/cart/items/{item_id}`
4. `DELETE /customers/me/cart/items/{item_id}`
5. `GET /customers/me/checkout/addresses`
6. `GET /customers/me/checkout/payment-methods`
7. `POST /customers/me/checkout/shipping-options`
8. `POST /customers/me/checkout/summary`
9. `POST /customers/me/checkout`
10. `GET /customers/me/orders`
11. `GET /customers/me/orders/{id}`

Customer checkout source behavior:

- If `items` is supplied, the order is created from direct `items`.
- If `items` is omitted, `cart_id` selects the customer cart source.
- If both `items` and `cart_id` are supplied, direct `items` is the source and the referenced cart is cleared after successful order creation.

## Location flow

Use either supported location selection pattern.

Pattern A:

1. Select province: `GET /public/locations/provinces`
2. Select city: `GET /public/locations/cities?province_id=...`
3. Select subdistrict: `GET /public/locations/subdistricts?city_id=...`
4. Postal codes: `GET /public/locations/{location_id}/postal-codes`

Pattern B:

1. Direct search: `GET /public/locations?search=...`
2. Use the returned location or subdistrict directly.
3. Postal codes: `GET /public/locations/{location_id}/postal-codes`

Location responses include only the fields needed for display and the next request:

```json
{
  "province_id": 31,
  "province_name": "DKI Jakarta"
}
```

```json
{
  "city_id": 3171,
  "city_name": "Kota Jakarta Pusat"
}
```

```json
{
  "id": 9090,
  "subdistrict_name": "Gambir",
  "city_name": "Kota Jakarta Pusat",
  "province_name": "DKI Jakarta",
  "display": "Gambir, Kota Jakarta Pusat, DKI Jakarta"
}
```

```json
{
  "postal_code": "10110"
}
```

## Password reset flow

Implement password reset as a link-based browser flow:

1. User enters email.
2. Frontend calls `POST /public/auth/forget-password`.
3. Scalev sends an email link to `/reset-password?token=<reset-token>`.
4. Frontend reads `token` from the URL.
5. User enters new password and confirmation.
6. Frontend calls `POST /public/auth/save-password`.

Do not show a manual reset token input. The frontend should never ask the user to copy and paste the reset token. The reset hostname is selected from the registered allowed origin when the request includes `Origin`.

## Payment rendering

Use these order fields to render the payment page:

- `product_price`
- `product_discount`
- `shipping_cost`
- `shipping_discount`
- `other_income`
- `gross_revenue`
- `payment_method`
- `payment_link_income`
- `payment_account_holder`
- `payment_account_number`
- `transferproof_url`
- `transfer_time`
- `payment_url`
- `pg_payment_info`
- `store.payment_accounts`
- `handler_phone`
- `chat_message`

`payment_method` is canonical; virtual accounts use flat values such as
`va_bca`. Manual bank transfer may use `store.payment_accounts` when no
specific order-level account has been selected. Use `transferproof_url` and
`transfer_time` to show whether the buyer has already submitted payment proof.
Hosted or provider-backed methods may use `payment_url` or `pg_payment_info`.
`payment_link_income` is any PayLink surcharge paid by the buyer, and
`gross_revenue` is the total amount the buyer pays.

See [Checkout and Payments](/docs/storefront-api-checkout-payments) for method-specific rendering rules.

## Customer subscriptions and courses

For customer account pages, use:

- `GET /customers/me/subscriptions`
- `GET /customers/me/subscriptions/{id}`
- `POST /customers/me/subscriptions/{id}/cancel`
- `POST /customers/me/subscriptions/{id}/resume`
- `GET /customers/me/subscription-items/{id}/upgrade`
- `POST /customers/me/subscription-items/{id}/upgrade`
- `GET /customers/me/subscription-items/{id}/downgrade`
- `POST /customers/me/subscription-items/{id}/downgrade`
- `GET /customers/me/variants/{uuid}/course`
- `GET /customers/me/course-sections/{uuid}`
- `GET /customers/me/course-contents/{uuid}`
- `PATCH /customers/me/course-contents/{uuid}`

Course endpoints are entitlement-dependent. A `403` or `404` can mean the customer does not own the course variant, not that the storefront integration is broken.

## Minimal full checkout payload

Use a complete variant checkout payload like:

```json
{
  "items": [
    {
      "type": "variant",
      "variant_id": 494535,
      "quantity": 1
    }
  ],
  "customer_name": "Demo Customer",
  "customer_email": "demo.customer@example.com",
  "customer_phone": "6281234567890",
  "shipping_address": "Jl. Demo Storefront API No. 3",
  "shipping_province": "DKI Jakarta",
  "shipping_city": "Kota Jakarta Pusat",
  "shipping_subdistrict": "Cempaka Putih",
  "shipping_postal_code": "10510",
  "shipping_location_id": 9089,
  "payment_method": "bank_transfer"
}
```

Use a bundle price option checkout payload like:

```json
{
  "items": [
    {
      "type": "bundle_price_option",
      "bundle_price_option_id": 31925,
      "quantity": 1
    }
  ],
  "customer_name": "Demo Customer",
  "customer_email": "demo.customer@example.com",
  "payment_method": "bank_transfer"
}
```

## Agent checklist

An implementation is complete when it can:

- list catalog items
- show product detail
- show bundle price option detail
- check pricing and availability
- persist guest cart using `X-Scalev-Guest-Token`
- add, update, and remove cart items
- select delivery location
- compute shipping options and checkout summary
- create public checkout orders
- show public order status and payment instructions
- create or fetch payment instructions
- login customer with direct-token or OTP branch
- refresh and blacklist JWTs
- manage customer profile and addresses
- use customer cart
- create authenticated checkout orders
- list and view authenticated orders
- send Meta, TikTok, and SnackVideo conversion events through Scalev
- list subscriptions and render entitlement-gated courses when present
- do all of the above from the frontend without a custom backend
