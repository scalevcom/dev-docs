---
title: Storefront API checkout and payment contracts
slug: storefront-api-checkout-and-payment-contracts
type: none
created_at: 2026-05-09T17:02:22+10:00
privacy:
  view: public
---

**API · Docs**

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
