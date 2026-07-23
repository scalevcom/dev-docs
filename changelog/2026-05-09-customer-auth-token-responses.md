---
title: Customer auth token responses
slug: customer-auth-token-responses
type: none
created_at: 2026-05-09T03:03:42Z
privacy:
  view: public
---

**Customer authentication now returns typed JWT responses with rotating refresh tokens.**

Storefront customer auth endpoints now return typed JWT token responses.
`POST /public/auth/login` returns customer access and refresh tokens when
the store can complete login directly, or `{ "message": "..." }` when an OTP
has been sent and the frontend should show the OTP entry step.
`POST /public/auth/otp/verify` and `POST /public/auth/jwt/refresh` also
return `token_type`, `expires_in`, and `refresh_expires_in`. Refresh tokens
rotate on every refresh, are single-use, and revoke their token family when
an already-rotated refresh token is reused. Send the access token as
`Authorization: Bearer <token>` to `/customers/me/*` routes. Password reset
links now use `/reset-password?token=<reset-token>` on the browser `Origin`
when it matches a registered Storefront API allowed origin, and fall back to
the hosted storefront custom domain otherwise. The regular hosted member
area reset URL is unchanged.
