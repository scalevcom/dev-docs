---
title: Creating Digital & Physical Orders
excerpt: >-
  Scalev API allows both **humans** (via script/application) and **AI agents**
  to create orders. This guide walks you step-by-step through the process.
deprecated: false
hidden: false
metadata:
  robots: index
---
## 🔹 Digital Product Orders

### 1. Select a store

* Use the **list store simplified** endpoint.
* Available filters:

  * `search`: filter by store name.
  * `domain`: filter by store domain.
* The response also includes **payment methods** and **sub-payment methods** (e.g., Virtual Account/VA).

### 2. Select products or bundles

* Use:

  * **list products from store** → to retrieve individual products.
  * **list bundles from store** → to retrieve product bundles.

### 3. Build the order payload

For digital product orders (which immediately create a payment request with `pending` status), the minimal payload is:

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
  "payment_method": "invoice"
}
```

### 4. Send the request

* Call the **create order** endpoint with the payload above.

### 5. Get the payment link

* The response contains a `secret_slug`.
* Use it to construct the payment instruction URL:

```
https://app.scalev.id/order/public/<secret_slug>/success
```

Customers can be redirected to this page.

***

## 🔹 Physical Product Orders

### 1–2. Same as digital orders

* Select store → select products/bundles.

### 3. Retrieve shipping information

Physical product orders require additional fields:

* `warehouse_unique_id`
* `shipping_cost`
* `courier_service_id`
* Optional: `shipment_provider_code`
  (for integrations such as Ninja, Lincah, or Mengantar).

**How to obtain these values**:

1. Call **search warehouse** endpoint.
2. Use the result to call **search courier service**.

   * The response provides the required shipping fields.

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
  "payment_method": "invoice",
  "warehouse_unique_id": "warehouse_xxx",
  "courier_service_id": 1,
  "shipping_cost": 20000,
  "shipment_provider_code": "lincah"
}
```

### 5. Send the request

* Call the **create order** endpoint with the payload above.

### 6. Get the payment link

* The response contains a `secret_slug`.
* Construct the payment instruction URL:

```
https://app.scalev.id/order/public/<secret_slug>/success
```

***

## 🔑 Key Notes

* **Digital product orders** → only need `store_id`, `customer`, `ordervariants`, `payment_method`.
* **Physical product orders** → also require `warehouse`, `courier`, and `shipping_cost`.
* **AI agents** can follow the same flow automatically:

  1. Select store
  2. Select products
  3. Retrieve warehouse & courier (if physical)
  4. Send order payload
  5. Use `secret_slug` for payment link
