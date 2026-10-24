---
title: "Compiled builder delivery"
excerpt: "Preview and test compiled delivery for an individual published builder page."
deprecated: false
hidden: true
metadata:
  robots: noindex
---
This beta is being validated and is not yet available to merchants. When enabled for your account, you can choose **Compiled HTML delivery — Beta** independently for each builder landing page. It starts off.

Your page stays editable in the same builder. This setting does not convert it to authored HTML Mode, change your saved content, or create an additional content version.

## Preview your published page

Open the page settings and choose **Preview published page**. Preview uses the currently published version. Publish any draft changes through the normal publishing flow before previewing them.

Read the confirmation before opening the preview: checkout is real. Orders, payments, inventory, notifications, checkout intents and tracking use their normal behavior. Do not submit a test order on a live store unless you intend those effects.

The preview link expires after one hour and is restricted to that page and host. Publishing a different revision invalidates checkout from the old preview. Open a fresh preview after publishing.

## Enable or disable delivery

Choose **Enable** to prepare compiled delivery. Visitors continue receiving the current standard page while it is being prepared. Once the new document is active and delivery caches have updated, the settings show **Active**.

| Status | Meaning |
| --- | --- |
| Off | The page uses standard delivery. |
| Preparing | The published page is being prepared. Visitors receive standard delivery. |
| Active | The compiled page is active and its requested cache updates have completed. |
| Standard fallback | Your preference remains enabled, but visitors receive standard delivery. Read the failure detail and retry after fixing the issue. |
| Updating delivery | The origin has changed, but delivery cache updates are still pending. |

Choose **Disable** to return to standard delivery. You can enable it again later. Saving a draft does not change published delivery. Publishing new content always serves that current content; the system never substitutes an older compiled version while preparing it.

## Report a difference

Compare the same published page on mobile and desktop. Check images, fonts, buttons, galleries, folding, product choices, form fields and the checkout destination. Record the page URL, viewport, steps and visible result. Copy the diagnostic reference from delivery settings when it is available. Do not share preview credentials or customer details.

A platform repair may update shared browser behavior or rebuild the stored presentation. Neither operation adds a system-generated version to your page history or requires you to edit and republish your content.
