---
title: Direct Storefront API
slug: direct-storefront-api
type: none
created_at: 2026-05-08T20:44:48+10:00
privacy:
  view: public
---

Storefront API setup is now documented as separate from hosted Storefront
configuration. Storefront frontends can use direct CORS-enabled Storefront API
calls, `X-Scalev-Guest-Token` cart identity, public
payment-method and guided location lookup endpoints, typed guest checkout,
minimized public order reads, idempotent public payment creation, and the
public store `unique_id` across setup and runtime routes. Customer login
responses now document the direct-token and OTP-challenge outcomes, password
reset links use `/reset-password?token=<reset-token>` on the validated
registered storefront origin, Storefront API
requests are documented as direct-client rate limited, and payment responses
document when to use `payment_url` versus provider-specific `pg_payment_info`.
