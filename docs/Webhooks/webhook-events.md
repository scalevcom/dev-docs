---
title: "Webhook Events"
excerpt: "Review the webhook event types currently sent by Scalev."
deprecated: false
hidden: false
metadata:
  robots: index
---
Scalev currently supports the following webhook events:

* `order.created`: Triggered when a new order is created.
* `order.epayment_created`: Triggered when the payment of an order using e-payment is successfully created. When this event occurs, customers can actually pay with the various methods provided by the e-payment provider in your account.
* `order.updated`: Triggered when an existing order is updated.
* `order.deleted`: Triggered when an order is deleted.
* `order.status_changed`: Triggered when the status of an order changes.
* `order.payment_status_changed`: Triggered when the payment status of an order changes.
* `order.spam_created`: Triggered when a spam order is created.
* `payment.received`: Triggered when an order's payment status becomes `paid` or `settled`. Use this stable event for payment-driven fulfillment.
* `payment.failed`: Triggered when an order's payment status becomes `conflict`.
* `checkout_intent.abandoned`: An unfinished contactable checkout intent has been idle for at least 15 minutes.
* `checkout_intent.completed`: A contactable checkout intent is linked to a successfully created order.

`payment.received` and `payment.failed` use the same `data` shape as
`order.payment_status_changed`. The payment payload identifies the order and
customer but does not include `orderlines`. Subscribe to `order.created` as well
when fulfillment depends on purchased variants.

Webhook delivery is at least once. Store `unique_id` with a unique constraint and
make event processing idempotent. A payment can produce separate
`payment.received` events at `paid` and `settled`; use your fulfillment key to
prevent duplicate delivery.

Order webhook payloads use one canonical `payment_method`; virtual accounts use
flat values such as `va_bca`. `payment_link_id` and `is_from_payment_link`
preserve PayLink origin after a paid order reports the concrete method
that the buyer used.

## Checkout intent events

Checkout intent events are sent only for intents with a valid normalized email or phone and an eligible active business subscription. See [checkout intents](/docs/checkout-intents) for browser capture, merchant reads, and recovery links.

`checkout_intent.abandoned` is emitted at most once per intent when it first qualifies for abandonment. Delivery may occur after the 15-minute threshold. Resuming makes the current intent active again; another idle period does not emit a second abandoned event. An intent completed before abandonment is processed does not emit an abandoned event.

`checkout_intent.completed` is emitted when successful order creation completes the intent, including contact details captured from that order. It does not indicate successful payment. An intent can complete without a prior abandoned event.

Both events use the merchant checkout-intent detail data shape plus `last_sequence` and `occurred_at`. These fields identify the captured snapshot version and event occurrence time. Contact fields are under `customer`; safe form fields, item snapshots, and campaign attribution are included. Storefront intents have `page: null`. The completed event has the linked `order`. The abandoned event can include `recovery_url` and `recovery_url_expires_at`; both are null for completed intents or a missing or untrusted source URL. A recovery URL contains a private `cip_` prefill capability valid for 30 days from issuance. The `cit_` write capability is never included.

For example, an abandoned intent can have this payload:

```json
{
  "event": "checkout_intent.abandoned",
  "unique_id": "event_EXAMPLE_UNIQUE_ID",
  "timestamp": "2026-09-16T01:15:00Z",
  "data": {
    "id": "019c9db5-0fcb-7df3-8c6b-1827b568a61c",
    "form_widget_id": "storefront-checkout",
    "status": "abandoned",
    "last_sequence": 1,
    "occurred_at": "2026-09-16T01:15:00Z",
    "contactable": true,
    "is_email_follow_up_already_sended": false,
    "customer": { "name": "Budi Santoso", "email": "budi@example.com", "phone": null },
    "store": { "id": "store_example", "unique_id": "store_example", "name": "Example store" },
    "page": null,
    "cart_summary": { "item_quantity": 2, "estimated_total": "200000", "currency": "IDR" },
    "handler": null,
    "source_url": "https://shop.example/checkout",
    "started_at": "2026-09-16T01:00:00Z",
    "last_activity_at": "2026-09-16T01:00:00Z",
    "follow_up_eligible_at": "2026-09-16T01:15:00Z",
    "completed_at": null,
    "order": null,
    "fields": { "shipping_address": "Jl. Merdeka No. 1" },
    "items": [{ "type": "variant", "variant_id": 101, "quantity": 2, "name": "Example item", "unit_price": "100000", "line_total": "200000", "currency": "IDR" }],
    "attribution": { "utm_source": "newsletter" },
    "recovery_url": "https://shop.example/checkout?checkout_intent_prefill_token=cip_...",
    "recovery_url_expires_at": "2026-10-16T01:15:00Z"
  }
}
```

### Delivery and current state

Checkout lifecycle events are saved with the state change and delivered through Scalev's durable webhook delivery flow. Eligible business endpoints and authorized app recipients receive the captured lifecycle data. Business delivery and each app's delivery can have distinct event IDs. A retry of the same event preserves its `unique_id` and snapshot rather than rebuilding it from the buyer's newer input.

Delivery is at least once and order is not guaranteed. A delayed abandoned event may arrive after the buyer resumes or completes checkout. Deduplicate by `unique_id`, then use the merchant detail endpoint before taking an action that depends on current status. Verify the signature over raw bytes and durably accept the event before returning a `2xx` response. See [webhook verification](/docs/verifying-a-webhook-request).

<br />

## Payload structure

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
    "id": "01948092-9b80-7f91-b23d-1a8686278331",
    "payment_link_id": null,
    "is_from_payment_link": false,
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
    "payment_link_income": "0.00",
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
