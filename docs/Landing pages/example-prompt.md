---
title: "Example prompt"
excerpt: "The AI prompt Scalev generates for HTML Mode pages, ready to paste into ChatGPT or Claude."
deprecated: false
hidden: false
metadata:
  robots: index
---
The **AI Prompt Builder** in the HTML Mode **Code** tab writes a complete prompt for ChatGPT or Claude. It fills in the page name, slug, store context, selected products and bundle price options, the action after checkout succeeds, the current CSP policy, and the brief you type, so the prompt is self-contained.

The two prompts below are that output with placeholders in the generated parts. Use them when you prompt an AI tool outside the dashboard: replace every `<...>` value first, and paste your real CSP policy if the page already has entries. Use the checkout prompt for a page that creates orders and the sales prompt for a content page.

The builder also produces an Indonesian version. Switch **EN** and **ID** in the prompt builder to copy it.

## HTML Checkout Page prompt

````markdown
# Scalev HTML Mode HTML File Instructions

Create a landing page for "<page name>".
Slug: <page slug>
Page Mode: HTML Checkout Page
Selected Store: <store name> (<store unique id>)
Selected Products: <selected product variants>
Selected Bundle Price Options: <selected bundle price options>
After Checkout Success Type: <after checkout label> (success_page)

## Landing Page Intent

- Page to build: <what the page should be>
- Goal: <what the page should achieve>
- Desired visitor action: <what the visitor should do>

You are creating complete HTML for Scalev HTML Mode. The user will upload or paste it through Scalev's Import HTML flow. This prompt is self-contained; use only the context, data shapes, runtime methods, and documentation links included here.

## Output Format

Return only one complete HTML document inside a single fenced `html` code block.

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Scalev HTML Mode Page</title>
  <style>
    /* Page CSS here. */
  </style>
</head>
<body>
  <!-- Page HTML here. -->
  <script>
    // Page JavaScript here.
  <\/script>
</body>
</html>
```

## Hard Rules

- You help users create complete HTML that can be imported into Scalev HTML Mode.
- Build only a landing page experience. For checkout pages, build the selected checkout flow described in this prompt.
- Build an order form because this is an HTML Checkout Page.
- Use only the selected products and selected bundle price options listed in this prompt.
- If the selected checkout context in this prompt says Not selected or None selected, use an empty state for the missing checkout context and keep all other content grounded in the listed context.
- Use pure HTML, CSS, and JavaScript in one importable document that runs directly in the browser.
- Use the <head> only for standard document metadata, embedded CSS, and safe external fonts/assets that the user can allow in CSP. Scalev page settings own SEO, pixels, favicon, crawler settings, domains, slug, and publishing.
- Use documented `window.Scalev` methods instead of private Scalev endpoints.
- Custom JavaScript, user-owned scripts, and browser-safe external APIs are allowed only when the user intentionally wants them and is confident about the source, privacy, and security impact.
- Keep secret keys, API keys, access tokens, session tokens, cookies, and credentials out of the HTML, CSS, and JavaScript.
- For Scalev data, checkout, analytics, and prefill behavior, use documented window.Scalev methods.
- The user will import the HTML manually in Scalev. Return the importable HTML only.
- Keep the page responsive and accessible. Use semantic controls, labels, clear focus states, and mobile-first layout.
- Any external asset, script, iframe, image, font, or connect/API domain must also be added to the CSP policy in Scalev.

## Available window.Scalev Methods

Full window.Scalev reference: https://dev.scalev.com/docs/html-mode-runtime

For Scalev features, use these window.Scalev methods from JavaScript:

- `Scalev.data.get()` returns public page data provided by Scalev.
- `Scalev.data.get().store.paymentMethodOptions` returns final selectable payment option objects. Render `display` as the visitor-facing label, use `logoUrl` as the payment image source, and submit `value` as `paymentMethod`.
- Option values like `va_bri` mean virtual account for that bank. Option values like `bt:BCA:paymentAccountUid` mean manual bank transfer for that bank/account. Regular values such as `cod`, `qris`, and `invoice` keep their original values.
- Use `store.paymentMethodOptions` for checkout payment UI.
- PayLink is never listed in `store.paymentMethodOptions`. To use PayLink, render your own PayLink choice and submit `payment_link` as `paymentMethod`. Scalev then creates the order unpaid and hosts the payment page where the buyer picks the concrete method (QRIS, virtual account, or e-wallet).
- `store.isPaymentLinkEnabled === true` means PayLink checkout is forced for this page. `store.paymentMethodOptions` is empty, every order is created as `payment_link`, and the page must not render a payment selector.
- `Scalev.location.provinces()`, `cities(province.id)`, `subdistricts(city.id)`, `postalCodes(subdistrict.id)` return location data. Province and city responses use `{ id, name }`. Subdistrict responses use `{ id, name, cityName, provinceName, display }`.
- `Scalev.checkout.validateDiscount(payload)` validates a discount code. Pass the code as `discountCode`.
- `Scalev.checkout.shippingOptions(payload)` returns shipping options for selected `items`, `destination`, and `paymentMethod`. Render the returned options, use `logoUrl` as the courier image source, and submit the chosen option as `shipping`.
- `Scalev.checkout.estimateSummary(payload)` is an optional helper for buyer-facing checkout summaries. Pass the same `items`, `destination`, `paymentMethod`, and `shipping` that will be sent to `createOrder`.
- `Scalev.checkout.createOrder(payload)` creates a public order, already validates the payload, and returns the order object directly. For a `payment_link` order, `order.paymentUrl` is the Scalev-hosted PayLink page the buyer must open to pay.
- `Scalev.analytics.track(provider, payload)` tracks configured analytics events; always pass provider as `facebook`, `tiktok`, or `kwai`.
- `Scalev.prefill.get()` reads safe form prefill data from the local encrypted cookie. It returns clean nested objects such as `customer: { name, phone, email }` and `destination: { address, subdistrictId, postalCode }`. `Scalev.prefill.save(form, metadata)` persists the same clean shape locally in that cookie.

Example:

```js
const scalevData = window.Scalev.data.get();
const store = scalevData.store;
const products = store?.products || [];
const bundlePriceOptions = store?.bundlePriceOptions || [];
const paymentMethodOptions = store?.paymentMethodOptions || [];
const firstPaymentLabel = paymentMethodOptions[0]?.display;
const firstPaymentLogoUrl = paymentMethodOptions[0]?.logoUrl;
const selectedPaymentMethod = paymentMethodOptions[0]?.value || "cod";
const items = [{ type: "product", variantUniqueId: products[0].variants[0].uniqueId, quantity: 1 }];
const provinces = await window.Scalev.location.provinces({ search: "DKI" });
const cities = await window.Scalev.location.cities(provinces[0].id, { search: "Jakarta Selatan" });
const subdistricts = await window.Scalev.location.subdistricts(cities[0].id, { search: "Pesanggrahan" });
const postalCodes = await window.Scalev.location.postalCodes(subdistricts[0].id);
const destination = { subdistrictId: subdistricts[0].id, postalCode: postalCodes[0]?.postalCode };
const shippingOptions = await window.Scalev.checkout.shippingOptions({
  paymentMethod: selectedPaymentMethod,
  destination,
  items
});
const shipping = shippingOptions[0];
orderPayload.shipping = shipping;
const order = await window.Scalev.checkout.createOrder(orderPayload);
```

## Data And Payload Shapes

`Scalev.data.get()` returns `page`, `store`, and `afterCheckout`. Only the products and bundle price options selected in Scalev are included. Products are in `store.products`; bundle price options are in `store.bundlePriceOptions`.

```json
{
  "page": { "id": 1, "uniqueId": "pageUid", "username": "brand" },
  "store": {
    "id": 1,
    "uniqueId": "storeUid",
    "name": "Main Store",
    "isPaymentLinkEnabled": false,
    "paymentMethodOptions": [{ "value": "bt:BCA:paymentAccountUid", "display": "Bank Central Asia (PT Interna Cipta Asia)", "logoUrl": "https://cdn.scalev.com/icons/BT_BCA.png" }, { "value": "cod", "display": "COD", "logoUrl": "https://cdn.scalev.com/icons/cod.png" }, { "value": "va_bri", "display": "BRI Virtual Account", "logoUrl": "https://cdn.scalev.com/icons/BRI.png" }],
    "products": [{ "id": 1, "name": "Product", "variants": [{ "id": 10, "uniqueId": "variantUid", "name": "Default", "price": 99000, "availableQty": 12 }] }],
    "bundlePriceOptions": [{ "id": 20, "uniqueId": "bundleOptionUid", "name": "Bundle", "price": 179000 }]
  },
  "afterCheckout": { "type": "direct_to_whatsapp", "handlerAssignment": "rotator" }
}
```

Order payloads use `customer`, `destination`, `items`, `paymentMethod`, and `shipping`. Each item is `{ type: "product", variantUniqueId, quantity }` or `{ type: "bundle", bundlePriceOptionUniqueId, quantity }`. In the form submit flow, call `createOrder` directly after local form validation. Create orders only from an intentional visitor submit action.

For payment selection, render each `store.paymentMethodOptions[].display` label, render each payment image from `store.paymentMethodOptions[].logoUrl`, and submit only the selected option `value` as `paymentMethod`. Virtual Account options are already flat values like `va_bri`; bank-transfer account options keep `bt:BCA:paymentAccountUid`.

Do not calculate or submit `otherIncome` / `otherIncomeName` for HTML Mode checkout. Scalev calculates store-configured extra fees in `estimateSummary` and applies them again during `createOrder`. Use `estimateSummary` only if the page shows an order summary before submit, and pass the same `items`, `destination`, `paymentMethod`, and `shipping` you will later pass to `createOrder`.

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
  "items": [{ "type": "product", "variantUniqueId": "variantUid", "quantity": 1 }],
  "paymentMethod": "bt:BCA:paymentAccountUid",
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
  "discountCode": "PROMO10"
}
```

### PayLink

PayLink is the deferred payment choice: the buyer confirms the order first and picks how to pay afterwards. Use it by submitting `payment_link` as `paymentMethod` in `createOrder`. Scalev creates an unpaid order plus a Scalev-hosted PayLink page, and the buyer chooses the concrete method (QRIS, virtual account, or e-wallet) there.

Scalev excludes `payment_link` from `store.paymentMethodOptions` on purpose, so PayLink never appears in that list. Render it as your own payment choice when the page should offer it, and label it as choosing the payment method later. The rest of the order payload stays exactly the same as any other order.

When `store.isPaymentLinkEnabled` is `true`, PayLink is forced for this page: `store.paymentMethodOptions` is empty, every order is created as `payment_link`, and the page must not render a payment selector at all.

After a `payment_link` order is created, send the buyer to `order.paymentUrl` instead of the configured after-checkout action, the same way the other e-payment methods go to their payment page. Follow the same navigation rule as the other after-checkout paths: post the URL to the parent window when the page runs inside an iframe.

```js
const order = await Scalev.checkout.createOrder({ ...orderPayload, paymentMethod: "payment_link" });
if (order.paymentUrl) window.location.assign(order.paymentUrl);
```

A `payment_link` order is created without extra fees on the order itself. Store-configured extra fees and any customer-borne payment fee are quoted on the PayLink page after the buyer picks a concrete method, so an `estimateSummary` total covers the order amount only and can differ from the final amount shown on the PayLink page. `createOrder` fails with a payment-method error when the business has no PayLink method enabled; show `error.message` and keep the other payment choices usable.

## Current CSP Policy

If you use external domains for assets, scripts, iframes, fonts, images, or API calls, tell the user exactly which entries to add here:

```json
{
  "connect_src": [],
  "img_src": [],
  "media_src": [],
  "font_src": [],
  "script_src": [],
  "style_src": [],
  "frame_src": [],
  "worker_src": [],
  "manifest_src": []
}
```

## Checkout Guidance

- If the page has a form, render the form yourself in HTML.
- Read the selected store data from `Scalev.data.get().store`.
- Use only products from `store.products` and bundle price options from `store.bundlePriceOptions`; the runtime data contains the complete available checkout catalog for this page.
- Build visitor-facing payment choices directly from `store.paymentMethodOptions`; render each option `display`, use each option `logoUrl` as the payment image source, and submit the selected option `value` as `paymentMethod`.
- Treat `va_*` option values as virtual-account choices and `bt:` option values as manual bank-transfer choices. Submit exactly one payment field: `paymentMethod` from the selected payment option `value`.
- Offer PayLink by submitting `payment_link` as `paymentMethod`. It is never part of `store.paymentMethodOptions`, so add it as your own choice when the page should let the visitor pay later and pick QRIS, virtual account, or an e-wallet on the Scalev PayLink page.
- When `store.isPaymentLinkEnabled` is `true`, drop the payment selector entirely and create every order with `payment_link` as `paymentMethod`.
- After a `payment_link` order succeeds, navigate the buyer to `order.paymentUrl` (the Scalev PayLink page) instead of the configured after-checkout action.
- Validate required fields client-side before calling `Scalev.checkout.createOrder()`.
- Call `Scalev.checkout.createOrder()` directly in the form submit flow because it validates the payload before creating the order.
- Use `Scalev.checkout.estimateSummary()` only when the page needs to display totals before submit. Pass the current checkout payload with `items`, `destination`, `paymentMethod`, and the selected `shipping`. Do not call it for validation.
- Wrap `Scalev.checkout.createOrder()` in `try/catch` and show `error.message` for failed submissions. Use `error.status`, `error.data`, and diagnostics only for debugging.
- Use `uniqueId` values from `Scalev.data.get().store` for `items[].variantUniqueId` and `items[].bundlePriceOptionUniqueId` identifiers.
- Include selected `items`, `customer`, `destination`, shipping selection, and discount code from the form as `discountCode`.
- Do not include `otherIncome` or `otherIncomeName`; Scalev calculates store-configured extra fees in `estimateSummary` and applies them again during order creation.
- For shipping selection, call `Scalev.checkout.shippingOptions(payload)`, render the returned options, use each option `logoUrl` as the courier image source, and pass the selected option object as `shipping` into `estimateSummary` and `createOrder`.
- Read the selected after-checkout config state from `Scalev.data.get().afterCheckout`.
- For `direct_to_whatsapp`, use `order.handlerPhone` returned by `Scalev.checkout.createOrder()`.
- Rely on `Scalev.checkout.createOrder()` to fire the configured form-submit analytics events after the order succeeds.
- For the next action after `Scalev.checkout.createOrder()` succeeds, implement the selected after-checkout type from this prompt and follow this guide: https://dev.scalev.com/docs/html-mode-checkout-success-paths.
- After order creation, use only data returned by the window.Scalev method for buyer-facing navigation.

## Quality Bar

- Make the first viewport look like a real landing page with complete, styled content.
- Use polished spacing, typography, and responsive layout.
- Use CSS classes for styling; reserve inline styles for small dynamic states.
- Render useful static fallback content in the HTML so the first viewport has meaningful content while waiting for window.Scalev data.
- Keep JavaScript defensive: check that `window.Scalev` exists, handle loading/errors, and keep the page usable when window.Scalev calls fail.
````

## HTML Sales Page prompt

````markdown
# Scalev HTML Mode HTML File Instructions

Create a landing page for "<page name>".
Slug: <page slug>
Page Mode: HTML Sales Page
Store data: Unavailable. Build page-safe content from the user-provided brief; product selection, bundle price options, checkout, payment, shipping, and order submission are outside this page context.

## Landing Page Intent

- Page to build: <what the page should be>
- Goal: <what the page should achieve>
- Desired visitor action: <what the visitor should do>

You are creating complete HTML for Scalev HTML Mode. The user will upload or paste it through Scalev's Import HTML flow. This prompt is self-contained; use only the context, data shapes, runtime methods, and documentation links included here.

## Output Format

Return only one complete HTML document inside a single fenced `html` code block.

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Scalev HTML Mode Page</title>
  <style>
    /* Page CSS here. */
  </style>
</head>
<body>
  <!-- Page HTML here. -->
  <script>
    // Page JavaScript here.
  <\/script>
</body>
</html>
```

## Hard Rules

- You help users create complete HTML that can be imported into Scalev HTML Mode.
- Build only a landing page experience. For checkout pages, build the selected checkout flow described in this prompt.
- This is an HTML Sales Page. Build a content/lead-capture landing page focused on sections, CTA links, testimonials, FAQ, lead magnets, and brand content.
- Use only user-provided products, prices, inventory, store ids, payment methods, shipping options, and checkout behavior.
- Use pure HTML, CSS, and JavaScript in one importable document that runs directly in the browser.
- Use the <head> only for standard document metadata, embedded CSS, and safe external fonts/assets that the user can allow in CSP. Scalev page settings own SEO, pixels, favicon, crawler settings, domains, slug, and publishing.
- Use documented `window.Scalev` methods instead of private Scalev endpoints.
- Custom JavaScript, user-owned scripts, and browser-safe external APIs are allowed only when the user intentionally wants them and is confident about the source, privacy, and security impact.
- Keep secret keys, API keys, access tokens, session tokens, cookies, and credentials out of the HTML, CSS, and JavaScript.
- For Scalev page data and analytics, use documented window.Scalev methods.
- The user will import the HTML manually in Scalev. Return the importable HTML only.
- Keep the page responsive and accessible. Use semantic controls, labels, clear focus states, and mobile-first layout.
- Any external asset, script, iframe, image, font, or connect/API domain must also be added to the CSP policy in Scalev.

## Available window.Scalev Methods

window.Scalev reference: https://dev.scalev.com/docs/html-mode-runtime

For this HTML Sales Page, use these page-safe window.Scalev methods:

- `Scalev.data.get()` returns public page data provided by Scalev. Treat `store` as unavailable for this page.
- `Scalev.analytics.track(provider, payload)` tracks configured analytics events; always pass provider as `facebook`, `tiktok`, or `kwai`.

Example:

```js
const scalevData = window.Scalev?.data?.get ? window.Scalev.data.get() : { page: {}, store: null };
const page = scalevData.page || {};
```

## Data Shape

`Scalev.data.get()` returns `page` and `store`; treat `store` as unavailable when Store Context is unselected.

```json
{
  "page": { "id": 1, "uniqueId": "pageUid", "username": "brand" },
  "store": null
}
```

## Current CSP Policy

If you use external domains for assets, scripts, iframes, fonts, images, or API calls, tell the user exactly which entries to add here:

```json
{
  "connect_src": [],
  "img_src": [],
  "media_src": [],
  "font_src": [],
  "script_src": [],
  "style_src": [],
  "frame_src": [],
  "worker_src": [],
  "manifest_src": []
}
```

## Sales Page Guidance

- Treat this as a content/lead-capture landing page. Use sections, CTA links, testimonials, FAQ, lead magnets, and brand content.
- If you include a form, keep it as a client-side UI pattern only.
- Use page-safe methods only: `Scalev.data.get()` and `Scalev.analytics.track()`.
- Mention only available products, bundles, prices, inventory, payment methods, shipping options, and order creation details provided by the user.

## Quality Bar

- Make the first viewport look like a real landing page with complete, styled content.
- Use polished spacing, typography, and responsive layout.
- Use CSS classes for styling; reserve inline styles for small dynamic states.
- Render useful static fallback content in the HTML so the first viewport has meaningful content while waiting for window.Scalev data.
- Keep JavaScript defensive: check that `window.Scalev` exists, handle loading/errors, and keep the page usable when window.Scalev calls fail.
````

## After the AI returns the HTML

The prompt asks for one complete HTML document. Bring it back with **Import HTML** in the **Code** tab, either as an uploaded `.html` file or pasted text, then review the split code and publish. See [Create landing page (HTML Mode)](/docs/create-landing-page-html-mode) for the full flow.

If the AI names external domains for fonts, images, scripts, or API calls, add them in the **Security** tab before publishing. Requests to domains that are not in the CSP policy are blocked.
