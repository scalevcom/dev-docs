---
title: Typed customer endpoint responses
slug: typed-customer-endpoint-responses
type: none
created_at: 2026-05-09T07:55:41Z
privacy:
  view: public
---

**API**

Authenticated customer storefront endpoints now return typed responses
instead of generic success envelopes. `GET`, `PATCH`, and `PATCH /password`
on `/customers/me/profile` return `customer`, `store`, and
`is_generated_password_reset`. Cart routes
(`GET /customers/me/cart`, item add/update/delete) return the customer cart;
cart item add now returns `201`. Order routes use the buyer-safe order
response for list and detail responses, with cursor
pagination on the list endpoint. Course routes return typed access, section,
and content responses, plus typed progress update responses.
