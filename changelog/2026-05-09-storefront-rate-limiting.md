---
title: Storefront rate limiting
slug: storefront-rate-limiting
type: none
created_at: 2026-05-09T03:03:42Z
privacy:
  view: public
---

Storefront API requests using `X-Scalev-Storefront-Api-Key` or
`X-Scalev-Guest-Token` are rate-limited as direct client/browser requests.
Machine-authenticated business requests continue to be rate-limited per
API key or OAuth installation. Rate-limit metadata is returned in
`X-Ratelimit-*` headers.
