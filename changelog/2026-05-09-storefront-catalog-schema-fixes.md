---
title: Storefront catalog schema fixes
slug: storefront-catalog-schema-fixes
type: none
created_at: 2026-05-09T15:13:00+10:00
privacy:
  view: public
---

**API**

The public OpenAPI schema for the catalog count route now documents
`{ "total": number }`, and `GET /public/products/{slug}` now documents a
storefront product detail response instead of the public order schema.
