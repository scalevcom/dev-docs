---
title: Canonical payment methods and E-Payment Link
slug: canonical-payment-methods-and-e-payment-link
type: none
created_at: 2026-07-21T20:55:48+10:00
privacy:
  view: public
---

**API · Docs**

Order and Storefront APIs now use one canonical `payment_method`. Virtual
accounts use flat values such as `va_bca`; there is no secondary payment
method field in the documented request or response contract. Stores can
offer `payment_link`, and strict two-step checkout can omit
`payment_method` so Scalev routes the buyer to the E-Payment Link selector.
Public order responses expose customer-paid E-Payment Link surcharge income
as `payment_link_income`. Order webhooks expose `payment_link_id` and
`is_from_payment_link` so the origin remains available after a paid order's
`payment_method` changes to the concrete method used.
