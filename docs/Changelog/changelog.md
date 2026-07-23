---
title: "Changelog"
excerpt: "Follow Scalev API product updates and documentation changes."
deprecated: false
hidden: false
metadata:
  robots: index
---
## Canonical payment methods and E-Payment Link

**July 2026** · API, Docs

Order and Storefront APIs now use one canonical `payment_method`. Virtual
accounts use flat values such as `va_bca`; there is no secondary payment
method field in the documented request or response contract. Stores can
offer `payment_link`, and strict two-step checkout can omit
`payment_method` so Scalev routes the buyer to the E-Payment Link selector.
Public order responses expose customer-paid E-Payment Link surcharge income
as `payment_link_income`. Order webhooks expose `payment_link_id` and
`is_from_payment_link` so the origin remains available after a paid order's
`payment_method` changes to the concrete method used.

## Partitioned order IDs

**May 2026** · API, Docs

Business order responses now return the canonical order primary key as a
UUIDv7 string after the partitioned orders-table migration. Use the response
`id` for follow-up business API calls such as `GET /v3/orders/{id}` and
`PATCH /v3/orders/{id}`. Legacy numeric order IDs for migrated orders remain
accepted on ID routes and bulk `ids` payloads for compatibility.

## Storefront API build guide

**May 2026** · Docs, API

Added an end-to-end Storefront API guide for agents and frontend developers
building a custom storefront. The guide covers the direct frontend
architecture, setup checklist, fetch helpers, catalog flow, guest and customer
cart checkout, customer auth, locations, password reset, payment rendering,
subscriptions, course access, and the final implementation checklist.

## Slimmer public order responses

**May 2026** · API, Docs

Storefront API and HTML Mode public order responses now return a smaller
buyer-facing shape. The response still includes `secret_slug`,
`public_order_url`, `payment_url`, status, totals, line items, shipping
display data, payment instructions such as `pg_payment_info`, and the existing
`variants` and `bundle_price_options` object maps, but it no
longer exposes internal order IDs, dashboard revenue fields, platform fees,
payment-status history, or affiliate attribution.

## Storefront API item catalog endpoints

**May 2026** · API, Docs

Storefront API v3 now uses `GET /v3/stores/{store_id}/public/items` and
`GET /v3/stores/{store_id}/public/items/count` for the public catalog feed
because the feed returns both products and bundle price options. Product detail remains
`GET /v3/stores/{store_id}/public/products/{slug}`, and bundle price option detail is
`GET /v3/stores/{store_id}/public/bundle-price-options/{slug}`. Catalog cards use
`entity_type` to distinguish `product` from `bundle_price_option`, while product
`item_type` keeps its product meaning such as `physical` or `digital`. Public cart item
and direct checkout item payloads use `{ "type": "bundle_price_option", "bundle_price_option_id": ... }`
for bundle price options.

## Storefront API v3 checkout endpoint cleanup

**May 2026** · API, Docs

Storefront API v3 checkout order creation now uses one endpoint per
auth mode: `POST /v3/stores/{store_id}/public/checkout` for public checkout
and `POST /v3/stores/{store_id}/customers/me/checkout` for authenticated
customers. The deprecated v3 compatibility checkout paths were removed from
the contract. Direct checkout items now use an explicit typed union for
variants and bundle price options, and the same item source model is used by
shipping options, checkout summary, and final order creation.

## Storefront API physical checkout completion

**May 2026** · API, Docs

Storefront API physical checkout now completes after the documented shipping
option and checkout summary steps. Guest checkout, guest cart checkout, and
authenticated customer checkout summary and confirm recompute the selected
shipping cost on the server from the courier service, warehouse,
destination, payment method, and cart items before creating the order. The
checkout completion responses now all return the same public order response
used by public order reads, so guest checkout, guest cart checkout,
authenticated customer checkout confirm, and hosted public order pages expose
the same order fields. The public discount-code check route is now a `POST`
request with a JSON checkout context body and returns a typed
ineligible response for unknown codes instead of treating the documented path
as missing. Storefront API v3 payment-method discovery and checkout creation
now reject `no_payment` so direct API submissions cannot create no-payment
storefront orders.
OpenAPI now also includes typed customer account, customer cart, customer
order, and customer course contracts. Public order responses continue to
include buyer-facing order links, totals, line items, shipping details, and
payment fields such as `public_order_url`, `payment_url`, and
`pg_payment_info`. Customer-account order responses now use a smaller
buyer-safe order object. It preserves buyer-visible totals such as `gross_revenue`,
plus the minimal Scalev customer portal compatibility fields needed for
existing member order pages, including store name, logo, unique ID, and
display flags. The customer-account order object omits
`financial_entity`, `warehouse`, `origin_address`, business/operator
analytics, net revenue, platform fee, provider, CRM, affiliate, and raw
internals.

## Typed customer endpoint responses

**May 2026** · API

Authenticated customer storefront endpoints now return typed responses
instead of generic success envelopes. `GET`, `PATCH`, and `PATCH /password`
on `/customers/me/profile` return `customer`, `store`, and
`is_generated_password_reset`. Cart routes
(`GET /customers/me/cart`, item add/update/delete) return the customer cart;
cart item add now returns `201`. Order routes use the buyer-safe order
response for list and detail responses, with cursor
pagination on the list endpoint. Course routes return typed access, section,
and content responses, plus typed progress update responses.

## Storefront API checkout and payment contracts

**May 2026** · API, Docs

Storefront API now documents browser-safe guest checkout preparation for
shipping options and checkout summary. Public guest checkout can use a guest
cart token or direct variant items, returns the same shipping option fields as
the hosted storefront, and exposes summary fields as
`product_price`, `shipping_cost`, `other_income`, `other_income_name`, and
`gross_revenue`. OpenAPI now also includes named schemas for customer
checkout endpoints and remaining normal-shopping storefront routes such as
categories, variant pricing, cart merge, public order read/update, and
discount-code checks. Storefront API docs now include checkout and payment
rendering guidance based on the hosted success page behavior.

## Customer auth token responses

**May 2026** · API

Storefront customer auth endpoints now return typed JWT token responses.
`POST /public/auth/login` returns customer access and refresh tokens when
the store can complete login directly, or `{ "message": "..." }` when an OTP
has been sent and the frontend should show the OTP entry step.
`POST /public/auth/otp/verify` and `POST /public/auth/jwt/refresh` also
return `token_type`, `expires_in`, and `refresh_expires_in`. Refresh tokens
rotate on every refresh, are single-use, and revoke their token family when
an already-rotated refresh token is reused. Send the access token as
`Authorization: Bearer <token>` to `/customers/me/*` routes. Password reset
links now use `/reset-password?token=<reset-token>` on the browser `Origin`
when it matches a registered Storefront API allowed origin, and fall back to
the hosted storefront custom domain otherwise. The regular hosted member
area reset URL is unchanged.

## Storefront catalog schema fixes

**May 2026** · API

The public OpenAPI schema for the catalog count route now documents
`{ "total": number }`, and `GET /public/products/{slug}` now documents a
storefront product detail response instead of the public order schema.

## Order payment response clarifications

**May 2026** · API

Order payment responses now document `pg_payment_info` per provider type:
manual methods such as `bank_transfer` and `cod` return an empty object;
virtual account methods expose provider reference and account details;
QRIS responses expose QR data or a QR image payload; e-wallet, card, and
invoice methods may expose provider actions while the browser should use
`payment_url` for hosted redirects. Payment methods use canonical flat
values, including bank-specific virtual-account codes such as `va_bca`.

## Storefront rate limiting

**May 2026** · API

Storefront API requests using `X-Scalev-Storefront-Api-Key` or
`X-Scalev-Guest-Token` are rate-limited as direct client/browser requests.
Machine-authenticated business requests continue to be rate-limited per
API key or OAuth installation. Rate-limit metadata is returned in
`X-Ratelimit-*` headers.

## Direct Storefront API

**May 2026** · API, Dashboard, Docs

Storefront API setup is now documented as separate from hosted Storefront
configuration. Storefront frontends can use direct CORS-enabled Storefront API
calls, `X-Scalev-Guest-Token` cart identity, public
payment-method and guided location lookup endpoints, typed guest checkout,
minimized public order reads, idempotent public payment creation, and the
public store `unique_id` across setup and runtime routes. Customer login
responses now document the direct-token and OTP-challenge outcomes, password
reset links use `/reset-password?token=<reset-token>` on the validated
registered storefront origin, Storefront API
requests are documented as direct-client rate limited, and payment responses
document when to use `payment_url` versus provider-specific `pg_payment_info`.

## Order search field selection

**May 2026** · API

Order list search now accepts `search_field` so clients choose one searchable
order column per request. When omitted, `search_field` defaults to `order_id`.

## Developer documentation

**April 2026** · Docs

Published the first Scalev developer documentation pages for API authentication, OAuth authorization, webhooks, and order creation.
