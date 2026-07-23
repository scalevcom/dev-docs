---
title: "Advertising conversion events"
excerpt: "Set up Meta, TikTok, and SnackVideo conversion events for a Storefront API frontend."
deprecated: false
hidden: false
metadata:
  robots: index
---
Storefront API gives you server-side conversion endpoints for Meta, TikTok, and SnackVideo. These endpoints are the server relay. Your storefront still owns the browser setup: loading pixels, storing attribution IDs, choosing which conversion events to fire, building commerce payloads, and sending the same event ID to the browser pixel and Scalev server event for deduplication.

Use this page when your custom storefront is used for ads.

## How the flow works

For each conversion you want to track:

1. Load the browser pixel for the ad platform.
2. Capture attribution IDs from the landing URL and cookies.
3. Build the event parameters and item payload.
4. Generate one event ID for Meta or TikTok.
5. Fire the browser pixel event with that event ID.
6. Send the same event to Scalev's Storefront API analytics endpoint.

Scalev then sends the server-side event to the pixels configured in the store's Storefront analytics settings.

The Storefront API routes select the store from `/v3/stores/{store_id}` and `X-Scalev-Storefront-Api-Key`. Do not send a custom domain or page ID to identify the store.

```text
POST /v3/stores/{store_id}/public/analytics/meta/events
POST /v3/stores/{store_id}/public/analytics/tiktok/events
POST /v3/stores/{store_id}/public/analytics/snackvideo/events
```

All three endpoints require the publishable storefront API key:

```js
const API_BASE = "https://api.scalev.com";
const STORE_ID = "store_xxx";
const STOREFRONT_KEY = "sfpk_xxx";

const analyticsPaths = {
  meta: "/public/analytics/meta/events",
  tiktok: "/public/analytics/tiktok/events",
  snackvideo: "/public/analytics/snackvideo/events",
};

async function postScalevAnalytics(provider, payload) {
  const response = await fetch(
    `${API_BASE}/v3/stores/${STORE_ID}${analyticsPaths[provider]}`,
    {
      method: "POST",
      credentials: "omit",
      headers: {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Scalev-Storefront-Api-Key": STOREFRONT_KEY,
      },
      body: JSON.stringify(payload),
    }
  );

  if (!response.ok) {
    throw new Error(`Scalev analytics request failed: ${response.status}`);
  }
}
```

The analytics endpoints return `204 No Content` after accepting the event for asynchronous delivery.

## Configure browser pixels

The server relay does not replace browser pixels. You still need browser pixels for attribution, optimization, and Meta/TikTok deduplication.

Use the same pixel IDs that are configured in Scalev Storefront analytics. Pixel IDs are public identifiers, so you can place them in frontend config:

```js
const META_PIXEL_IDS = ["1234567890"];
const TIKTOK_PIXEL_IDS = ["CABCDEF123456"];
const SNACKVIDEO_PIXEL_IDS = ["KWAI_PIXEL_ID"];
```

Load each provider's official browser SDK once, then initialize the configured pixels:

```js
function initPixels() {
  if (window.__scalevStorefrontPixelsInitialized) return;
  window.__scalevStorefrontPixelsInitialized = true;

  for (const pixelId of META_PIXEL_IDS) {
    window.fbq?.("init", pixelId);
  }
  window.fbq?.("track", "PageView");

  for (const pixelId of TIKTOK_PIXEL_IDS) {
    window.ttq?.load(pixelId);
  }
  window.ttq?.page?.();

  for (const pixelId of SNACKVIDEO_PIXEL_IDS) {
    window.kwaiq?.load(pixelId);
  }
  window.kwaiq?.page?.();
}
```

If you use Google Tag Manager or another tag manager, keep the same rule: the browser event and the Scalev server event must use the same event name and event ID for the same shopper action.

## Allow your storefront domain in Meta

Meta uses **Traffic permissions** in Events Manager to control which domains can send events through a Meta pixel. If a Meta allow list is active and your storefront domain is not on it, Meta blocks events from that domain. The pixel can still fire in the browser, and Scalev can still accept the server relay request, but the events will not be recorded by Meta.

Set this up before you run ads or validate production events.

1. Open Meta **Events Manager**.
2. Select the pixel or dataset used by the store's Storefront analytics settings.
3. Open **Settings**.
4. In **Traffic permissions**, create or manage the allow list.
5. Add the production storefront domain that shoppers visit, such as `shop.example.com` or `example.com`.
6. Confirm the change, then test a real storefront event in Meta **Test events**.

If you add a top-level domain such as `example.com`, Meta includes its subdomains, such as `shop.example.com`. If you do not want every subdomain accepted, add the exact subdomains separately.

Keep staging, preview, and localhost domains out of a production pixel allow list unless those events should be accepted by the production dataset. When you send server events through Scalev, keep `event_source_url` on the same storefront domain you allowed in Meta.

See Meta's docs for [managing pixel traffic permissions](https://www.facebook.com/business/help/278125336598935) and [traffic permissions best practices](https://www.facebook.com/business/help/267505221173979).

## Capture attribution IDs

Capture ad click IDs as soon as the app boots. The hosted Scalev storefront stores these values:

| Source | Query parameter | Cookie | Used by |
| --- | --- | --- | --- |
| Meta click ID | `fbclid` | `_fbc` | Meta Conversions API |
| Meta browser ID | Generated when missing | `_fbp` | Meta Conversions API |
| TikTok click ID | `ttclid` | `_ttclid` | TikTok Events API |
| TikTok browser ID | Set by TikTok pixel | `_ttp` | TikTok Events API |
| SnackVideo click ID | `click_id` | `_kwai_click_id` | SnackVideo Events API |

Store click IDs for seven days. Meta browser IDs are usually kept for longer because Meta's browser pixel uses them across visits.

```js
function getCookie(name) {
  return document.cookie
    .split("; ")
    .find((row) => row.startsWith(`${name}=`))
    ?.split("=")[1];
}

function setCookie(name, value, maxAgeDays) {
  if (!value) return;

  const secure = location.protocol === "https:" ? "Secure" : "";
  document.cookie = [
    `${name}=${encodeURIComponent(value)}`,
    `Max-Age=${maxAgeDays * 24 * 60 * 60}`,
    "Path=/",
    "SameSite=Lax",
    secure,
  ].filter(Boolean).join("; ");
}

export function captureAdAttribution() {
  const params = new URLSearchParams(location.search);
  const now = Date.now();

  const fbclid = params.get("fbclid");
  if (fbclid) {
    setCookie("_fbc", `fb.1.${now}.${fbclid}`, 90);
  }

  if (!getCookie("_fbp")) {
    const random = Math.floor(Math.random() * 10000000000);
    setCookie("_fbp", `fb.1.${now}.${random}`, 90);
  }

  setCookie("_ttclid", params.get("ttclid"), 7);
  setCookie("_kwai_click_id", params.get("click_id"), 7);
}

export function currentAttribution() {
  const params = new URLSearchParams(location.search);

  return {
    fbc: decodeURIComponent(getCookie("_fbc") || ""),
    fbp: decodeURIComponent(getCookie("_fbp") || ""),
    ttclid:
      params.get("ttclid") ||
      decodeURIComponent(getCookie("_ttclid") || ""),
    ttp: decodeURIComponent(getCookie("_ttp") || ""),
    snackVideoClickId:
      params.get("click_id") ||
      decodeURIComponent(getCookie("_kwai_click_id") || ""),
  };
}
```

Run `captureAdAttribution()` before you fire page, product, cart, checkout, or order events.

## Choose events

Fire events after the shopper action succeeds. Do not fire conversion events before the API action they represent has completed.

| Storefront moment | Fire after | Meta event | TikTok event | SnackVideo event |
| --- | --- | --- | --- | --- |
| Product or bundle detail is visible | The detail API response renders | `ViewContent` | `ViewContent` | Your configured content-view event |
| Item is added to cart | `POST /public/cart/items` succeeds | `AddToCart` | `AddToCart` | Your configured add-to-cart event |
| Checkout starts | The checkout page or form opens with item context | `InitiateCheckout` | `InitiateCheckout` | Your configured checkout event |
| Buyer chooses a payment method | The payment selector is opened or a method is selected | Optional configured event | Optional configured event | Optional configured event |
| Order is created | `POST /public/checkout` or `POST /customers/me/checkout` succeeds | `Purchase` or configured submit event | `CompletePayment` or configured submit event | Your configured purchase event |
| Payment success page is shown | Only if you did not already fire the order conversion | `Purchase` | `CompletePayment` | Your configured purchase event |

Pick one conversion point for purchase optimization. If you fire purchase on order creation, do not fire another purchase event on the payment page. If you only optimize for paid orders, fire the purchase event after payment confirmation instead of order creation.

For TikTok, use the event names configured in TikTok Events Manager. For purchase optimization, TikTok commonly uses `CompletePayment`.

For SnackVideo, use the exact event names configured for the store. The Storefront API forwards the event name you send.

## Build item payloads

Scalev analytics payloads use item unique IDs, not the numeric IDs used by checkout item input.

For product variants:

```json
{
  "variant_unique_id": "variant_xxx",
  "quantity": 1
}
```

For bundle price options:

```json
{
  "bundle_price_option_unique_id": "bundle_price_option_xxx",
  "quantity": 1
}
```

Build the analytics item payload from the products, bundle price options, cart rows, or checkout rows that the event is about:

```js
function buildAnalyticsItems(items) {
  const variants = [];
  const bundle_price_options = [];

  for (const item of items) {
    if (item.type === "variant") {
      variants.push({
        variant_unique_id: item.variant_unique_id,
        quantity: item.quantity,
      });
    }

    if (item.type === "bundle_price_option") {
      bundle_price_options.push({
        bundle_price_option_unique_id: item.bundle_price_option_unique_id,
        quantity: item.quantity,
      });
    }
  }

  return {
    variants: variants.length > 0 ? variants : undefined,
    bundle_price_options:
      bundle_price_options.length > 0 ? bundle_price_options : undefined,
  };
}
```

For a product detail event, send the visible variant with quantity `1`. For a checkout or purchase event, send every item in the checkout.

## Build event parameters

Send provider-friendly commerce parameters with each event.

For Meta, common parameters are:

```js
{
  content_ids: ["variant_xxx"],
  content_type: "product",
  contents: [
    {
      id: "variant_xxx",
      quantity: 1,
      item_price: 150000,
      delivery_category: "home_delivery",
    },
  ],
  content_name: "Black T-Shirt",
  content_category: "Apparel",
  value: 150000,
  currency: "IDR",
  num_items: 1,
}
```

For TikTok, include a stable `content_id` when you can. The hosted storefront derives it from the product, bundle, or page context when the event payload does not include it.

```js
{
  content_id: "product_or_bundle_xxx",
  content_type: "product",
  contents: [
    {
      content_id: "variant_xxx",
      quantity: 1,
      price: 150000,
    },
  ],
  value: 150000,
  currency: "IDR",
}
```

For SnackVideo, send properties such as:

```js
{
  content_type: "product",
  content_category: "Apparel",
  content_name: "Black T-Shirt",
  currency: "IDR",
  value: 150000,
  quantity: 1,
  price: 150000,
}
```

Use the same integer amount format that you show for IDR totals in your storefront.

## Deduplicate Meta and TikTok events

Meta and TikTok deduplicate by event ID. Generate one event ID for one shopper action, then reuse it in both places:

- Meta browser pixel: `eventID`
- Meta Storefront API payload: `events[].event_id`
- TikTok browser pixel: `event_id`
- TikTok Storefront API payload: `events[].event_id`

For page, product, cart, and checkout interaction events, generate a random event ID:

```js
function newEventId(prefix = "evt") {
  if (crypto.randomUUID) return `${prefix}_${crypto.randomUUID()}`;
  return `${prefix}_${Date.now()}_${Math.random().toString(36).slice(2)}`;
}
```

For order submit events, use a deterministic ID based on the order. This prevents duplicate purchase events if the user retries the request or reloads the success page.

```js
function orderEventId(order, eventName) {
  return `${order.order_id}-${eventName}-FORM`;
}
```

SnackVideo's current Storefront API payload does not use `event_id`. For SnackVideo, use `click_id` for attribution and make sure your frontend does not fire the same conversion twice.

## Send a Meta event

```js
async function trackMetaEvent({
  eventName,
  eventId,
  parameters,
  userData = {},
  items = {},
}) {
  const attribution = currentAttribution();

  window.fbq?.("track", eventName, parameters, {
    eventID: eventId,
  });

  await postScalevAnalytics("meta", {
    event_source_url: location.href,
    referrer_url: document.referrer || undefined,
    user_data: {
      country: "id",
      fbc: attribution.fbc || undefined,
      fbp: attribution.fbp || undefined,
      ...userData,
    },
    events: [
      {
        event_id: eventId,
        event_name: eventName,
        parameters,
      },
    ],
    ...items,
  });
}
```

Meta user data can include `fn`, `ln`, `em`, `ph`, `ct`, `st`, `country`, `external_id`, `location_id`, `fbc`, and `fbp`. Scalev fills `client_ip_address` and `client_user_agent` from the observed API request, so you do not need to send them from the browser.

## Send a TikTok event

```js
async function trackTiktokEvent({
  eventName,
  eventId,
  parameters,
  user = {},
  items = {},
}) {
  const attribution = currentAttribution();

  window.ttq?.track(eventName, parameters, {
    event_id: eventId,
  });

  await postScalevAnalytics("tiktok", {
    event_source_url: location.href,
    referrer_url: document.referrer || undefined,
    user: {
      ttclid: attribution.ttclid || undefined,
      ttp: attribution.ttp || undefined,
      ...user,
    },
    events: [
      {
        event_id: eventId,
        event: eventName,
        parameters,
      },
    ],
    ...items,
  });
}
```

TikTok user data can include `email`, `phone`, `external_id`, `ttclid`, and `ttp`. Scalev fills `ip` from the observed API request and defaults `user_agent` from the request when you omit it.

## Send a SnackVideo event

```js
async function trackSnackVideoEvent({
  eventName,
  properties,
  items = {},
}) {
  const attribution = currentAttribution();

  for (const pixelId of SNACKVIDEO_PIXEL_IDS) {
    window.kwaiq?.instance?.(pixelId)?.track(eventName, properties);
  }

  if (!attribution.snackVideoClickId) return;

  await postScalevAnalytics("snackvideo", {
    click_id: attribution.snackVideoClickId,
    event_source_url: location.href,
    referrer_url: document.referrer || undefined,
    events: [
      {
        event_name: eventName,
        properties,
      },
    ],
    ...items,
  });
}
```

SnackVideo server events require `click_id`. If the shopper did not arrive with `click_id`, still fire the browser pixel event when configured, but skip the server event.

## Example: add to cart

Fire this after `POST /public/cart/items` succeeds:

```js
async function trackAddToCart(cartItem) {
  const item = {
    type: "variant",
    variant_unique_id: cartItem.variant.unique_id,
    quantity: cartItem.quantity,
  };

  const items = buildAnalyticsItems([item]);
  const parameters = {
    content_ids: [item.variant_unique_id],
    content_type: "product",
    contents: [
      {
        id: item.variant_unique_id,
        quantity: item.quantity,
        item_price: cartItem.unit_price,
      },
    ],
    value: cartItem.unit_price * cartItem.quantity,
    currency: "IDR",
    num_items: item.quantity,
  };

  const eventId = newEventId("add_to_cart");

  await Promise.all([
    trackMetaEvent({
      eventName: "AddToCart",
      eventId,
      parameters,
      items,
    }),
    trackTiktokEvent({
      eventName: "AddToCart",
      eventId,
      parameters: {
        ...parameters,
        content_id: item.variant_unique_id,
      },
      items,
    }),
    trackSnackVideoEvent({
      eventName: "addToCart",
      properties: parameters,
      items,
    }),
  ]);
}
```

## Example: checkout conversion

Fire the purchase conversion after checkout succeeds, unless your ad strategy only counts paid orders.

```js
async function trackOrderCreated(order, checkoutItems, buyer) {
  const items = buildAnalyticsItems(checkoutItems);
  const value = order.gross_revenue || order.total_price;

  const parameters = {
    content_ids: checkoutItems.map(
      (item) => item.variant_unique_id || item.bundle_price_option_unique_id
    ),
    content_type: "product",
    contents: checkoutItems.map((item) => ({
      id: item.variant_unique_id || item.bundle_price_option_unique_id,
      quantity: item.quantity,
      item_price: item.unit_price,
    })),
    value,
    currency: "IDR",
    num_items: checkoutItems.reduce((total, item) => total + item.quantity, 0),
  };

  await Promise.all([
    trackMetaEvent({
      eventName: "Purchase",
      eventId: orderEventId(order, "Purchase"),
      parameters,
      userData: {
        em: buyer.email,
        ph: buyer.phone,
        fn: buyer.firstName,
        ln: buyer.lastName,
        ct: buyer.city,
        st: buyer.province,
        external_id: String(order.customer_id || buyer.customerId || ""),
      },
      items,
    }),
    trackTiktokEvent({
      eventName: "CompletePayment",
      eventId: orderEventId(order, "CompletePayment"),
      parameters: {
        ...parameters,
        content_id: parameters.content_ids[0],
      },
      user: {
        email: buyer.email,
        phone: buyer.phone,
        external_id: String(order.customer_id || buyer.customerId || ""),
      },
      items,
    }),
    trackSnackVideoEvent({
      eventName: "purchase",
      properties: parameters,
      items,
    }),
  ]);
}
```

If the order response or your own fraud checks mark the order as spam, skip purchase conversion events.

## Payload reference

Meta request:

```json
{
  "event_source_url": "https://shop.example.com/products/black-shirt",
  "referrer_url": "https://facebook.com/",
  "user_data": {
    "country": "id",
    "em": "buyer@example.com",
    "ph": "628123456789",
    "fbc": "fb.1.1710000000000.fbclid",
    "fbp": "fb.1.1710000000000.1234567890",
    "external_id": "customer_123"
  },
  "events": [
    {
      "event_id": "add_to_cart_123",
      "event_name": "AddToCart",
      "parameters": {
        "content_ids": ["variant_xxx"],
        "content_type": "product",
        "value": 150000,
        "currency": "IDR"
      }
    }
  ],
  "variants": [
    {
      "variant_unique_id": "variant_xxx",
      "quantity": 1
    }
  ]
}
```

TikTok request:

```json
{
  "event_source_url": "https://shop.example.com/products/black-shirt",
  "referrer_url": "https://tiktok.com/",
  "user": {
    "email": "buyer@example.com",
    "phone": "628123456789",
    "ttclid": "ttclid_value",
    "ttp": "ttp_cookie_value",
    "external_id": "customer_123"
  },
  "events": [
    {
      "event_id": "add_to_cart_123",
      "event": "AddToCart",
      "parameters": {
        "content_id": "variant_xxx",
        "content_type": "product",
        "value": 150000,
        "currency": "IDR"
      }
    }
  ],
  "variants": [
    {
      "variant_unique_id": "variant_xxx",
      "quantity": 1
    }
  ]
}
```

SnackVideo request:

```json
{
  "click_id": "snackvideo_click_id",
  "event_source_url": "https://shop.example.com/products/black-shirt",
  "referrer_url": "https://snackvideo.com/",
  "events": [
    {
      "event_name": "addToCart",
      "properties": {
        "content_type": "product",
        "content_name": "Black T-Shirt",
        "value": 150000,
        "currency": "IDR",
        "quantity": 1
      }
    }
  ],
  "variants": [
    {
      "variant_unique_id": "variant_xxx",
      "quantity": 1
    }
  ]
}
```

## Production checklist

- Load browser pixels once per page session.
- Capture `fbclid`, `ttclid`, and `click_id` before firing events.
- Preserve `_fbp`, `_fbc`, `_ttp`, `_ttclid`, and `_kwai_click_id`.
- Add the production storefront domain to the Meta pixel traffic allow list before validating Meta events.
- Fire events only after the represented API action succeeds.
- Use one event ID for the browser and server copy of each Meta or TikTok event.
- Use deterministic order event IDs for purchase events.
- Send `event_source_url` and `referrer_url` so Scalev can choose checkout or home storefront analytics configuration.
- Send `variants` or `bundle_price_options` with item unique IDs and quantities.
- Skip SnackVideo server events when there is no `click_id`.
- Do not block checkout completion if the analytics request fails. Log it and let the buyer continue.
