---
title: Membuat Order Digital & Fisik
excerpt: >-
  API Scalev memungkinkan order dibuat baik oleh **manusia** (via
  script/aplikasi) maupun **AI agent**. Berikut panduan step-by-step.
deprecated: false
hidden: false
metadata:
  robots: index
---
## 🔹 Digital Product Orders

### 1. Pilih toko (store)

* Gunakan endpoint **list store simplified**.
* Opsi filter:

  * `search`: cari nama toko.
  * `domain`: cari domain spesifik.
* Response dari endpoint ini juga memuat **payment methods** dan **sub-payment methods** (misal Virtual Account/VA) yang tersedia.

### 2. Pilih produk / bundle

* Gunakan:

  * **list products from store** → untuk produk individual.
  * **list bundles from store** → untuk paket produk.

### 3. Buat payload order

Untuk digital product, cukup field minimal berikut:

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

### 4. Kirim request

* Hit endpoint **create order** dengan payload di atas.

### 5. Dapatkan link pembayaran

* Response akan memuat `secret_slug`.
* Gunakan untuk membuat URL instruksi pembayaran:

```
https://app.scalev.id/order/public/<secret_slug>/success
```

Customer bisa diarahkan langsung ke link ini.

***

## 🔹 Physical Product Orders

### 1-2. Sama seperti digital orders

* Pilih store → pilih produk/bundle.

### 3. Cari informasi pengiriman

Untuk order fisik, ada field tambahan:

* `warehouse_unique_id`
* `shipping_cost`
* `courier_service_id`
* Opsional: `shipment_provider_code`
  (untuk plugin Ninja, Lincah, atau Mengantar).

**Cara mendapatkannya**:

1. Hit endpoint **search warehouse**.
2. Gunakan hasilnya untuk hit endpoint **search courier service**.

   * Response berisi keempat nilai di atas.

### 4. Buat payload order

Contoh minimal:

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

### 5. Kirim request

* Hit endpoint **create order** dengan payload di atas.

### 6. Dapatkan link pembayaran

* Sama seperti digital orders, ambil `secret_slug` dari response.
* Arahkan customer ke:

```
https://app.scalev.id/order/public/<secret_slug>/success
```

***

## 🔑 Catatan Penting

* **Digital product** → cukup `store_id`, `customer`, `ordervariants`, `payment_method`.
* **Physical product** → butuh tambahan `warehouse`, `courier`, `shipping_cost`.
* AI agent bisa otomatis mengikuti flow ini:

  1. Pilih store
  2. Pilih produk
  3. Cek warehouse & courier (jika fisik)
  4. Kirim payload
  5. Ambil `secret_slug`

<br />
