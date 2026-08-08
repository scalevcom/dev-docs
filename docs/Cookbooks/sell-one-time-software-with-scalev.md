---
title: "Sell one-time software with Scalev"
excerpt: "Use Scalev for checkout and payment while your app provisions permanent access after a verified webhook."
deprecated: false
hidden: false
metadata:
  robots: index
---
Use this cookbook when your web app is already running and you want Scalev to sell permanent, one-time access to it. Scalev hosts the sales and checkout flow, collects the payment, and notifies your app. Your app remains responsible for accounts, entitlements, login, and access control.

This flow is for a one-time purchase. It does not create a recurring SaaS subscription.

## What you will build

The buyer journey is:

1. An ad or campaign sends the buyer to a Scalev Sales Page.
2. The Sales Page sends the buyer to a Scalev Checkout Page.
3. The buyer submits the checkout form and opens the PayLink page.
4. The buyer chooses an available payment method and pays.
5. Scalev sends signed webhook events to your app.
6. Your app provisions permanent access and sends a one-time set-password email.
7. Scalev's paid-order page redirects the buyer to your app's success page.
8. The buyer opens the email, sets a password, and can then use your app normally.

The webhook is the source of truth for provisioning. A browser redirect is only navigation and must never grant access.

## Before you start

You need:

- A Scalev account and business.
- A Scalev subscription plan supporting webhooks, currently Basic or above. See [Enable webhooks](/docs/enabling-webhooks).
- A payment gateway that has completed its required verification.
- An HTTPS webhook endpoint in your app.
- Durable storage for webhook events, purchases, entitlements, and email jobs.
- A public HTTPS success page in your app, for example `https://app.example.com/payment/success`.

Configure SingaPay or DurianPay under **Settings > Integrations**, then enable the supported methods under **Settings > Payment Methods**. If Xendit is available for your business, configure and verify it through the corresponding payment settings.

Payment methods shown to a buyer depend on both the methods enabled for the business and the methods selected for the store. Test the final checkout instead of assuming that a configured gateway makes every method available.

## 1. Create the product

In Scalev, create a product for the software access you are selling.

Use these settings for a straightforward one-time offer:

- Set the product type to **Digital**.
- Use **Satu Varian** when you sell one access tier.
- Set access to **Permanent**.
- Set the one-time price.
- Disable Scalev file, link, and LMS delivery when access lives entirely in your external app.
- Add the product to the store used by the campaign and checkout.
- Keep the checkout quantity at `1` unless buying multiple seats is an intentional feature.

Record the variant's `variant_unique_id`. Your app will map this stable value to an internal entitlement or plan. Do not map access by the product's display name because merchants can rename it.

The **Permanent** setting describes the Scalev product. Your app must still create and enforce its own permanent entitlement.

### Find the variant unique ID in the dashboard

Open the product in Scalev. Where the id sits depends on how many variants the product has:

- **Satu Varian**: the **Informasi Detil** header shows `Unique ID: variant_...` with a **Salin** button beside it.
- Several variants: open the row menu in **Daftar Varian** and choose **Copy Unique ID**. The same id also appears under the title in **Edit Varian**.

A variant only has an id once it is saved, so save a new variant before you look for it.

### Find the variant unique ID through the API

List the products attached to the store and read `unique_id` from each variant. Get `{store_id}` from `GET /v3/stores/simplified`.

```bash
curl "https://api.scalev.com/v3/stores/{store_id}/products" \
  -H "Authorization: Bearer $SCALEV_API_KEY"
```

Each product carries its variants inline:

```json
{
  "data": [
    {
      "id": 1,
      "name": "Software access",
      "is_visible": true,
      "variants": [
        {
          "id": 456,
          "unique_id": "variant_qnUEhjhOSjcUda8xpktbiH1F",
          "fullname": "Permanent",
          "sku": null,
          "price": 200000
        }
      ]
    }
  ],
  "is_paginated": true,
  "has_next": false
}
```

When you already know the numeric variant `id`, read the full record instead:

```bash
curl "https://api.scalev.com/v3/stores/{store_id}/variants/{variant_id}" \
  -H "Authorization: Bearer $SCALEV_API_KEY"
```

Both are authenticated business endpoints. They accept a business API key or an OAuth access token, and the OAuth scopes are `product:list` for the product list and `product:read` for the single variant. Do not call them from browser JavaScript.

`unique_id` is the same value that arrives as `variant_unique_id` in `order.created` order lines, so store it as the join key between a Scalev variant and your internal plan.

## 2. Configure the store and PayLink

Open the intended store and confirm that the new product is included.

In the store's **Payment Methods** settings:

1. Add **PayLink** (`payment_link`) to the selected payment methods.
2. Select the concrete methods buyers may use, such as QRIS, virtual accounts, and e-wallets. PayLink offers the store methods that the business has also enabled and that a PayLink-capable gateway supports, so a method missing on either side never reaches the buyer. When the store selects no PayLink-capable method at all, PayLink falls back to every eligible business method.
3. Open **Pengaturan PayLink** to launch **PayLink Studio** when you want to change how the page looks: default language, the buyer-facing language switcher, primary color, favicon, and the metadata shown when the link is shared. PayLink Studio controls appearance and metadata only. It does not select payment methods.
4. Save, then open a real checkout preview and confirm the final methods shown.

Use **PayLink**, not the deprecated all-in-one **ALL E-Payment** (`invoice`) option, for this flow. PayLink lets the buyer choose from the store's currently eligible gateway methods on a dedicated payment page.

## 3. Build the Sales Page

Create a Sales Page for the first visit from ads or campaigns. Explain the offer, one-time price, included access, device or seat limits, refund policy, and support terms.

Set the primary call to action to **Other Pages**, then select the Checkout Page you create in the next step. Preserve campaign parameters when you intentionally need them for attribution.

## 4. Build the Checkout Page

Create a Checkout Page for the same store and product.

Configure the form as follows:

- Show the email field and make it required.
- Use a label such as **Email for your app login**.
- Explain that Scalev sends the purchase to the email entered here and that the buyer must be able to open it.
- Keep the product quantity at `1` for a single-license purchase.
- Confirm that the form uses the intended store and variant.
- Turn on **Aktifkan PayLink** so the buyer lands on the PayLink page after submitting the form.

**Aktifkan PayLink** replaces the form's own payment selector: every order the form creates uses `payment_link`, and the buyer picks the concrete method on the PayLink page instead. Scalev rejects the toggle when the store and business leave no executable PayLink method, so finish step 2 first.

Enable **Redirect to a custom URL after payment**, then set **Post-payment redirect URL** to your app's HTTPS success page, such as:

```text
https://app.example.com/payment/success
```

The toggle is explicit: when it is off, Scalev keeps its default paid-order success flow even if an old URL is still saved. When it is on, a valid URL is required. Scalev snapshots that decision onto each new public order, so later page edits do not change an existing buyer's destination.

For an API-created order, you can override this page default without exposing another dashboard or buyer-facing form control. Omit `is_post_payment_redirect_enabled` and `post_payment_redirect_url` to inherit the page. Send the flag as `false` to use Scalev's hosted flow for that order, or send it as `true` with an absolute HTTPS URL to use an order-specific destination. The override is accepted only during order creation.

This setting applies to every payment method on the checkout page. It controls where Scalev sends the buyer after it has observed a `paid` or `settled` payment. It is separate from **After Submit**, which controls the first redirect immediately after the checkout form creates an order.

For a PayLink order, the normal initial destination is still Scalev's hosted payment page. After payment, that page waits briefly and then uses the configured post-payment URL. Other hosted order and payment-success pages apply the same order-level redirect after they observe payment. If the toggle is off, the snapshot is absent, or the URL is rejected, Scalev keeps its hosted success flow.

Do not put secrets, raw order identifiers, access tokens, or credentials in the success URL. Scalev preserves the URL's configured query string and fragment but does not append buyer or order data.

Your app's success page should use neutral copy because the webhook worker and email delivery may complete at slightly different times. For example:

> Payment received. Check your email for the secure link to set your password and access your account. It may take a few minutes to arrive.

Do not provision access from a request to this page. Buyers, crawlers, and attackers can open it directly.

## 5. Enable the webhook events

Go to **Settings > Developers > Webhooks** and register your app's HTTPS endpoint.

Select these events:

- `order.created`: Save the order, buyer email, and purchased `variant_unique_id` values.
- `payment.received`: Mark the purchase as paid and provision access.

You can also select `payment.failed` if you want to record payment conflicts or alert support.

Do not use `order.status_changed` with `status == "confirmed"` as the payment signal. Order workflow status and payment status are separate. `payment.received` is the stable payment event and is sent when payment status becomes `paid` or `settled`.

Both recommended events identify the order with `data.id`:

- `order.created` includes `data.customer.email`, `data.destination_address.email`, and `data.orderlines` with each `variant_unique_id` and `variant_sku`.
- `payment.received` uses the payment-status payload. It includes the order and customer identity but does not include `orderlines`.

Persist the `order.created` snapshot so a later `payment.received` event can resolve the purchased variant. Design for duplicate delivery and for events to arrive later or in an unexpected order. A payment may produce `payment.received` once at `paid` and again at `settled`.

See [Webhook events](/docs/webhook-events), [Payload example](/docs/payload-example), and [Verifying a webhook request](/docs/verifying-a-webhook-request) for the complete contract.

## 6. Verify and store webhook requests

Scalev signs the exact request body with HMAC-SHA256 and sends the Base64 signature in `X-Scalev-Hmac-Sha256`. Verify the raw bytes before parsing JSON.

The following Express example verifies the signature, writes the event to a durable inbox, and only then acknowledges it. Implement `webhookInbox.insert` with your database and add a unique constraint on `event_unique_id`.

```js
import crypto from "node:crypto";
import express from "express";

const app = express();
const signingSecret = process.env.SCALEV_WEBHOOK_SIGNING_SECRET;

function validScalevSignature(rawBody, receivedSignature) {
  if (!signingSecret || !receivedSignature) return false;

  const expected = crypto
    .createHmac("sha256", signingSecret)
    .update(rawBody)
    .digest();

  let received;
  try {
    received = Buffer.from(receivedSignature, "base64");
  } catch {
    return false;
  }

  return (
    received.length === expected.length &&
    crypto.timingSafeEqual(received, expected)
  );
}

app.post(
  "/webhooks/scalev",
  express.raw({ type: "application/json", limit: "1mb" }),
  async (req, res) => {
    const rawBody = req.body;
    const signature = req.get("X-Scalev-Hmac-Sha256");

    if (!Buffer.isBuffer(rawBody) || !validScalevSignature(rawBody, signature)) {
      return res.sendStatus(401);
    }

    let event;
    try {
      event = JSON.parse(rawBody.toString("utf8"));
    } catch {
      return res.sendStatus(400);
    }

    if (!event.unique_id || !event.event || !event.data?.id) {
      return res.sendStatus(400);
    }

    try {
      await webhookInbox.insert({
        event_unique_id: event.unique_id,
        event_name: event.event,
        scalev_order_id: event.data.id,
        payload: event,
        received_at: new Date()
      });
    } catch (error) {
      if (isDuplicateKey(error, "event_unique_id")) {
        return res.sendStatus(204);
      }

      return res.sendStatus(503);
    }

    return res.sendStatus(204);
  }
);

// Register normal JSON middleware after the raw-body webhook route.
app.use(express.json());
```

Any `2xx` response acknowledges delivery. Scalev retries failed deliveries, so returning success before durable storage can lose provisioning work.

## 7. Process events asynchronously

Use a background worker to process inbox records. Keep the HTTP handler fast.

At minimum, store these records:

| Record | Required uniqueness | Purpose |
| --- | --- | --- |
| Webhook inbox | `event_unique_id` | Deduplicate delivery and retain the original event. |
| Scalev purchase | `scalev_order_id` | Join `order.created` and `payment.received`. |
| Entitlement | `(scalev_order_id, variant_unique_id)` | Prevent duplicate provisioning for paid and settled events. |
| Email outbox | Your idempotency key | Send the access email reliably after the database commit. |

Process `order.created` by upserting a purchase snapshot with:

- `data.id` as `scalev_order_id`.
- The normalized buyer email.
- Each `data.orderlines[].variant_unique_id`.
- The original event ID and payload for audit and replay.

Process `payment.received` only when `data.payment_status` is `paid` or `settled`. Mark the purchase paid and create entitlements inside one database transaction. If the order snapshot is not available yet, leave the event pending and retry it instead of guessing which product was bought.

For each order line:

1. Look up the internal access plan by `variant_unique_id`.
2. Quarantine the purchase for manual review if the mapping is unknown.
3. Quarantine it if no usable buyer email exists.
4. Upsert the app user by normalized email.
5. Insert the permanent entitlement with a unique `(scalev_order_id, variant_unique_id)` key.
6. Write an email job to the outbox in the same transaction.

Do not replace an existing user's password. Grant the entitlement to that account and send a sign-in or access-confirmation email instead.

For a new user, create a pending account and email a single-use set-password link. Store only a hash of the token, expire it after a short period such as 60 minutes, and mark it used after the password is set. This is safer than emailing a generated password.

## 8. Test the complete journey

Test with a non-production business and gateway before launching a campaign.

Verify all of the following:

- The Sales Page CTA opens the intended Checkout Page.
- The checkout requires an email and creates an order for the expected variant.
- PayLink shows only eligible store payment methods.
- A successful payment creates both `order.created` and `payment.received` inbox records.
- Replaying either event does not create another user, entitlement, or email.
- A `paid` event followed by a `settled` event still creates one entitlement.
- Your worker safely waits when payment arrives before the order snapshot.
- Unknown variants and missing emails enter manual review without granting access.
- Existing users keep their current password and gain the new entitlement.
- New users receive one single-use set-password email.
- Every tested paid method redirects to the configured app success page.
- Opening the success page directly does not provision access.
- Turning off the custom post-payment redirect keeps Scalev's hosted success flow, even when a URL remains saved.

## Responsibility boundary

| Scalev | Your app |
| --- | --- |
| Sales Page and Checkout Page | User accounts and authentication |
| Store and product selection | Variant-to-plan mapping |
| PayLink and gateway payment | Permanent entitlements and authorization |
| Signed order and payment webhooks | Idempotent webhook inbox and worker |
| Paid-order browser redirect | Set-password tokens and email delivery |

This boundary keeps payment verification server-to-server. The buyer can close the browser after paying and still receive access when your webhook worker completes.
