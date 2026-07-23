---
title: "Auth"
excerpt: "Use Storefront API keys, guest cart tokens, and customer JWTs from a browser storefront."
deprecated: false
hidden: false
metadata:
  robots: index
---
Storefront API uses three browser-safe identity layers:

- `X-Scalev-Storefront-Api-Key` identifies the store and allows anonymous public storefront routes.
- `X-Scalev-Guest-Token` keeps the same guest cart across page reloads.
- `Authorization: Bearer <customer_access_token>` authenticates a signed-in customer on `/customers/me/*`.

These layers are intentionally separate. The Storefront API key is publishable and selects the storefront. It is not account authorization.

## Storefront API key

A valid Storefront API key only enables runtime access when the business has an active Basic, Pro, or Ultimate plan. Free, Lite, inactive, or unpaid businesses can still configure keys and allowed origins, but public Storefront API calls return the same `Store not found` response as an unknown store or invalid key.

Public storefront routes require:

```text
X-Scalev-Storefront-Api-Key: sfpk_...
```

Use this header on anonymous Storefront API routes under:

```text
/v3/stores/{store_id}/public/*
```

Do not use a business API key in browser JavaScript. Business API keys are secret credentials for server-side integrations and dashboard setup flows.

## Guest cart token

Guest cart routes return and accept:

```text
X-Scalev-Guest-Token: 7e7f8c12-2e1d-4b31-97ad-5ca4f8d1c2d0
```

You get this token from the first guest cart response. Call `GET /public/cart` or `POST /public/cart/items` without a guest token, then read `X-Scalev-Guest-Token` from the response headers.

```js
const response = await fetch(
  `https://api.scalev.com/v3/stores/${storeId}/public/cart`,
  {
    credentials: "omit",
    headers: {
      "X-Scalev-Storefront-Api-Key": storefrontApiKey,
    },
  }
);

const guestToken = response.headers.get("X-Scalev-Guest-Token");

if (guestToken) {
  localStorage.setItem("scalev_guest_token", guestToken);
}
```

Store the guest token in browser storage and send it on later cart and checkout requests:

```js
const guestToken = localStorage.getItem("scalev_guest_token");

await fetch(`https://api.scalev.com/v3/stores/${storeId}/public/cart/items`, {
  method: "POST",
  credentials: "omit",
  headers: {
    "Content-Type": "application/json",
    "X-Scalev-Storefront-Api-Key": storefrontApiKey,
    ...(guestToken ? { "X-Scalev-Guest-Token": guestToken } : {}),
  },
  body: JSON.stringify({
    type: "variant",
    variant_id: 494535,
    quantity: 1,
  }),
});
```

Use only `X-Scalev-Guest-Token`; `X-Guest-Token` is not part of the v3 Storefront API contract.

## Customer auth model

Anonymous customer auth starts under:

```text
/v3/stores/{store_id}/public/auth/*
```

These routes require `X-Scalev-Storefront-Api-Key` because the browser is not signed in yet.

After login, account routes use the customer JWT:

```text
Authorization: Bearer <customer_access_token>
```

Use the customer JWT on:

```text
/v3/stores/{store_id}/customers/me/*
```

These routes are scoped by the store path and the customer JWT. The Storefront API key is not required there because it is not the account authorization mechanism.

Customer order routes return only the order data a signed-in buyer should see: order identity, public links, status timestamps, payment fields, totals including `gross_revenue`, destination address, shipment fields, customer data, and order lines. They do not return business analytics, net revenue, platform fees, provider internals, CRM history, affiliate data, or raw metadata. The response also keeps the fields used by the Scalev customer portal, including `store.name`, `store.logo`, `store.unique_id`, store display flags, store `payment_accounts` for manual bank transfer instructions, `final_variants`, `status_history`, and dropshipper display totals.

Customer access and refresh tokens are browser-held credentials. Use a strict Content Security Policy, avoid untrusted third-party scripts, keep dependencies current, and sanitize any customer- or merchant-provided HTML before rendering it in the storefront.

## Sign in

Start sign-in with:

```text
POST /v3/stores/{store_id}/public/auth/login
```

Example body:

```json
{
  "email": "customer@example.com",
  "password": "customer-password"
}
```

If the store does not require OTP, the response is `200` with customer tokens:

```json
{
  "access": "eyJ...",
  "refresh": "eyJ...",
  "token_type": "Bearer",
  "expires_in": 900,
  "refresh_expires_in": 2592000
}
```

If the store requires OTP, the response is `200` with a message. Show the one-time-code field and call:

```json
{
  "message": "If this email exists in our system, an OTP has been sent to it."
}
```

```text
POST /v3/stores/{store_id}/public/auth/otp/verify
```

Example body:

```json
{
  "email": "customer@example.com",
  "otp": "123456"
}
```

Successful OTP verification returns customer tokens:

```json
{
  "access": "eyJ...",
  "refresh": "eyJ...",
  "token_type": "Bearer",
  "expires_in": 900,
  "refresh_expires_in": 2592000,
  "store_unique_id": "store_vlzpML8edzxO5roOdV7Oyfn6"
}
```

## Token refresh and logout

Refresh a customer session with:

```text
POST /v3/stores/{store_id}/public/auth/jwt/refresh
```

```json
{
  "refresh": "eyJ..."
}
```

Refresh tokens rotate on every refresh and are single-use. Store the new `refresh` value from the response and discard the previous one. Reusing an already-rotated refresh token revokes that token family and requires a new sign-in.

Revoke tokens with:

```text
POST /v3/stores/{store_id}/public/auth/jwt/blacklist
```

```json
{
  "tokens": ["eyJ..."]
}
```

Successful blacklist responses return `204` with an empty body.

## Password reset

Request a password reset email with:

```text
POST /v3/stores/{store_id}/public/auth/forget-password
```

```json
{
  "email": "customer@example.com"
}
```

For Storefront API requests, password reset email links use this URL contract:

```text
http(s)://<allowed-storefront-host>/reset-password?token=<reset-token>
```

The host and scheme come from the validated browser `Origin` when the request comes from an allowed Storefront API origin. Requests without an `Origin` header fall back to the hosted storefront custom domain and use the same `/reset-password?token=...` path.

Save a new password with:

```text
POST /v3/stores/{store_id}/public/auth/save-password
```

```json
{
  "token": "reset-token-from-email",
  "password": "new-password"
}
```

## Rate limits

Storefront public routes are rate-limited as direct browser/client requests, including requests that send `X-Scalev-Storefront-Api-Key` or `X-Scalev-Guest-Token`. They do not use the machine API key or OAuth app rate-limit bucket.
