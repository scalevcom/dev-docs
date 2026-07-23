---
title: "HTML Mode checkout success types"
excerpt: "Choose what happens after a manual HTML Mode checkout creates an order."
deprecated: false
hidden: false
metadata:
  robots: index
---
When you build a checkout form manually in HTML Mode, `Scalev.checkout.createOrder(payload)` creates the order. Your page handles the redirect after the order is created.

HTML Checkout Pages expose the selected after-checkout configuration in `Scalev.data.get().afterCheckout`. Use that config to choose one of these six types after `createOrder` returns successfully.

```js
const afterCheckout = Scalev.data.get().afterCheckout || {
  type: "success_page"
};
```

`afterCheckout` is editor config state from the Scalev editor.

## Redirect rules

Use these rules when deciding where to send the buyer after `createOrder` succeeds:

- For new HTML Mode checkout pages, render payment labels from `Scalev.data.get().store.paymentMethodOptions[].display` and submit the selected option `value` as `paymentMethod`.
- E-payment methods always go to the payment instruction page. This includes `va`, flattened VA values such as `va:BRI`, `qris`, `card`, `invoice`, `alfamart`, `ovo`, `dana`, `shopeepay`, `linkaja`, and `gopay`.
- Manual bank-transfer values such as `bt:BCA:paymentAccountUid` are treated as `bank_transfer`.
- If the order status is `draft`, the payment instruction path falls back to **Self Hosted Orderan / Invoice** (`order_page`).
- If the page is rendered inside an iframe, post the target URL to the parent window instead of navigating the iframe directly.

Use the order data returned by `createOrder` and the public URLs in that response.

`createOrder` returns the order object directly:

```json
{
  "secretSlug": "orderSecret",
  "publicOrderUrl": "https://example.com/o/orderSecret",
  "paymentUrl": "https://example.com/o/orderSecret/success",
  "handlerPhone": "6281200000000",
  "chatMessage": "..."
}
```

```js
const order = await Scalev.checkout.createOrder(payload);
```

## Reference implementation

Use this helper after `createOrder` succeeds.

```js
const PAYMENT_INSTRUCTION_METHODS = new Set([
  "va",
  "qris",
  "card",
  "invoice",
  "alfamart",
  "ovo",
  "dana",
  "shopeepay",
  "linkaja",
  "gopay"
]);

const SCALEV_QUERY_FORWARD_HOSTS = new Set([
  "scalev.com",
  "scalev.id",
  "app.scalev.id",
  "app.scalev.com"
]);

function paymentMethodForRedirect(paymentMethod) {
  if (typeof paymentMethod !== "string") return paymentMethod;

  if (paymentMethod.toLowerCase().startsWith("va:")) return "va";
  if (paymentMethod.toLowerCase().startsWith("bt:")) return "bank_transfer";

  return paymentMethod;
}

function publicOrderUrl(order) {
  if (order.publicOrderUrl) return order.publicOrderUrl;
  return new URL(`/o/${order.secretSlug}`, window.location.origin).toString();
}

function paymentInstructionUrl(order) {
  if (order.status === "draft") return publicOrderUrl(order);
  if (order.paymentUrl) return order.paymentUrl;

  const url = new URL(publicOrderUrl(order));
  url.pathname = `${url.pathname.replace(/\/$/, "")}/success`;
  return url.toString();
}

function whatsappUrl(phone, order, fallbackMessage = "") {
  const cleanPhone = String(phone || "").replace(/[^\d]/g, "");
  const message = order.chatMessage || encodeURIComponent(fallbackMessage);
  return `https://api.whatsapp.com/send/?phone=${cleanPhone}&text=${message}`;
}

function withCurrentQuery(url) {
  const nextUrl = new URL(url, window.location.href);
  const currentParams = new URLSearchParams(window.location.search);

  currentParams.forEach((value, key) => {
    nextUrl.searchParams.set(key, value);
  });

  return nextUrl.toString();
}

function maybeForwardCurrentQuery(url) {
  const nextUrl = new URL(url, window.location.href);
  const shouldForward =
    nextUrl.host === window.location.host ||
    SCALEV_QUERY_FORWARD_HOSTS.has(nextUrl.host);

  return shouldForward
    ? withCurrentQuery(nextUrl.toString())
    : nextUrl.toString();
}

function navigateAfterOrder(url) {
  if (window.self !== window.top) {
    window.parent.postMessage(url, "*");
    return;
  }

  window.location.assign(url);
}

function redirectAfterOrder({
  type,
  order,
  paymentMethod,
  customWhatsappPhone,
  otherPagePath,
  customUrl
}) {
  const redirectPaymentMethod = paymentMethodForRedirect(
    paymentMethod || order.paymentMethod
  );
  const finalType = PAYMENT_INSTRUCTION_METHODS.has(redirectPaymentMethod)
    ? "success_page"
    : type;

  if (finalType === "success_page") {
    return navigateAfterOrder(paymentInstructionUrl(order));
  }

  if (finalType === "direct_to_whatsapp") {
    const phone = order.handlerPhone;
    return navigateAfterOrder(
      phone ? whatsappUrl(phone, order) : publicOrderUrl(order)
    );
  }

  if (finalType === "direct_to_custom_whatsapp") {
    return navigateAfterOrder(whatsappUrl(customWhatsappPhone, order));
  }

  if (finalType === "other_page") {
    return navigateAfterOrder(withCurrentQuery(otherPagePath));
  }

  if (finalType === "order_page") {
    return navigateAfterOrder(publicOrderUrl(order));
  }

  if (finalType === "custom_url") {
    return navigateAfterOrder(maybeForwardCurrentQuery(customUrl));
  }

  return navigateAfterOrder(paymentInstructionUrl(order));
}
```

Example usage:

```js
const data = Scalev.data.get();
const store = data.store;
const afterCheckout = data.afterCheckout || { type: "success_page" };
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

redirectAfterOrder({
  type: afterCheckout.type,
  order,
  paymentMethod: payload.paymentMethod,
  customWhatsappPhone: afterCheckout.customWhatsappPhone,
  otherPagePath: afterCheckout.otherPagePath,
  customUrl: afterCheckout.customUrl
});
```

If the checkout includes store-configured extra fees, Scalev calculates them in `estimateSummary` and applies and validates them again during `createOrder`. Use `Scalev.checkout.estimateSummary()` only when the page needs to show an estimated fee and total before submit; pass the payload you will send to `createOrder`. The redirect logic after order creation does not change.

## The six types

| Editor label                        | Value                       | HTML Mode behavior                                                                                                                                                                                                 |
| ----------------------------------- | --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Halaman Instruksi Pembayaran        | `success_page`              | Redirect to the Scalev payment instruction page. Prefer `order.paymentUrl`; otherwise use `/o/{secretSlug}/success`. If `order.status` is `draft`, use **Self Hosted Orderan / Invoice** (`order_page`) instead. |
| Langsung ke WhatsApp                | `direct_to_whatsapp`        | Open WhatsApp using `order.handlerPhone` and `order.chatMessage`. Scalev chooses the handler from the store or page assignment. If `handlerPhone` is missing, fall back to **Self Hosted Orderan / Invoice** (`order_page`). |
| Langsung ke Nomor WhatsApp tertentu | `direct_to_custom_whatsapp` | Open WhatsApp using your own configured phone number and `order.chatMessage`. Use this when every order should go to a fixed sales or admin number.                                                               |
| Landing Page Lainnya                | `other_page`                | Redirect to another landing page path on the current host and preserve the current query string. Use `afterCheckout.otherPagePath` from the runtime config when a page is selected.                              |
| Self Hosted Orderan / Invoice       | `order_page`                | Redirect to the public order or invoice page. Prefer `order.publicOrderUrl`; otherwise use `/o/{secretSlug}` on the current origin.                                                                               |
| Custom URL                          | `custom_url`                | Redirect to a URL you provide. For the current host or known Scalev app hosts, you can forward the current query string to preserve attribution. For external hosts, forward only the parameters you intentionally want to share. |

## Choosing a type

Use `success_page` when the buyer needs payment instructions or the most complete Scalev-hosted payment state.

Use `direct_to_whatsapp` when the next step is handled by the store's assigned sales person. The selected config state only exposes `afterCheckout.handlerAssignment`; Scalev resolves the actual handler during order creation, so redirect with `order.handlerPhone` from the created order response.

Use `direct_to_custom_whatsapp` when the next step always goes to a fixed number. Read the number from `afterCheckout.customWhatsappPhone`.

Use `other_page` when the destination is another Scalev landing page on the same host, such as a thank-you page or upsell page. Read the path from `afterCheckout.otherPagePath`.

Use `order_page` when the buyer should see the generated public invoice or order detail page.

Use `custom_url` for destinations outside the current page flow, such as a CRM handoff, external thank-you page, or custom hosted experience. Read the URL from `afterCheckout.customUrl`.

## Notes for analytics and attribution

Preserve query parameters for `other_page`. For `custom_url`, forward query parameters only when the target host is the current host or one of the known Scalev app hosts.

After `Scalev.checkout.createOrder(payload)` succeeds, HTML Checkout Pages automatically fire the configured form-submit analytics events for analytics pixels configured on the page. Redirect handling is still manual, so keep the redirect after `createOrder` resolves and add custom analytics only for intentionally separate events.

If the page has buttons or links that redirect to another URL, preserve the current query parameters that are commonly important for analytics, such as UTM, click, and affiliate parameters.
