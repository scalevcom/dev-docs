---
title: Storefront API v3 checkout endpoint cleanup
slug: storefront-api-v3-checkout-endpoint-cleanup
type: none
created_at: 2026-05-10T20:17:43+10:00
privacy:
  view: public
---

Storefront API v3 checkout order creation now uses one endpoint per
auth mode: `POST /v3/stores/{store_id}/public/checkout` for public checkout
and `POST /v3/stores/{store_id}/customers/me/checkout` for authenticated
customers. The deprecated v3 compatibility checkout paths were removed from
the contract. Direct checkout items now use an explicit typed union for
variants and bundle price options, and the same item source model is used by
shipping options, checkout summary, and final order creation.
