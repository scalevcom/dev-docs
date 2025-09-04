---
title: Membuat Order
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

* Gunakan endpoint **[list store simplified](https://developers.scalev.id/reference/scalevapiwebstorecontrollerindex_simplified)**.
* Opsi filter:

  * `search`: cari nama toko.
  * `domain`: cari domain spesifik.
* Response dari endpoint ini juga memuat **payment methods** dan **sub-payment methods** (misal Virtual Account/VA) yang tersedia.

### 2. Pilih produk / bundle

* Gunakan:

  * **[list products from store](https://developers.scalev.id/reference/scalevapiwebstorecontrollerindex_product)** → untuk produk individual.
  * **[list bundles from store](https://developers.scalev.id/reference/scalevapiwebstorecontrollerindex_bundle)** → untuk paket produk.

### 3. Buat payload order

Untuk digital product order yang langsung membuat payment request dengan order status `pending`, cukup field minimal berikut:

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

Atau kalau ingin menggunakan bundle alih-alih produk:

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
  "payment_method": "invoice"
}
```

### 4. Kirim request

* Hit endpoint **[create order](https://developers.scalev.id/reference/scalevapiwebordercontrollercreate)** dengan payload di atas.

### 5. Dapatkan link pembayaran

* Response akan memuat `secret_slug`.
* Gunakan untuk membuat URL instruksi pembayaran:

```
https://app.scalev.id/order/public/<secret_slug>/success
```

Customer bisa diarahkan langsung ke link ini.

***

## 🔹 Physical Products Orders

### 1–2. Sama seperti order digital

### 3. Tambahkan data pengiriman

Field tambahan yang dibutuhkan:

* `address`
* `location_id`
* `warehouse_unique_id`
* `shipping_cost`
* `courier_service_id`
* Opsional: `postal_code`
* Opsional: `shipment_provider_code`

**Cara mendapatkannya:**

* **`address`** → isi teks alamat **tanpa kecamatan, kota, provinsi** (karena diwakili oleh `location_id`).
* **`location_id`** → cari kecamatan via endpoint **[list location](https://developers.scalev.id/reference/scalevapiweblocationcontrollerindex_locations)** (query mendukung partial match).
* **`postal_code`** → isi teks kode pos alamatnya jika ingin lebih spesifik.
* **`warehouse_unique_id`**, **`shipping_cost`**, **`courier_service_id`**, **`shipment_provider_code`** → dari endpoint **[search warehouse](https://developers.scalev.id/reference/scalevapiwebshippingcostcontrollersearch_warehouses)**, lalu lanjut ke **[search courier service](https://developers.scalev.id/reference/scalevapiwebshippingcostcontrollersearch_courier_services)**.

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
  "address": "Jl. Pegangsaan Timur No. 28",
  "location_id": 1,
  "postal_code": "12345",
  "warehouse_unique_id": "warehouse_xxx",
  "courier_service_id": 1,
  "shipping_cost": 20000,
  "shipment_provider_code": "lincah"
}
```

### 5. Kirim request

* Hit endpoint **[create order](https://developers.scalev.id/reference/scalevapiwebordercontrollercreate)** dengan payload di atas.

### 6. Dapatkan link pembayaran

* Sama seperti order digital:

```
https://app.scalev.id/order/public/<secret_slug>/success
```

<br />