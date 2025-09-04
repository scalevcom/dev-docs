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

<br />

## 🔹 Physical Product Orders

### 1–2. Same as digital orders

### 3. Add shipping information

Required additional fields:

* `address`
* `location_id`
* `warehouse_unique_id`
* `shipping_cost`
* `courier_service_id`
* Optional: `postal_code`
* Optional: `shipment_provider_code`

**How to obtain them:**

* **`address`** → provide the street address text **without district, city, or province**, since these are represented by `location_id`.
* **`location_id`** → search district (kecamatan) using **list location** endpoint (supports partial matches).
* **`postal_code`** → provide postal code to make the address more specific.
* **`warehouse_unique_id`**, **`shipping_cost`**, **`courier_service_id`**, **`shipment_provider_code`** → first call **search warehouse**, then **search courier service**.

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

* Call the **create order** endpoint with the payload above.

### 6. Get the payment link

* Same as digital orders:

```
https://app.scalev.id/order/public/<secret_slug>/success
```

<br />
