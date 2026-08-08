---
title: "Creating Orders"
excerpt: "Create digital or physical product orders with Scalev API v3."
deprecated: false
hidden: false
metadata:
  robots: index
---
## Digital Product Orders

### 1. Select a store

Use `GET /v3/stores/simplified`.

Runtime currently supports these filters:

- `search`: filter by store name
- `domain`: filter by store domain

The response also includes:

- `payment_methods`

`payment_methods` contains the canonical values accepted by order APIs. Virtual
accounts use flat codes such as `va_bca`, `va_bni`, and `va_bri`.

If you want a dedicated payment-method lookup for a specific store, use:

- `GET /v3/stores/{store_id}/payment-methods`

### 2. Select products or bundles

Use:

- `GET /v3/stores/{store_id}/products` to retrieve individual products
- `GET /v3/stores/{store_id}/bundles` to retrieve bundles

### 3. Build the order payload

For digital product orders, the minimal payload is:

```json
{
  "store_unique_id": "store_xxx",
  "customer_name": "John Doe",
  "customer_phone": "62812345678",
  "customer_email": "example@example.com",
  "ordervariants": [
    {
      "quantity": 1,
      "variant_unique_id": "variant_xxx"
    }
  ],
  "payment_method": "payment_link"
}
```

Or if you want to use bundles instead of products:

```json
{
  "store_unique_id": "store_xxx",
  "customer_name": "John Doe",
  "customer_phone": "62812345678",
  "customer_email": "example@example.com",
  "orderbundles": [
    {
      "quantity": 1,
      "bundle_price_option_unique_id": "bpo_xxx"
    }
  ],
  "payment_method": "payment_link"
}
```

### 4. Send the request

Call `POST /v3/orders` with the payload above.

### 5. Redirect the customer to the payment page

The response includes:

- `id` - the canonical UUIDv7 order primary key
- `order_id` - the business-facing order number
- `secret_slug`
- `public_order_url`
- `payment_url`

Use `id` for later business API calls such as `GET /v3/orders/{id}` or `PATCH /v3/orders/{id}`. Legacy numeric order IDs for migrated orders are still accepted on ID routes, but new order responses return UUIDs.

Use `payment_url` for the customer redirect.

When `payment_method` is `payment_link`, the customer selects the final payment
method on Scalev's PayLink page. The order keeps its PayLink
origin while the paid order exposes the canonical method that was actually
used.

***

## Physical Product Orders

### 1–2. Same as digital orders

### 3. Add shipping information

Required additional fields:

- `address`
- `location_id`
- `warehouse_unique_id`
- `shipping_cost`
- `courier_service_id`

Optional fields:

- `postal_code`
- `shipment_provider_code`

How to obtain them:

- `address` -> provide the street address only, without district/city/province details
- `location_id` -> search district using `GET /v3/locations`
- `postal_code` -> if needed, use `GET /v3/locations/{location_id}/postal-codes` or provide the known postal code directly
- `warehouse_unique_id` -> use `POST /v3/shipping-costs/search-warehouse`
- `courier_service_id`, `shipping_cost`, `shipment_provider_code` -> use `POST /v3/shipping-costs/search-courier-service`

### 4. Build the order payload

Minimal example:

```json
{
  "store_unique_id": "store_xxx",
  "customer_name": "John Doe",
  "customer_phone": "62812345678",
  "customer_email": "example@example.com",
  "ordervariants": [
    {
      "quantity": 1,
      "variant_unique_id": "variant_xxx"
    }
  ],
  "payment_method": "payment_link",
  "address": "Jl. Pegangsaan Timur No. 28",
  "location_id": 1,
  "postal_code": "12345",
  "warehouse_unique_id": "warehouse_xxx",
  "courier_service_id": 1,
  "shipping_cost": 20000,
  "shipment_provider_code": "lincah"
}
```

### 5. Send the request

Call `POST /v3/orders` with the payload above.

### 6. Redirect the customer to the payment page

Use `id` for later business API calls such as `GET /v3/orders/{id}` or `PATCH /v3/orders/{id}`. Legacy numeric order IDs for migrated orders are still accepted on ID routes, but new order responses return UUIDs.

Use `payment_url` from the order-create response.
