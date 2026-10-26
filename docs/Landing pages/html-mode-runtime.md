---
title: "Landing page runtime"
excerpt: "Use window.Scalev for page data, checkout, location lookup, analytics, and visitor prefill."
deprecated: false
hidden: false
metadata:
  robots: index
---
The landing page runtime exposes `window.Scalev` to your page JavaScript. Use it to read public page and store data, look up locations, handle checkout, send analytics events, and manage visitor prefill.

Use the documented methods instead of calling private Scalev URLs directly. Scalev manages authentication and validates checkout requests for the current page.

## Availability

The runtime is available on published HTML Mode pages and Builder pages served in **Fast mode**. Check for the methods you need before enabling controls that depend on them; a standard Builder page may not expose this API.

On HTML Mode pages, Scalev inserts the runtime before the trailing top-level script block. Scripts that run earlier should initialize after `DOMContentLoaded`. This pattern also handles scripts loaded after that event:

```js
function initializePage() {
  const scalev = window.Scalev;
  if (!scalev?.data?.get) {
    // Leave controls that require the runtime disabled.
    return;
  }

  const data = scalev.data.get();
  // Render your controls from data, then attach handlers before enabling them.
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initializePage, { once: true });
} else {
  initializePage();
}
```

External scripts and resources need the appropriate page CSP permission. Preserve script order when one script depends on another.

HTML Mode editor previews simulate commerce, location, and prefill behavior. They do not create real orders or send platform analytics. Simulated orders include `redirectUrl: "#scalev-preview-order"`. Verify your integration on a published page before treating it as a working checkout.

Most methods are asynchronous and return a `Promise`. `Scalev.data.get()`, `Scalev.diagnostics.get()`, and `Scalev.checkout.updateIntent()` are synchronous.

Runtime method payloads and responses use camelCase object keys. The runtime handles the backend casing internally, so page JavaScript should not send snake_case keys. Runtime methods also return the JavaScript-visible result directly. They remove backend collection containers such as `data` and `is_paginated` before returning arrays.

String enum values and provider-owned blobs keep their original values. For example, `success_page`, `direct_to_whatsapp`, analytics `parameters`, `metadata`, and `customData` are not renamed.

## Store context

`Scalev.data.get().store` contains the store summary, products, and bundle price options available to the current page. Treat it as the page-specific checkout catalog. For an HTML Mode page, select **Store Context** and the products or bundles you want to make available.

`Scalev.data.get().afterCheckout`, when present, describes the page's after-checkout configuration. After checkout, use the resolved `order.redirectUrl` from `Scalev.checkout.createOrder()` instead of rebuilding a URL from this configuration.

If the page has no store context, treat `store` as unavailable. Rely on methods such as `Scalev.data.get()`, `Scalev.analytics.track()`, and `Scalev.prefill.get()` without adding checkout controls.

## Security rules

- Keep API keys, business-user JWTs, storefront API keys, customer tokens, cookies, and credentials out of page JavaScript.
- Use documented `window.Scalev` methods instead of private Scalev URLs or private APIs.
- Create orders only after a visitor intentionally submits a form.
- Prefer `Scalev.checkout.createOrder()` on submit; it validates the payload before the order is persisted.
- Use only selected products, bundles, prices, inventory, payment methods, shipping options, and customer identity values present in the runtime data.

## `Scalev.data.get()`

Returns the current page's public data synchronously. Visitor prefill and internal analytics configuration are excluded. Read visitor-specific form values through `Scalev.prefill.get()`.

```js
const data = Scalev.data.get();
```

Response example:

```json
{
  "page": {
    "id": 1,
    "uniqueId": "pageUid",
    "username": "brand"
  },
  "store": {
    "id": 1,
    "uniqueId": "storeUid",
    "name": "Main Store",
    "paymentMethodOptions": [
      {
        "value": "bt:BCA:paymentAccountUid",
        "display": "Bank Central Asia",
        "logoUrl": "https://cdn.scalev.com/icons/BT_BCA.png"
      },
      {
        "value": "cod",
        "display": "COD",
        "logoUrl": "https://cdn.scalev.com/icons/cod.png"
      }
    ],
    "products": [
      {
        "id": 1,
        "name": "Product",
        "variants": [
          {
            "id": 10,
            "uniqueId": "variantUid",
            "name": "Default",
            "price": 99000,
            "availableQty": 12
          }
        ]
      }
    ],
    "bundlePriceOptions": [
      {
        "id": 20,
        "uniqueId": "bundleOptionUid",
        "name": "Bundle",
        "price": 179000
      }
    ]
  },
  "afterCheckout": {
    "type": "other_page",
    "otherPagePath": "/thank-you"
  }
}
```

Use `store.paymentMethodOptions` to render payment choices. Render `display`, show `logoUrl`, and submit the selected `value` as `paymentMethod`. Scalev omits e-payment methods that cannot be executed with a verified fee schedule when the store passes provider transaction fees to the customer; do not recreate hidden options from saved store configuration.

Payment option values are already flattened:

- `va:BRI` means virtual account for BRI.
- `bt:BCA:paymentAccountUid` means manual bank transfer for the represented BCA account.
- Regular values such as `cod`, `qris`, `invoice`, `alfamart`, or `gopay` keep their original values.

## Location methods

Use these methods for address and shipping forms.

```js
const provinces = await Scalev.location.provinces();
const cities = await Scalev.location.cities(provinces[0].id);
const subdistricts = await Scalev.location.subdistricts(cities[0].id);
const postalCodes = await Scalev.location.postalCodes(subdistricts[0].id);
```

Use `Scalev.location.search({ search: "Cakung", pageSize: 20 })` to search kelurahan/desa across cities. It returns normalized location rows. Use **Kecamatan/Kelurahan** as the picker label. `subdistricts(cityId)` is a cascading lookup and requires a selected city; it is not a global search.

For a search picker that loads more results, pass `{ pagination: true }` as the second argument. The response then contains `data`, `hasNext`, and `nextCursor`. Pass the returned cursor with the same search query to load the next batch. Numeric `page` parameters are not supported.

```js
const first = await Scalev.location.search(
  { search: "Bandung", pageSize: 25 },
  { pagination: true }
);
if (first.hasNext && first.nextCursor) {
  const next = await Scalev.location.search(
    { search: "Bandung", pageSize: 25, nextCursor: first.nextCursor },
    { pagination: true }
  );
}
```

Omit the second argument to keep the default array response.

`search`, `provinces`, `cities`, and `subdistricts` accept optional query objects:

```js
const provinces = await Scalev.location.provinces({ search: "Jawa" });
```

Province and city responses use `{ id, name }`. Location search and subdistrict responses use `id`, `name`, `kelurahanName`, `cityName`, `provinceName`, and `display`. The `name` combines the kecamatan and kelurahan, such as `Coblong, Sekeloa`; `kelurahanName` is `null` on legacy kecamatan rows. Render full labels with `[row.provinceName, row.cityName, row.name].filter(Boolean).join(", ")`. Do not split `display` to infer administrative fields.

Despite its historical name, `destination.subdistrictId` takes the selected location row ID, including a kelurahan/desa row. Pass that same ID to `postalCodes` and checkout helpers. Saved legacy kecamatan IDs remain valid; never replace a selected row with its parent ID.

Response examples:

```json
[
  {
    "id": 31,
    "name": "DKI Jakarta"
  }
]
```

```json
[
  {
    "id": 3171,
    "name": "Kota Jakarta Pusat"
  }
]
```

```json
[
  {
    "id": 9090,
    "name": "Gambir",
    "kelurahanName": null,
    "cityName": "Kota Jakarta Pusat",
    "provinceName": "DKI Jakarta",
    "display": "Gambir, Kota Jakarta Pusat, DKI Jakarta"
  }
]
```

```json
[
  {
    "postalCode": "10110"
  }
]
```

## `Scalev.checkout.updateIntent(payload)`

Schedules a debounced checkout-intent snapshot and returns synchronously. Use the same `customer`, `destination`, `items`, `paymentMethod` and `discountCode` fields as your checkout payload when your controls are not represented by the standard form fields the runtime observes.

This method does not complete an intent. Completion belongs to a successful `Scalev.checkout.createOrder()` response. Do not mark checkout complete on a click, failed request or redirect attempt.

## `Scalev.checkout.validateDiscount(payload)`

Validates a discount code for a checkout payload.

```js
const result = await Scalev.checkout.validateDiscount({
  discountCode: "PROMO10",
  grossRevenue: 179000,
  netProductPrice: 179000,
  shippingCost: 0,
  paymentMethod: store.paymentMethodOptions?.[0]?.value || "cod"
});
```

Response example:

```json
{
  "discountCode": {
    "code": "PROMO10",
    "appliedTo": "product_price",
    "amountType": "fixed",
    "amount": 10000,
    "isEnabled": true
  },
  "eligibilityDetails": {
    "isEnabled": true,
    "isExpiryCheck": true,
    "isUsageLimitCheck": true,
    "isMinimumRevenueCheck": true,
    "isLimitedToPagesCheck": true,
    "isLimitedToPaymentMethodsCheck": true,
    "isPageDiscountActive": true,
    "isAmountNotZero": true
  },
  "isEligible": true,
  "discountCodeDiscount": 10000
}
```

## `Scalev.checkout.shippingOptions(payload)`

Returns shipping options for the selected items, destination, and payment method. Use this as the only shipping lookup method.

```js
const shippingOptions = await Scalev.checkout.shippingOptions({
  paymentMethod: selectedPaymentOption.value,
  destination: {
    subdistrictId: selectedSubdistrictId,
    postalCode: selectedPostalCode
  },
  items: [
    {
      type: "product",
      variantUniqueId: firstVariant.uniqueId,
      quantity: 1
    }
  ]
});
```

Pass the chosen option back as one `shipping` field in `estimateSummary` and `createOrder`. The runtime prepares the checkout request from that option. Options include `logoUrl` when a courier code is available.

Response example:

```json
[
  {
    "courierServiceId": 48,
    "courierCode": "anteraja",
    "serviceCode": "ND",
    "name": "Next Day",
    "cost": 15300,
    "etd": "1",
    "isCod": false,
    "warehouseUniqueId": "warehouseUid",
    "courierAggregatorCode": null,
    "logoUrl": "https://cdn.scalev.com/assets/images/kurir/anteraja.png"
  }
]
```

Recommended method payload:

```json
{
  "items": [
    { "type": "product", "variantUniqueId": "variantUid", "quantity": 1 },
    {
      "type": "bundle",
      "bundlePriceOptionUniqueId": "bundleOptionUid",
      "quantity": 1
    }
  ],
  "destination": { "subdistrictId": 12345, "postalCode": "10110" },
  "paymentMethod": "cod"
}
```

## `Scalev.checkout.estimateSummary(payload)`

Returns a checkout summary for pages that show a buyer-facing breakdown before submit.

This method is optional. Pass the same item, destination, payment, and `shipping` that you will send to `Scalev.checkout.createOrder(payload)`.

The result does not replace order creation validation. Scalev still validates and applies final shipping, discount, extra-fee, and total amounts during order creation before the order is persisted.

```js
const shipping = shippingOptions[0];

const payload = {
  destination: { subdistrictId: 12345, postalCode: "10110" },
  items: [
    { type: "product", variantUniqueId: firstVariant.uniqueId, quantity: 1 },
    {
      type: "bundle",
      bundlePriceOptionUniqueId: firstBundlePriceOption.uniqueId,
      quantity: 1
    }
  ],
  paymentMethod: selectedPaymentOption.value,
  shipping
};

const summary = await Scalev.checkout.estimateSummary(payload);
```

Recommended method payload:

```json
{
  "items": [
    { "type": "product", "variantUniqueId": "variantUid", "quantity": 1 },
    {
      "type": "bundle",
      "bundlePriceOptionUniqueId": "bundleOptionUid",
      "quantity": 1
    }
  ],
  "destination": { "subdistrictId": 12345, "postalCode": "10110" },
  "paymentMethod": "cod",
  "shipping": {
    "courierServiceId": 48,
    "courierCode": "anteraja",
    "serviceCode": "ND",
    "name": "Next Day",
    "cost": 15300,
    "etd": "1",
    "isCod": false,
    "warehouseUniqueId": "warehouseUid",
    "courierAggregatorCode": null,
    "logoUrl": "https://cdn.scalev.com/assets/images/kurir/anteraja.png"
  }
}
```

Response example:

```json
{
  "productPrice": 268000,
  "shippingCost": 15300,
  "otherIncome": 6500,
  "otherIncomeName": "Biaya Penanganan",
  "serviceFee": 2500,
  "grossRevenue": 292300
}
```

During delivery selection, you can explicitly pass `allowIncomplete: true`. If the address or shipping choice is incomplete, the response contains `{ isComplete: false, productPrice }` with current product pricing and no payable total. Display it as a product subtotal and keep checkout disabled until a later complete summary succeeds. Invalid items and unavailable shipping still return errors. Omitting this flag keeps the existing validation behavior. Never use an incomplete subtotal as `grossRevenue` or as permission to create an order.

Pass `includeBreakdown: true` to request backend-owned receipt details. The response additionally contains `lines` with `{ name, quantity, unitPrice, amount }`, `productDiscount`, and, for complete quotes, `discountCodeDiscount`. Amounts are decimal strings. Display these returned amounts directly; do not recalculate bundle discounts, eligibility or payment fees in page code. An incomplete quote can include lines but still has no payable total. Older servers may omit these optional fields; retain the aggregate subtotal in that case.

You can also pass `includeProvisional: true` with `allowIncomplete: true`. While delivery is missing, the response can include a separate `provisional` receipt with backend-calculated product prices, fees, discounts and `grossRevenue`, excluding shipping. Render those amounts directly. Keep `isComplete: false` authoritative: the provisional receipt never permits creating an order. You may allow the form button to show required-field validation, but do not call `createOrder` until a complete summary succeeds.

Older servers may omit `provisional`; continue showing only the product subtotal in that case.

Use `estimateSummary` when the checkout UI displays totals before submit. Refresh it whenever the selected items, quantities, destination, shipping option, discount, or payment method changes. Render `otherIncome` with `otherIncomeName` when it is non-zero, and render one `Biaya layanan` or `Service fee` row from `serviceFee` when it is non-zero.

`otherIncome` remains the store's existing Other Charges concept. `serviceFee` is one combined customer-facing fee for direct e-payment. Both can be non-zero in the same checkout. Scalev calculates Other Charges first, then uses the checkout amount plus `otherIncome` as the base for the Service Fee, and `grossRevenue` is the displayed and charged total.

Both fees are calculated by Scalev from the store's saved Service Fee and Other Charges settings. The page does not send a fee policy, a fee amount, or a fee quote, and there is no fee field to echo back into `createOrder`. Order creation recalculates both fees from the same store settings, so treat every summary value as a preview for the buyer. `serviceFee` is zero when the store charges no customer fee for the selected method, and it is always zero for `cod`, other non-e-payment methods, and `payment_link`, while saved Other Charges rules still apply.

A `payment_link` order is always created with `otherIncome` of zero, whatever the request contains. The Payment Link snapshots the store's Other Charges configuration and quotes both fees on the Scalev-hosted payment page once the buyer picks a concrete method.

## `Scalev.checkout.createOrder(payload)`

Creates a real public order and validates the payload. Call this only after a visitor intentionally submits the form.

```js
async function submitOrder(event) {
  event.preventDefault();
  const form = event.currentTarget;

  const data = Scalev.data.get();
  const store = data.store;
  const firstVariant = store.products[0].variants[0];
  const selectedPaymentOption = store.paymentMethodOptions[0];
  const selectedSubdistrictId = 12345;
  const selectedPostalCode = "10110";
  const items = [
    { type: "product", variantUniqueId: firstVariant.uniqueId, quantity: 1 }
  ];
  const destination = {
    subdistrictId: selectedSubdistrictId,
    postalCode: selectedPostalCode
  };
  const shippingOptions = await Scalev.checkout.shippingOptions({
    paymentMethod: selectedPaymentOption.value,
    destination,
    items
  });
  const shipping = shippingOptions[0];

  const payload = {
    customer: {
      name: form.elements.customerName.value,
      phone: form.elements.customerPhone.value,
      email: form.elements.customerEmail.value
    },
    destination: {
      address: form.elements.address.value,
      ...destination
    },
    items,
    paymentMethod: selectedPaymentOption.value,
    shipping
  };

  const order = await Scalev.checkout.createOrder(payload);
  return order;
}
```

Supported payload fields:

- Customer object: `customer.name`, `customer.phone`, `customer.email`
- Destination object: `destination.address`, `destination.subdistrictId`, `destination.postalCode`
- Payment field: `paymentMethod`
- Items list: `items[]` with `{ type: "product", variantUniqueId, quantity }` or `{ type: "bundle", bundlePriceOptionUniqueId, quantity }`
- Discount field: `discountCode`
- Optional post-payment override: `isPostPaymentRedirectEnabled` and `postPaymentRedirectUrl`

The post-payment fields are creation-only API inputs; Scalev does not add them as controls to your public form. Omit both fields to inherit the Checkout Page setting. Send `isPostPaymentRedirectEnabled: false` to force Scalev's hosted success flow for that order. Send `isPostPaymentRedirectEnabled: true` with an absolute HTTPS `postPaymentRedirectUrl` to replace the page setting for that order. Scalev snapshots the result, so an order update cannot change it later.

Do not submit top-level product or shipping discount fields. Product price and item-level adjustments belong on `items[]` when needed. Use `validateDiscount` to preview eligible discount code amounts, then pass the selected code as `discountCode` to `createOrder`.

For shipping selection, call `Scalev.checkout.shippingOptions(payload)`, let the visitor choose one option, then pass that whole option as `shipping` into summary and order calls.

Recommended method payload:

```json
{
  "customer": {
    "name": "Customer Name",
    "phone": "08123456789",
    "email": "customer@example.com"
  },
  "destination": {
    "address": "Customer address",
    "subdistrictId": 12345,
    "postalCode": "10110"
  },
  "items": [
    { "type": "product", "variantUniqueId": "variantUid", "quantity": 1 }
  ],
  "paymentMethod": "cod",
  "shipping": {
    "courierServiceId": 48,
    "courierCode": "anteraja",
    "serviceCode": "ND",
    "name": "Next Day",
    "cost": 15300,
    "etd": "1",
    "isCod": false,
    "warehouseUniqueId": "warehouseUid",
    "courierAggregatorCode": null,
    "logoUrl": "https://cdn.scalev.com/assets/images/kurir/anteraja.png"
  },
  "discountCode": "PROMO10",
  "eventSourceUrl": "https://brand.myscalev.com/page",
  "utmSource": "ads"
}
```

For payment selection, render `store.paymentMethodOptions[].display`, render payment images from `store.paymentMethodOptions[].logoUrl`, and submit only the selected option `value` as `paymentMethod`.

Response example:

```json
{
  "orderId": "260601HPQSPBX",
  "status": "pending",
  "paymentStatus": "unpaid",
  "secretSlug": "orderSecretSlug",
  "redirectUrl": "https://brand.myscalev.com/o/orderSecretSlug/success",
  "publicOrderUrl": "https://brand.myscalev.com/o/orderSecretSlug",
  "paymentUrl": null,
  "productPrice": "90000.00",
  "productDiscount": "0.00",
  "shippingCost": "15300.00",
  "shippingDiscount": "0.00",
  "discountCodeDiscount": "10000.00",
  "otherIncome": "0.00",
  "otherIncomeName": "Biaya Lainnya",
  "serviceFee": "0.00",
  "grossRevenue": "95300.00",
  "paymentMethod": "bank_transfer",
  "paymentAccount": {
    "uniqueId": "paymentAccountUid",
    "financialEntityName": "Bank Central Asia",
    "accountNumber": "1234567890"
  },
  "courierService": {
    "id": 48,
    "name": "Next Day",
    "courier": {
      "name": "AnterAja",
      "code": "anteraja"
    }
  },
  "variants": {},
  "bundlePriceOptions": {
    "Bundle": {
      "bundlePriceOptionUniqueId": "bundleOptionUid",
      "quantity": 1
    }
  },
  "handlerPhone": null,
  "chatMessage": null
}
```

### After order creation

`createOrder` returns the order directly and does not navigate. The Scalev API resolves the immediate destination as `redirect_url`; the runtime exposes it as `order.redirectUrl`. This covers the configured After Checkout destination and payment-specific behavior, including PayLink and WhatsApp. If the configured destination cannot be resolved, the server returns the Scalev-hosted payment-instructions page (`/o/{secret_slug}/success`) as `order.redirectUrl`.

```js
const order = await Scalev.checkout.createOrder(payload);
const target = typeof order.redirectUrl === "string"
  ? order.redirectUrl.trim()
  : "";

if (target) {
  if (window.self !== window.top) {
    // Use the embedding parent's exact origin when you control it.
    window.parent.postMessage(target, "*");
  } else {
    window.location.assign(target);
  }
} else {
  // Handle older or unexpected responses without a redirect. Offer the returned
  // order.publicOrderUrl as a link; do not submit the order again.
  showOrderCreated(order);
}
```

Open the returned URL unchanged. Do not derive the destination from `afterCheckout`, infer it from a payment-method list, re-encode a WhatsApp message, or append the current query string. `order.paymentUrl` (the API's order-level `payment_url`) is deprecated and returned for backward compatibility only. Always use `order.redirectUrl` for checkout navigation, including PayLink. If an older or unexpected response has a missing or empty `redirectUrl`, the order can still have been created successfully; keep the buyer on the page, show a confirmation, and offer `order.publicOrderUrl` when available. Do not fall back to `paymentUrl`. This deprecation does not apply to provider URL fields inside a raw gateway payload.

This immediate redirect is separate from the post-payment destination snapshot. The page's post-payment setting stays private; hosted Scalev pages use the order's snapshot only after its payment status becomes `paid` or `settled`. Neither redirect proves payment. Provision external access from a verified `payment.received` webhook.

See [HTML Mode checkout success types](/docs/html-mode-checkout-success-paths) for the destination types, embedding behavior, and a reusable navigation helper.

### Error handling

Runtime methods reject the `Promise` with a JavaScript `Error`. Use `error.message` for UI copy. Use `error.status`, `error.data`, and `Scalev.diagnostics.get()` only for debugging.

Order errors also expose `error.orderOutcome`:

| Value | Meaning | Next action |
| --- | --- | --- |
| `not_submitted` | Validation or security verification failed before sending the order. | Correct the problem and allow another explicit submission. |
| `rejected` | The order endpoint rejected the request. | Show the error and allow the visitor to correct it. |
| `unknown` | The response was lost or the service could not confirm the outcome. An order may already exist. | Keep repeat submission blocked until the outcome is checked. |

Provide a loading state for your custom form and disable submission while a request is in flight. Calling `createOrder` does not add loading UI to your custom markup. Do not automatically retry an order. A successful order remains successful if saving prefill or forwarding analytics later fails.

```js
try {
  const order = await Scalev.checkout.createOrder(payload);
  return order;
} catch (error) {
  showFormError(error.message || "Order creation failed.");
}
```

## `Scalev.analytics.track(provider, payload)`

Forwards configured advertising-provider events through Scalev. These events are separate from [Web Analytics reports](/docs/web-analytics); this method does not create a first-party page view. Use the Web Analytics reporting API from your backend to read hosted-page traffic.

```js
await Scalev.analytics.track("facebook", {
  firstName: "Customer",
  phone: "08123456789",
  variants: [{ uniqueId: "variantUid", quantity: 1, price: 179000 }],
  events: [
    {
      eventName: "Lead",
      parameters: { value: 179000, currency: "IDR" }
    }
  ]
});
```

For Meta events, the runtime sends the configured browser pixel and server event with the same event ID. Visitor consent applies to both; unrelated pixels initialized by your own code are not targeted. A missing browser SDK does not prevent an allowed server event. Requests use keepalive when the final encoded body fits its 64 KiB limit; larger events use ordinary delivery and are not guaranteed to finish during navigation.

Supported provider names:

- `facebook` (aliases: `fb`, `meta`)
- `tiktok`
- `kwai` (alias: `snackvideo`)
- `google_ads` (alias: `google`)

For native Google Ads, first connect Google and configure the event-to-action
mapping in **Settings → Analytics → Google Ads**, then assign the destination
to this page or storefront. GTM is not required. The Google runtime sends browser
and server conversions with the same interaction ID:

```js
const interactionId = crypto.randomUUID();
await Scalev.analytics.track("google_ads", {
  eventName: "Contact",
  interactionId,
  parameters: { value: 0, currency: "IDR" }
});
```

Keep `interactionId` when retrying the same interaction. Generate a new ID for a
new interaction. If you also configure a widget event for the same interaction,
pass that ID to `Scalev.analytics.trackWidgetEvents({ googleAdsEvents: ["Contact"],
googleAdsEventsParameters: {}, interactionId })`. Google deduplicates only within
the same conversion action. Use the page and widget event editors for normal
configuration; you do not need to write JavaScript for those events.

The native cart and checkout methods already send their automatic events.
`Purchase` is not accepted by this generic method or by page/button mappings;
it follows the order's payment and eligibility rules. A resolved call does not
prove Google ingestion, attribution or bidding use. Inspect delivery diagnostics
in Scalev. Advertising permission applies to both channels. Product remarketing
requires explicit feed-ID configuration and applicable consent; missing feed
mappings do not disable conversion tracking.

Response example:

```json
null
```

If no provider is passed, the runtime skips the call without contacting Scalev:

```json
{
  "skipped": true,
  "reason": "missing_analytics_provider"
}
```

If the analytics request fails, the checkout flow should continue and the runtime returns:

```json
{
  "skipped": true,
  "reason": "analytics_request_failed"
}
```

## `Scalev.prefill.get()`

Reads safe browser-scoped form prefill data.

```js
const prefill = await Scalev.prefill.get();
const customerName = prefill.customer?.name || "";
const customerPhone = prefill.customer?.phone || "";
const destinationAddress = prefill.destination?.address || "";
```

Response example:

```json
{
  "customer": {
    "name": "Customer Name",
    "phone": "08123456789",
    "email": "customer@example.com"
  },
  "destination": {
    "address": "Jl. Contoh No. 1",
    "subdistrictId": 9104,
    "postalCode": "12250"
  }
}
```

## `Scalev.prefill.save(form, metadata)`

Persists safe browser-scoped form prefill data in an encrypted cookie. Use this method rather than reading or writing the cookie yourself.

```js
await Scalev.prefill.save(
  {
    customer: {
      name: "Customer Name",
      phone: "08123456789",
      email: "customer@example.com"
    },
    destination: {
      address: "Jl. Contoh No. 1",
      subdistrictId: 9104,
      postalCode: "12250"
    }
  },
  {
    source: "checkout_form"
  }
);
```

Response example:

```json
{
  "saved": true
}
```

## `Scalev.diagnostics.get()`

Returns recent runtime diagnostics for debugging.

```js
const diagnostics = Scalev.diagnostics.get();
```

Response example:

```json
[
  {
    "level": "error",
    "code": "runtime_request_failed",
    "message": "Scalev runtime request failed.",
    "details": {
      "path": "/pages/pageUid/orders",
      "status": 422,
      "response": {
        "message": "customer.phone: can't be blank"
      }
    },
    "timestamp": "2026-06-01T08:00:00.000Z"
  }
]
```

Scalev editors display the Google conversion-action name with its Scalev trigger
as context. The trigger remains the stable API key, so changing a display label
does not change event identity or Purchase eligibility.
