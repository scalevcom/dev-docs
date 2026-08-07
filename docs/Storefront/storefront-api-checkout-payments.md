---
title: "Checkout and Payments"
excerpt: "Prepare shipping, compute totals, create guest orders, and render payment instructions."
deprecated: false
hidden: false
metadata:
  robots: index
---
Storefront API checkout uses the same buyer-facing checkout concepts as the Scalev-hosted storefront. A browser storefront can prepare delivery options, compute the checkout summary, create a guest order, read the public order, and create or reuse payment instructions without a merchant backend.

The Storefront API is designed so your storefront can render its own payment page. Use the public order and payment responses to show buyer-facing instructions directly in your UI. `payment_url` is still returned as a hosted fallback for storefronts that have not implemented a method-specific renderer or for provider flows that must open a hosted payment page.

Use only payment methods returned by `GET /v3/stores/{store_id}/public/payment-methods`. Storefront checkout does not return `no_payment`, and checkout endpoints reject it if submitted directly. When a store passes provider transaction fees to the customer, Scalev also omits configured e-payment methods that do not have an executable provider and verified fee schedule. This filtering does not disable or delete the store's saved method configuration.

## Guest checkout flow

1. Read or create the guest cart and store `X-Scalev-Guest-Token`.
2. Ask the buyer for delivery location and postal code when the cart contains physical items.
3. Call `POST /public/checkout/shipping-options`.
4. Let the buyer select a shipping option.
5. Call `POST /public/checkout/summary`.
6. Call `POST /public/checkout` with buyer details and the selected checkout fields.
7. Read the order with `GET /public/orders/{secret_slug}`.
8. For manual `bank_transfer`, request a transfer-proof upload URL, upload the image, and patch the order with the returned file URL.
9. Call `POST /public/orders/{secret_slug}/payment` and render the returned payment data on your own payment page.

## Shipping options

```http
POST /v3/stores/{store_id}/public/checkout/shipping-options
```

Headers:

```text
X-Scalev-Storefront-Api-Key: sfpk_...
X-Scalev-Guest-Token: <guest-token>
```

Send direct typed items, or omit `items` and let `X-Scalev-Guest-Token` select the guest cart:

```json
{
  "items": [
    {
      "type": "variant",
      "variant_id": 494535,
      "quantity": 1
    }
  ],
  "destination": {
    "location_id": 9089,
    "postal_code": "10510"
  },
  "payment_method": "bank_transfer"
}
```

Direct `items[]` supports variants and bundle price options. Bundle price option items use `{ "type": "bundle_price_option", "bundle_price_option_id": 123, "quantity": 1 }`.

Response:

```json
{
  "data": [
    {
      "courier_service_id": 123,
      "courier_code": "jne",
      "service_code": "REG",
      "name": "Regular",
      "cost": 12000,
      "etd": "2-3",
      "is_cod": false,
      "warehouse_unique_id": "warehouse_...",
      "courier_aggregator_code": null
    }
  ],
  "is_paginated": false
}
```

Digital-only carts return:

```json
{
  "data": [],
  "is_paginated": false
}
```

## Checkout summary

```http
POST /v3/stores/{store_id}/public/checkout/summary
```

Send the selected shipping option. Scalev recomputes the shipping cost server-side and ignores any client-supplied `shipping_cost`.

```json
{
  "destination": {
    "location_id": 9089,
    "postal_code": "10510"
  },
  "courier_service_id": 123,
  "warehouse_unique_id": "warehouse_...",
  "courier_aggregator_code": null,
  "payment_method": "bank_transfer"
}
```

Response fields match the existing checkout summary:

```json
{
  "product_price": "125000.00",
  "shipping_cost": "12000",
  "other_income": "6500",
  "other_income_name": "Biaya Penanganan",
  "service_fee": "3500",
  "gross_revenue": "147000.00"
}
```

`other_income` remains the store's existing Other Charges amount and uses `other_income_name` as its buyer-facing label. `service_fee` is the single combined customer-facing fee for direct e-payment. The two charges are independent and can both be non-zero. Scalev calculates Other Charges first, then uses the canonical checkout amount plus `other_income` as the Service Fee base. `gross_revenue` is the displayed and charged total. Do not derive or submit separate provider or Scalev fee components.

Scalev calculates both charges from the store's saved Service Fee and Other Charges settings. Your storefront does not send a fee policy, a fee amount, or a fee quote in either request, and there is no fee field to carry from the summary into checkout. Checkout recalculates both from the same settings, so treat summary values as a buyer-facing preview.

Dynamic E-Payment Other Charges and per-payment-method overrides remain active for direct checkout and can coexist with Service Fee. `service_fee` is zero when the store charges no customer fee for the selected method, while the saved Other Charges rules still apply. COD and other non-e-payment methods continue using Other Charges and return no service fee. Digital-only carts return `shipping_cost: "0"`.

A `payment_link` order is always created with `other_income` of zero, whatever the request contains. The Payment Link snapshots the store's Other Charges configuration and quotes both charges on the Scalev-hosted payment page after the buyer picks a concrete method.

Refresh the summary whenever the cart items, destination, shipping selection, discount, or payment method changes.

## Discount code check

```http
POST /v3/stores/{store_id}/public/discount-codes/check
```

Use a JSON body to validate a discount code before checkout:

```json
{
  "code": "SAVE10",
  "items": [
    {
      "type": "variant",
      "variant_id": 494535,
      "quantity": 1
    }
  ],
  "destination": {
    "location_id": 9089,
    "postal_code": "10510"
  },
  "courier_service_id": 123,
  "warehouse_unique_id": "warehouse_abc",
  "courier_aggregator_code": null,
  "payment_method": "bank_transfer"
}
```

If direct `items` are supplied, the API uses them as the item source. Otherwise, provide `X-Scalev-Guest-Token` for the guest cart. Unknown or ineligible codes return a normal validation response with `is_eligible: false` and `discount_code: null`.

## Public checkout

Create the order with:

```http
POST /v3/stores/{store_id}/public/checkout
```

The endpoint accepts direct typed `items`, the guest cart referenced by `X-Scalev-Guest-Token`, or both. If both are supplied, direct `items` create the order and the referenced guest cart is cleared after success.

Use the same selected checkout fields:

```json
{
  "items": [
    {
      "type": "variant",
      "variant_id": 494535,
      "quantity": 1
    }
  ],
  "customer_name": "Customer Name",
  "customer_email": "customer@example.com",
  "customer_phone": "08123456789",
  "shipping_address": "Jl. Example 1",
  "shipping_location_id": 9089,
  "shipping_subdistrict": "Cempaka Putih",
  "shipping_postal_code": "10510",
  "courier_service_id": 123,
  "warehouse_unique_id": "warehouse_...",
  "courier_aggregator_code": null,
  "payment_method": "va_bca"
}
```

The checkout endpoint uses the selected courier service, warehouse, destination, payment method, and checkout items to recompute shipping, Other Charges, and the service fee internally. Do not submit a fee policy or a fee amount, and do not treat a client-supplied `shipping_cost` as the source of truth.

The created order carries the fees Scalev calculated at checkout time, which can differ from an older summary if the store settings or checkout inputs changed in between. Read the totals from the checkout response before showing the buyer a confirmation.

On success, the response includes the created slim public order data, including `secret_slug`, `public_order_url`, `payment_url`, status, totals, the existing `variants` and `bundle_price_options` object maps, line items, shipping details, and payment fields. Internal order IDs, dashboard-only revenue fields, platform fees, payment-status history, and affiliate attribution are not returned. Use `secret_slug` to read or update the order. Use `payment_url` only as a hosted fallback if your storefront does not render the payment instructions itself.

New orders expose one unified customer-facing `service_fee`, including orders
created through E-Payment Link. `other_income` remains independent. Legacy
orders can still expose historical compatibility fee fields, including
`payment_link_income`; do not combine those fields again for new orders.

`payment_method` normally uses one canonical method returned by the store's
payment-method endpoint. Virtual accounts use flat values such as `va_bca` and
`va_bri`.

### Strict two-step E-Payment Link checkout

When the store enables strict two-step checkout and offers `payment_link`, you
may omit `payment_method`. Scalev resolves the order to `payment_link` and
returns a `payment_url` for the Scalev E-Payment Link page, where the buyer
selects the concrete method.

Do not render `payment_link` as a virtual account or wallet. Redirect the buyer
to `payment_url`. After payment, the order's `payment_method` becomes the
canonical method actually used, while Scalev keeps the E-Payment Link origin
separately.

## Payment instructions

After checkout, call:

```http
POST /v3/stores/{store_id}/public/orders/{secret_slug}/payment
```

The endpoint is idempotent. If payment instructions already exist, the response returns the order again with the existing buyer-facing payment data and URLs.

Use this order of preference in a browser storefront:

1. Render the order's method-specific instructions from the canonical `payment_method`, `epayment_provider`, and `pg_payment_info`.
2. For provider-hosted methods, open the provider URL from `pg_payment_info` when the provider requires a redirect.
3. Use `payment_url` only as a fallback to the Scalev-hosted payment page when your storefront does not yet support that method or provider response.
4. Poll the public order when the method needs gateway data that may not exist immediately.

## Method rendering

The Scalev-hosted success page is the reference implementation for method-specific rendering. A Storefront API storefront can replace that page by applying the same `pg_payment_info` mappings in its own UI.

The hosted success page first derives a small set of display fields from the current Xendit/default `pg_payment_info`. This is not a separate API response. It is a useful reference if your storefront wants one payment renderer instead of branching directly on raw provider payload fields:

```json
{
  "qrString": "000201010212...",
  "qrImageUrl": "https://api.qrserver.com/v1/create-qr-code/?...",
  "vaNumber": "88081234567890",
  "vaAccountHolder": "Customer Name",
  "invoiceUrl": "https://provider.example/pay/...",
  "renderUrlAs": "button"
}
```

The actual source fields come from the order and payment response. For the current Xendit/default payload, map them this way:

| Display value     | Source field                                                                                                                                                                    |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `qrString`        | `pg_payment_info.qr_string` or `pg_payment_info.payment_method.qr_code.channel_properties.qr_string`                                                                            |
| `vaNumber`        | `pg_payment_info.payment_method.virtual_account.channel_properties.virtual_account_number` or `pg_payment_info.payment_method.over_the_counter.channel_properties.payment_code` |
| `vaAccountHolder` | `pg_payment_info.payment_method.virtual_account.channel_properties.customer_name` or `pg_payment_info.payment_method.over_the_counter.channel_properties.customer_name`         |
| `invoiceUrl`      | `pg_payment_info.invoice_url` or `pg_payment_info.redirect_url`                                                                                                                 |
| `qrImageUrl`      | Generate a QR image from `qrString` in your frontend when you need a downloadable QR image.                                                                                     |

For `gopay`, `dana`, `linkaja`, `shopeepay`, and `ovo`, choose an action URL from `pg_payment_info.actions`: mobile prefers `url_type` `WEB` or `DEEPLINK`; desktop prefers `MOBILE` or `DEEPLINK`.

Set `renderUrlAs` to `button` for `invoice`, `card`, and all mobile views. For other desktop views, render the URL as a QR code.

`bank_transfer`:

Display the order total, manual bank transfer accounts, expiry countdown when enabled, and a payment-confirmation link to `/o/{secret_slug}?showPaymentConfirmation=true`. The hosted page gets bank accounts from the store `payment_accounts` where `method` is `bank_transfer` and the method is still active. `pg_payment_info` can be `{}`.

For manual transfer proof, follow the same flow as the Scalev-hosted public order page:

1. Let the buyer choose a bank account from `store.payment_accounts` where `method` is `bank_transfer`.
2. Let the buyer upload a `jpg`, `png`, or `webp` proof image.
3. Request upload metadata:

```http
POST /v3/stores/{store_id}/public/orders/{secret_slug}/transfer-proof-upload
```

```json
{
  "filename": "transfer-proof.png",
  "content_type": "image/png",
  "content_length": 12345
}
```

4. Upload the file bytes directly to the returned `upload_url` with `PUT` and the same `Content-Type`.
5. Patch the public order with the returned `file_url`:

```http
PATCH /v3/stores/{store_id}/public/orders/{secret_slug}
```

```json
{
  "transferproof_url": "https://files.scalev.com/uploads/.../transfer-proof.png",
  "transfer_time": "2026-05-15T04:00:00Z",
  "financial_entity_id": 12,
  "payment_account_holder": "PT Example",
  "payment_account_number": "1234567890"
}
```

6. Refetch the order and show the submitted proof from `transferproof_url`.

`cod`:

Display the COD success body and do not show a payment countdown. Payment creation may return an empty `pg_payment_info`.

Virtual accounts (`va_*`):

Derive the bank from the canonical method and render `vaNumber` plus the optional `vaAccountHolder`. Show a copy button and a payment tutorial link. Supported canonical values are `va_bca`, `va_bni`, `va_bri`, `va_mandiri`, `va_permata`, `va_cimb`, `va_bsi`, `va_maybank`, `va_bnc`, `va_danamon`, `va_artha_graha`, `va_muamalat`, `va_btn`, `va_ocbc`, `va_bjb`, `va_sahabat_sampoerna`, and `va_artajasa`.

QRIS (`qris`):

Render a QR code from `qrString`. Also offer a QR download action from `qrImageUrl` and show mobile instructions for saving or screenshotting the QR image before paying in a QRIS app. If QR generation fails or `qrString` is missing, show a retry action that calls the public payment endpoint again.

E-wallets except OVO (`gopay`, `dana`, `linkaja`, `shopeepay`):

Use `invoiceUrl` from provider actions. On mobile, open it as a button/deep link. On desktop, render the `invoiceUrl` as a QR code when `renderUrlAs` is `qr_code`; otherwise open it as a button. If no URL can be mapped, send the buyer back to the public order page.

OVO (`ovo`):

Show an instruction to check the OVO app tied to the buyer phone number. The hosted success component does not render OVO through the same e-wallet QR component.

Card (`card`) and invoice/hosted payment (`invoice`):

Open the mapped `invoiceUrl` as a button/redirect. The hosted success page redirects automatically when `invoiceUrl` exists and `renderUrlAs` is `button`.

Alfamart:

Render `vaNumber` as `No Pembayaran`, show `vaAccountHolder` when present, and provide a copy action.

## Polling and status checks

For e-payment methods (`gopay`, `card`, `invoice`, any canonical `va_*` method, `qris`, `ovo`, `dana`, `shopeepay`, `linkaja`, and `alfamart`), the hosted success page waits for `pg_payment_info` to appear by refetching the public order up to 15 times with a 1.5 second delay.

For pending unpaid orders with `card`, `invoice`, `shopeepay`, `dana`, `qris`, `linkaja`, `gopay`, `bank_transfer`, and `alfamart`, the hosted success page then refreshes the public order every 5 seconds while waiting for payment confirmation.

For canonical `va_*` methods, `bank_transfer`, `qris`, and `alfamart`, it also shows a manual "check payment status" action.

## Authenticated customer checkout

Customer checkout endpoints stay under:

```text
/v3/stores/{store_id}/customers/me/checkout/*
```

They use `Authorization: Bearer <customer_access_token>`, not the Storefront API key. Addresses, payment methods, shipping options, and summary use the same checkout preparation fields as public checkout. Create the order with `POST /v3/stores/{store_id}/customers/me/checkout`; the request accepts direct typed `items`, `cart_id`, or both. The response uses the same public order shape returned by public checkout and public order reads, so every checkout completion response has the same order fields.

Customer checkout summary uses the selected courier service, warehouse, destination, payment method, and either direct `items` or the referenced customer cart to recompute shipping cost server-side. A client-supplied `shipping_cost` is only a compatibility value and is not the authoritative amount.

Authenticated customer checkout handles fees the same way as guest checkout: Scalev calculates Other Charges and Service Fee from the store's settings, the request carries no fee fields, and the storefront refreshes the summary when checkout inputs change and renders `other_income` and `service_fee` as separate rows.
