---
title: "HTML Mode checkout success types"
excerpt: "Choose what happens after a manual HTML Mode checkout creates an order."
deprecated: false
hidden: false
metadata:
  robots: index
---
When you build a checkout form manually in HTML Mode, `Scalev.checkout.createOrder(payload)` creates the order. The Scalev API resolves the destination and returns it as `order.redirectUrl`. Your page opens that URL after the order is created; the runtime does not navigate automatically.

There are two separate success moments in a checkout:

1. **Order created:** Your HTML Mode page receives the result from `createOrder` and opens `order.redirectUrl`. This can lead to payment instructions, PayLink, an order page, WhatsApp, another landing page, or a custom URL.
2. **Payment received:** A hosted Scalev payment, success, or order page observes the paid state and can redirect the buyer to the merchant-configured post-payment URL.

The editor uses an explicit **Redirect to a custom URL after payment** toggle and a **Post-payment redirect URL**. When the toggle is off, Scalev uses its default success flow; a saved but disabled URL has no effect. When the toggle is on, a valid URL is required.

This configuration is private editor state. It is not included in `window.Scalev` or `Scalev.data.get()`, so HTML code cannot read the page default. Scalev snapshots the resolved URL onto the new public order. Hosted Scalev pages apply that snapshot only after the order reports a `paid` or `settled` payment.

An API caller can override the private default for one order through `Scalev.checkout.createOrder(payload)`. This does not add a control to the dashboard or public form. Omit both override fields to inherit the page setting:

```js
const order = await Scalev.checkout.createOrder({
  ...payload,
  isPostPaymentRedirectEnabled: true,
  postPaymentRedirectUrl: "https://app.example.com/order-specific-success"
});
```

Send `isPostPaymentRedirectEnabled: false` to keep Scalev's hosted success flow for that order. When you send `true`, `postPaymentRedirectUrl` is required and must be an absolute HTTPS URL. The override is creation-only and cannot be changed through an order update.

Neither redirect proves payment. Provision external access from a verified `payment.received` webhook, not from browser navigation.

HTML Checkout Pages expose the selected after-checkout configuration in `Scalev.data.get().afterCheckout`. This describes the editor's configuration, not the resolved destination for a particular order. Do not use it to reconstruct a redirect. The Scalev API accounts for the payment method, PayLink, order status, assigned WhatsApp number, and supported attribution parameters when it builds `order.redirectUrl`.

## Redirect rules

- Render payment labels from `Scalev.data.get().store.paymentMethodOptions[].display` and submit the selected option `value` as `paymentMethod`.
- After `createOrder` succeeds, open the returned `order.redirectUrl` unchanged. Do not infer a URL from the selected payment method, append query parameters, or build a WhatsApp URL from the template yourself.
- A missing or empty `redirectUrl` means no destination was resolved. Keep the buyer on the page and show an order-created confirmation. You can offer the returned `order.publicOrderUrl` as an order-details link. Do not resubmit the order to obtain a redirect.
- If your page is embedded in an iframe, send the returned URL to the embedding parent's navigation handler instead of navigating only the iframe.

`createOrder` returns the order object directly. Runtime response keys use camelCase; the API's `redirect_url` becomes `redirectUrl`:

```json
{
  "secretSlug": "orderSecret",
  "redirectUrl": "https://example.com/o/orderSecret/success",
  "publicOrderUrl": "https://example.com/o/orderSecret",
  "paymentUrl": "https://example.com/o/orderSecret/success",
  "handlerPhone": "6281200000000",
  "chatMessage": "..."
}
```

`paymentUrl` describes the payment step only. It is not a substitute for the resolved After Checkout destination when `redirectUrl` is present.

## Reference implementation

Use this helper after `createOrder` succeeds. It returns `false` if no destination is available, so your page can display a confirmation instead. When you control the embedding page, use its exact origin as `parentOrigin` and validate messages in its handler. The default retains the existing embedding convention.

```js
function redirectAfterOrder(order, parentOrigin = "*") {
  const url = typeof order.redirectUrl === "string"
    ? order.redirectUrl.trim()
    : "";

  if (!url) return false;

  if (window.self !== window.top) {
    window.parent.postMessage(url, parentOrigin);
  } else {
    window.location.assign(url);
  }

  return true;
}
```

Example usage:

```js
const data = Scalev.data.get();
const store = data.store;
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
const shipping = shippingOptions[0];

const payload = {
  customer: {
    name: form.customerName.value,
    phone: form.customerPhone.value
  },
  destination,
  items,
  paymentMethod: selectedPaymentOption.value,
  shipping
};

const order = await Scalev.checkout.createOrder(payload);

if (!redirectAfterOrder(order)) {
  // Implement this in your page: confirm the order was created and optionally
  // offer order.publicOrderUrl as a link. Do not ask the buyer to submit again.
  showOrderCreated(order);
}
```

If the checkout includes Other Charges or a customer-facing Service Fee, Scalev calculates both from the store's saved settings in `estimateSummary` and recalculates them during `createOrder`. The Service Fee base includes Other Charges. The page never sends a fee policy, a fee amount, or a fee quote. Use `Scalev.checkout.estimateSummary()` only when the page needs to show an estimated fee and total before submit; pass the payload you will send to `createOrder`. The redirect logic after order creation does not change.

## The six types

Choose these destinations in the editor. Your HTML code uses the same `order.redirectUrl` field for every type; the Scalev API resolves any payment-method override or PayLink destination before returning it.

| Editor label | Value | Configured destination |
| --- | --- | --- |
| Halaman Instruksi Pembayaran | `success_page` | The hosted payment instruction page. Draft orders use the order page because payment instructions are not available yet. |
| Langsung ke WhatsApp | `direct_to_whatsapp` | WhatsApp for the sales person assigned to the order, with the rendered visitor-to-store message. |
| Langsung ke Nomor WhatsApp Tertentu | `direct_to_custom_whatsapp` | WhatsApp for the configured fixed number, with the rendered visitor-to-store message. |
| Landing Page Lainnya | `other_page` | The selected landing page on the checkout host, with supported attribution parameters. |
| Self Hosted Orderan / Invoice | `order_page` | The public order or invoice page. |
| Custom URL | `custom_url` | The configured URL. Scalev includes supported attribution parameters only for eligible destinations. |

If a required destination is missing, such as an unselected landing page or an unavailable WhatsApp number, `redirectUrl` can be empty. Use the confirmation behavior above instead of reconstructing the destination from editor state.

## Notes for analytics and attribution

Scalev includes supported attribution in the resolved URL where allowed. Open `order.redirectUrl` unchanged; do not copy the browser's raw query string onto it or encode its WhatsApp message again.

After `Scalev.checkout.createOrder(payload)` succeeds, HTML Checkout Pages automatically fire the configured form-submit analytics events for analytics pixels configured on the page. Keep navigation after `createOrder` resolves and add custom analytics only for intentionally separate events.

Order creation and browser navigation do not prove payment. Use a verified `payment.received` webhook to provision external access.
