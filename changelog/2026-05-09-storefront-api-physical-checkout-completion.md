---
title: Storefront API physical checkout completion
slug: storefront-api-physical-checkout-completion
type: none
created_at: 2026-05-09T18:27:11+10:00
privacy:
  view: public
---

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
