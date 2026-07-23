---
title: Order payment response clarifications
slug: order-payment-response-clarifications
type: none
created_at: 2026-05-09T03:03:42Z
privacy:
  view: public
---

Order payment responses now document `pg_payment_info` per provider type:
manual methods such as `bank_transfer` and `cod` return an empty object;
virtual account methods expose provider reference and account details;
QRIS responses expose QR data or a QR image payload; e-wallet, card, and
invoice methods may expose provider actions while the browser should use
`payment_url` for hosted redirects. Payment methods use canonical flat
values, including bank-specific virtual-account codes such as `va_bca`.
