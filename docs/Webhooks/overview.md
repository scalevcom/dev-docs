---
title: Overview
excerpt: This document outlines how webhooks in Scalev are implemented.
deprecated: false
hidden: false
metadata:
  robots: index
---
Webhooks are ways for Scalev to notify you when certain events happen. When the specified events occur, Scalev will send an HTTP POST request to the webhook URL you provided. You can use webhooks to trigger custom code or actions in your system.

Webhooks are sent as POST requests with a JSON payload in the request body. The payload contains the event type and the data associated with the event. The webhook URL must be a publicly accessible URL that can receive POST requests from Scalev.

## Verifying a Webhook Request

To authenticate webhook requests from Scalev, verify the signature included in the `X-Scalev-Hmac-Sha256` header. This signature is created using your Client Secret as the key in an HMAC-SHA256 algorithm. To validate each request:

1. Extract the signature from the `X-Scalev-Hmac-Sha256` header
2. Calculate your own HMAC-SHA256 digest using your Client Secret
3. Compare your calculated digest with the received signature

If the signatures match, you can trust that the webhook came from Scalev and wasn't tampered with.

Here are code examples to help you validate the webhook:

### Node.js

```javascript
// Using crypto-js dependency
const HMACSHA256 = require("crypto-js/hmac-sha256");
const BASE64 = require("crypto-js/enc-base64");
const calculatedHmac = BASE64.stringify(
  HMACSHA256("JSON-BODY-HERE", "YOUR-CLIENT-SECRET-HERE"),
);
console.log(calculatedHmac);
```

### Python

```python
import hmac
import base64
json_body = 'JSON-BODY-HERE'.encode('utf-8')
client_secret = 'YOUR-CLIENT-SECRET-HERE'.encode('utf-8')
calculated_hmac = base64.b64encode(
   hmac.new(client_secret, json_body, 'sha256').digest()
).decode('utf-8')
print(calculated_hmac)
```

## Apps Webhooks

Apps can also receive webhooks on behalf of their users. When a user authorizes your app, Scalev will send webhook events to the URL you specified in your business Webhooks settings. This allows your app to respond to events related to the user's business activities, such as order creation or updates. To use this feature, you must:

* Enable the Webhooks feature on your business and specify the webhook URL and events you want to receive
* Enable the Webhooks feature in your app settings and specify the events you want to receive
* Ensure your apps' requested events are within the specified events in your business settings
* Your users must authorize your app to receive webhooks on their behalf

Events sent to you on behalf of your users will have the signature calculated using **your business Client Secret**, not the user's Client Secret nor the app's Client Secret. This means:

* You don't need to ask your users for their Client Secret to verify webhook requests. Instead, you can use your own Client Secret to validate the signature.
* If you have multiple apps, you can use the same Client Secret for all of them to verify webhooks. This simplifies the process of handling webhooks across different apps. We add `X-Scalev-App-Id` header to identify which app the webhook is for, so you can handle them accordingly.
* If you also receives webhooks for your own business, you can use the same Client Secret to verify those webhooks as well. This means you don't need to maintain separate secrets for different webhook sources.

## Available Events

Scalev currently supports the following webhook events:

* `order.created`: Triggered when a new order is created.
* `order.epayment_created`: Triggered when the payment of an order using e-payment is successfully created. When this event occurs, customers can actually pay with the various methods provided by the e-payment provider in your account.
* `order.updated`: Triggered when an existing order is updated.
* `order.deleted`: Triggered when an order is deleted.
* `order.status_changed`: Triggered when the status of an order changes.
* `order.payment_status_changed`: Triggered when the payment status of an order changes.
* `order.spam_created`: Triggered when a spam order is created.

<br />

## Payload Structure

All events in Scalev will have the following structure:

| Field       | Description                                                     |
| ----------- | --------------------------------------------------------------- |
| `event`     | Event name, for example: `order.created`, `order.deleted`, etc. |
| `unique_id` | ID of the corresponding webhook event.                          |
| `timestamp` | Timestamp of the corresponding webhook event (ISO 8601 format). |
| `data`      | The actual webhook event data.                                  |

For example:

```json
{
  "event": "order.spam_created",
  "unique_id": "event_I7fkiBF4YksYDsKbVe5ZOEyZ",
  "timestamp": "2025-01-29T20:28:25.046183Z",
  "data": {
    "order_id": "250130JQHFZG",
    "secret_slug": "WjCc_Jk-EK2F8xLCseNKfjFIaESbm9-W2RZvRaas",
    "status": "pending",
    "is_probably_spam": true,
    "mark_as_spam_by": "ai",
    "draft_time": "2025-01-29T20:28:08Z",
    "pending_time": "2025-01-29T20:28:08Z",
    "confirmed_time": null,
    "in_process_time": null,
    "ready_time": null,
    "shipped_time": null,
    "completed_time": null,
    "rts_time": null,
    "canceled_time": null,
    "closed_time": null,
    "payment_status": "unpaid",
    "unpaid_time": "2025-01-29T20:28:08Z",
    "paid_time": null,
    "conflict_time": null,
    "settled_time": null,
    "business": {
      "username": "username",
      "client_id": "41750fd8-e7e2-4887-b348-04c01a547ae0"
    },
    "store": {
      "name": "Example Store"
    },
    "epayment_provider": null,
    "payment_method": "bank_transfer",
    "sub_payment_method": null,
    "financial_entity": {
      "code": "bni",
      "name": "Bank Negara Indonesia"
    },
    "payment_account_holder": "Unreal Person",
    "payment_account_number": "1234567812345678",
    "transferproof_url": "https://cdn.scalev.id/Image/dGONXQPPK_hDCrEL3lfEnOQoPOBwuRUZUUyjxreQCzQ/1738182480347-milkbox.webp",
    "transfer_time": null,
    "final_variants": {
      "Amazing Product": 1
    },
    "total_quantity": 1,
    "gross_revenue": "168724.00",
    "unique_code_discount": "276.00",
    "discount_code_discount": "0.00",
    "net_revenue": "149724.00",
    "product_price": "150000.00",
    "product_discount": "0.00",
    "other_income_name": "Biaya Lainnya",
    "other_income": "0.00",
    "discount_rate": "0.00",
    "cogs": "45095.00",
    "shipping_cost": "19000.00",
    "shipping_discount": "0.00",
    "payment_fee": "0.00",
    "customer_id": 28024,
    "destination_address": {
      "name": "Example Person",
      "phone": "628112345678",
      "email": "testing@example.com",
      "address": "This is not a real address.",
      "subdistrict": "Gayungan",
      "city": "Kota Surabaya",
      "province": "Jawa Timur",
      "postal_code": null,
      "notes": ""
    },
    "origin_address": {
      "address": "This is not a real address.",
      "subdistrict": "Gunung Jati (Cirebon Utara)",
      "city": "Kabupaten Cirebon",
      "province": "Jawa Barat",
      "postal_code": "45151"
    },
    "warehouse": {
      "name": "Example Warehouse",
      "unique_id": "warehouse_FN9odhpi1VOF7FLxMhtiWdJo"
    },
    "product_weight": 500,
    "weight_bump": 0,
    "total_weight": 500,
    "courier_service": {
      "courier": {
        "name": "Ninja Xpress",
        "code": "ninja"
      },
      "name": "Standard",
      "code": "STANDARD"
    },
    "courier_aggregator_code": null,
    "rtsproof_url": null,
    "shipment_receipt": null,
    "shipment_status": null,
    "awb_status": "unavailable",
    "awb_ca_status": "unavailable",
    "notes": "Example notes.",
    "tags": [],
    "orderlines": [
      {
        "quantity": 1,
        "is_inventory": false,
        "weight": 500,
        "product_name": "Amazing Product",
        "variant_unique_id": "variant_Wifko5BIJbnQoo9LPAiJ63Kv",
        "variant_sku": "BCF009",
        "variant_price": "150000.00",
        "variant_cogs": "45095.00",
        "product_price": "150000.00",
        "discount": "0.00",
        "discount_code_discount": "0.00",
        "cogs": "45095.00"
      }
    ],
    "created_at": "2025-01-29T20:28:08Z",
    "last_updated_at": "2025-01-29T20:28:08Z"
  }
}
```