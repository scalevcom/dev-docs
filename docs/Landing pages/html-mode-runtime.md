---
title: "HTML Mode runtime"
excerpt: "Use the window.Scalev runtime methods available inside Scalev HTML Mode pages."
deprecated: false
hidden: false
metadata:
  robots: index
---
Scalev HTML Mode pages can use `window.Scalev` from browser JavaScript. The runtime gives your page safe page context, selected store context, checkout helpers, analytics forwarding, form prefill helpers, and diagnostics while keeping private API tokens server-side.

This page is written for developers and AI agents that generate HTML Mode files. Use these methods instead of calling private Scalev URLs directly.

## Availability

The runtime is available on rendered HTML Mode pages. In local editor previews, some methods can return stubbed preview data.

```js
const scalev = window.Scalev;

if (!scalev) {
  // Keep the page usable while runtime data loads.
}
```

Most methods are asynchronous and return a `Promise`. `Scalev.data.get()` and `Scalev.diagnostics.get()` are synchronous.

Runtime method payloads and responses use camelCase object keys. The runtime handles the backend casing internally, so page JavaScript should not send snake_case keys. Runtime methods also return the JavaScript-visible result directly. They remove backend collection containers such as `data` and `is_paginated` before returning arrays.

String enum values and provider-owned blobs keep their original values. For example, `success_page`, `direct_to_whatsapp`, analytics `parameters`, `metadata`, and `customData` are not renamed.

## Store context

When Store Context is selected, `Scalev.data.get().store` includes only the selected store summary, products, and bundle price options. Treat it as the page-specific checkout catalog.

When HTML Checkout Page is selected, `Scalev.data.get().afterCheckout` includes the selected after-checkout success type and its public destination config.

When Store Context is unselected, treat `store` as unavailable. Build a regular landing page and rely only on page-safe methods such as `Scalev.data.get()`, `Scalev.analytics.track()`, and `Scalev.prefill.get()`.

## Security rules

- Keep API keys, business-user JWTs, storefront API keys, customer tokens, cookies, and credentials out of page JavaScript.
- Use documented `window.Scalev` methods instead of private Scalev URLs or private APIs.
- Create orders only after a visitor intentionally submits a form.
- Prefer `Scalev.checkout.createOrder()` on submit; it validates the payload before the order is persisted.
- Use only selected products, bundles, prices, inventory, payment methods, shipping options, and customer identity values present in the runtime data.

## `Scalev.data.get()`

Returns public page data injected into the rendered page.

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

Use `store.paymentMethodOptions` to render payment choices. Render `display`, show `logoUrl`, and submit the selected `value` as `paymentMethod`.

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

`provinces`, `cities`, and `subdistricts` accept optional query objects:

```js
const provinces = await Scalev.location.provinces({ search: "Jawa" });
```

Province and city responses use `{ id, name }`. Subdistrict responses use `id` and `name` for the subdistrict, plus `cityName`, `provinceName`, and `display` for address labels.

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
  "otherIncome": 0,
  "otherIncomeName": "Biaya Lainnya",
  "grossRevenue": 273300
}
```

Use `estimateSummary` only when the checkout UI displays totals before submit. Do not calculate or submit `otherIncome` or `otherIncomeName`; Scalev calculates store-configured extra fees in `estimateSummary` and applies them again during `createOrder`.

## `Scalev.checkout.createOrder(payload)`

Creates a real public order and validates the payload. Call this only after a visitor intentionally submits the form.

```js
async function submitOrder(event) {
  event.preventDefault();

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
      name: event.currentTarget.elements.customerName.value,
      phone: event.currentTarget.elements.customerPhone.value,
      email: event.currentTarget.elements.customerEmail.value
    },
    destination: {
      address: event.currentTarget.elements.address.value,
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
  "publicOrderUrl": "https://brand.myscalev.com/order/orderSecretSlug",
  "paymentUrl": null,
  "productPrice": "90000.00",
  "productDiscount": "0.00",
  "shippingCost": "15300.00",
  "shippingDiscount": "0.00",
  "discountCodeDiscount": "10000.00",
  "otherIncome": "0.00",
  "otherIncomeName": "Biaya Lainnya",
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

### Error handling

Runtime methods reject the `Promise` with a JavaScript `Error`. Use `error.message` for UI copy. Use `error.status`, `error.data`, and `Scalev.diagnostics.get()` only for debugging.

```js
try {
  const order = await Scalev.checkout.createOrder(payload);
  return order;
} catch (error) {
  showFormError(error.message || "Order creation failed.");
}
```

## `Scalev.analytics.track(provider, payload)`

Forwards configured analytics events through Scalev.

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

Supported provider names:

- `facebook`
- `tiktok`
- `kwai`

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

Persists safe browser-scoped form prefill data in the encrypted `scv_fd` cookie. This is handled locally by fe-public and does not call a Storefront or page runtime API endpoint.

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
