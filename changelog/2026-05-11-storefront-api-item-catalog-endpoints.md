---
title: Storefront API item catalog endpoints
slug: storefront-api-item-catalog-endpoints
type: none
created_at: 2026-05-11T16:09:13+10:00
privacy:
  view: public
---

**API · Docs**

Storefront API v3 now uses `GET /v3/stores/{store_id}/public/items` and
`GET /v3/stores/{store_id}/public/items/count` for the public catalog feed
because the feed returns both products and bundle price options. Product detail remains
`GET /v3/stores/{store_id}/public/products/{slug}`, and bundle price option detail is
`GET /v3/stores/{store_id}/public/bundle-price-options/{slug}`. Catalog cards use
`entity_type` to distinguish `product` from `bundle_price_option`, while product
`item_type` keeps its product meaning such as `physical` or `digital`. Public cart item
and direct checkout item payloads use `{ "type": "bundle_price_option", "bundle_price_option_id": ... }`
for bundle price options.
