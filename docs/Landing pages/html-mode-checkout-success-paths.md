---
title: "HTML Mode checkout success types"
excerpt: "Where a buyer goes after a manual HTML Mode checkout creates an order."
deprecated: false
hidden: false
metadata:
  robots: index
---
When you build a checkout form manually in HTML Mode, `Scalev.checkout.createOrder(payload)` creates the order and resolves where the buyer goes next. Your page performs the navigation; it does not decide the destination.

There are two separate success moments in a checkout:

1. **Order created:** `createOrder` returns `order.redirectUrl`. Send the buyer there.
2. **Payment received:** a hosted Scalev payment, success, or order page observes the paid state and can redirect the buyer to the merchant-configured post-payment URL.

## Redirect after the order is created

```js
const order = await Scalev.checkout.createOrder(payload);

if (order.redirectUrl) {
  if (window.self !== window.top) {
    window.parent.postMessage(order.redirectUrl, "*");
  } else {
    window.location.assign(order.redirectUrl);
  }
}
```

That is the whole redirect. `order.redirectUrl` already accounts for:

- **The payment-method override.** An electronic method — `va`, `qris`, `card`, `invoice`, `payment_link`, `alfamart`, `indomaret`, `ovo`, `dana`, `shopeepay`, `linkaja`, `gopay` — goes to its payment page regardless of the configured after-checkout type. PayLink resolves to the Scalev-hosted PayLink page.
- **Per-bank virtual account values.** A flattened value such as `va_bca` follows the configured after-checkout type rather than the payment page, matching how Scalev's own Builder checkout behaves.
- **Draft orders.** A draft has no payment instructions yet, so it resolves to its own order page instead of the instruction page.
- **Every configured destination:** the payment instruction page, the order/invoice page, both WhatsApp destinations, another landing page, and a custom URL.
- **The host.** Scalev-hosted destinations are built on the host the order was created on, falling back to the business's `*.myscalev.com` domain.
- **Attribution.** Retained UTM, click-ID, and affiliate parameters are forwarded onto another landing page or a custom URL, but only while the destination stays on the buyer's own host or a Scalev-owned one. An external host never receives them.

`order.redirectUrl` is `null` only when the merchant's configured destination is incomplete — for example a custom URL that was never filled in. Treat that as "stay on this page" and show your own confirmation; do not guess a destination.

`order.paymentUrl` still exists and still points at the payment step only. Use `redirectUrl` for navigation after checkout.

Both fields are also available in snake_case (`order.redirect_url`, `order.payment_url`) if you prefer that shape.

### Do not rebuild the routing

Earlier versions of this page documented a client-side helper that inspected the payment method, the order status and `Scalev.data.get().afterCheckout` to pick a destination. That logic now lives in Scalev and is shared with the Builder checkout, so the two can no longer disagree. Delete any copy of it from your page and read `order.redirectUrl`.

`Scalev.data.get().afterCheckout` remains available, and it is still the right source if you want to *show* the buyer what happens next before they submit. It is no longer needed to route them.

## Redirect after payment is received

The editor has a **Redirect to a custom URL after payment** toggle and a **Post-payment redirect URL**. When the toggle is off, Scalev uses its default success flow; a saved but disabled URL has no effect. When the toggle is on, a valid URL is required.

This configuration is private editor state. It is not included in `window.Scalev` or `Scalev.data.get()`, so HTML code cannot read the page default. Scalev snapshots the resolved URL onto the new public order, and hosted Scalev pages apply that snapshot only after the order reports a `paid` or `settled` payment.

An API caller can override the private default for one order:

```js
const order = await Scalev.checkout.createOrder({
  ...payload,
  isPostPaymentRedirectEnabled: true,
  postPaymentRedirectUrl: "https://app.example.com/order-specific-success"
});
```

Send `isPostPaymentRedirectEnabled: false` to keep Scalev's hosted success flow for that order. When you send `true`, `postPaymentRedirectUrl` is required and must be an absolute HTTPS URL. The override is creation-only and cannot be changed through an order update.

Neither redirect proves payment. Provision external access from a verified `payment.received` webhook, not from browser navigation.

## What each configured type means

The merchant picks one of these in the editor. You do not implement them; this table explains what the buyer will experience.

| Editor label                        | Value                       | Where the buyer lands                                                                                      |
| ----------------------------------- | --------------------------- | ---------------------------------------------------------------------------------------------------------- |
| Halaman Instruksi Pembayaran        | `success_page`              | The Scalev payment instruction page for the order.                                                          |
| Langsung ke WhatsApp                | `direct_to_whatsapp`        | WhatsApp, using the handler Scalev assigns from the store or page assignment, with the order's chat message. |
| Langsung ke Nomor WhatsApp tertentu | `direct_to_custom_whatsapp` | WhatsApp, using the fixed number configured on the page.                                                    |
| Landing Page Lainnya                | `other_page`                | Another Scalev landing page, with retained attribution parameters forwarded.                                |
| Self Hosted Orderan / Invoice       | `order_page`                | The public order/invoice page.                                                                              |
| Custom URL                          | `custom_url`                | The configured URL. Attribution is forwarded only when it stays on the buyer's host or a Scalev host.        |

An electronic payment method overrides whichever of these is configured, except for per-bank virtual account values as described above.

## Example

```js
const store = Scalev.data.get().store;
const selectedPaymentOption = store.paymentMethodOptions[0];
const selectedVariant = store.products[0].variants[0];
const destination = {
  address: form.address.value,
  subdistrictId: Number(form.subdistrictId.value),
  postalCode: form.postalCode.value
};
const items = [
  { type: "product", variantUniqueId: selectedVariant.uniqueId, quantity: 1 }
];
const shippingOptions = await Scalev.checkout.shippingOptions({
  items,
  destination,
  paymentMethod: selectedPaymentOption.value
});

const order = await Scalev.checkout.createOrder({
  customer: {
    name: form.customerName.value,
    phone: form.customerPhone.value
  },
  destination,
  items,
  paymentMethod: selectedPaymentOption.value,
  shipping: shippingOptions[0]
});

if (order.redirectUrl) window.location.assign(order.redirectUrl);
```

If the checkout includes Other Charges or a customer-facing Service Fee, Scalev calculates both from the store's saved settings in `estimateSummary` and recalculates them during `createOrder`. The Service Fee base includes Other Charges. The page never sends a fee policy, a fee amount, or a fee quote. Use `Scalev.checkout.estimateSummary()` only when the page needs to show an estimated fee and total before submit; pass the payload you will send to `createOrder`.

## Notes for analytics and attribution

After `Scalev.checkout.createOrder(payload)` succeeds, HTML Checkout Pages automatically fire the configured form-submit analytics events for the pixels configured on the page. Keep the redirect after `createOrder` resolves, and add custom analytics only for intentionally separate events.

Scalev forwards retained attribution parameters onto the destinations described above. For your page's own buttons and links, preserve the query parameters that matter for analytics — UTM, click, and affiliate parameters — yourself.
