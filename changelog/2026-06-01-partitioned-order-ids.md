---
title: Partitioned order IDs
slug: partitioned-order-ids
type: none
created_at: 2026-06-01T10:01:16+10:00
privacy:
  view: public
---

Business order responses now return the canonical order primary key as a
UUIDv7 string after the partitioned orders-table migration. Use the response
`id` for follow-up business API calls such as `GET /v3/orders/{id}` and
`PATCH /v3/orders/{id}`. Legacy numeric order IDs for migrated orders remain
accepted on ID routes and bulk `ids` payloads for compatibility.
