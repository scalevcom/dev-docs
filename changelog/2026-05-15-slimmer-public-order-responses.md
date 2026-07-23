---
title: Slimmer public order responses
slug: slimmer-public-order-responses
type: none
created_at: 2026-05-15T10:49:42+10:00
privacy:
  view: public
---

**Public order responses now focus on buyer-facing fields and omit internal operational data.**

Storefront API and HTML Mode public order responses now return a smaller
buyer-facing shape. The response still includes `secret_slug`,
`public_order_url`, `payment_url`, status, totals, line items, shipping
display data, payment instructions such as `pg_payment_info`, and the existing
`variants` and `bundle_price_options` object maps, but it no
longer exposes internal order IDs, dashboard revenue fields, platform fees,
payment-status history, or affiliate attribution.
