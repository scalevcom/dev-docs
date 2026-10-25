---
title: "Fast mode"
excerpt: "Enable Fast mode for a Builder landing page and preview changes in Studio."
deprecated: false
hidden: false
metadata:
  robots: index
---
**Fast mode (Beta)** is an optional setting for Builder landing pages. It serves a prepared HTML page while keeping the same Builder editor, content, and checkout configuration. New pages use the standard view until you enable Fast mode.

Fast mode does not convert your page to [HTML Mode](/docs/create-landing-page-html-mode). Your saved Builder content stays editable, and changing the delivery setting does not add a content version. Authored HTML Mode pages, storefronts, and dedicated checkout, offer, payment, and thank-you pages keep their existing rendering.

## Enable Fast mode

Open your Builder page in Studio, select **Settings**, and find **Fast mode (Beta)**.

- **New page:** Choose **Enable** before saving. Your choice is saved with the page; Fast mode is prepared when you publish it. A draft shows **Ready on publication**.
- **Existing published page:** Choose **Enable**. The activation window shows preparation progress and checks the published page link.
- **Existing unpublished page:** Publish it before enabling Fast mode. If you previously enabled Fast mode, the preference is retained for the next publication.

The preference applies to that page only. Other pages keep their current setting.

## Preview changes in Studio

When Fast mode is enabled, the Studio preview updates from your unsaved edits. It does not publish each change or change what visitors see.

Use the device controls to inspect these widths:

| Preview | Width |
| --- | --- |
| Mobile | 390 px |
| Tablet | 768 px |
| Desktop | 1280 px |
| Wide desktop | 1440 px |

The preview scales to fit the editor pane and scrolls within it. Your page's responsive styles and configured container still determine its layout. Changing the preview width does not change the published page's width.

The preview preserves supported form inputs, selections, open sections, focus, and scroll while you edit. If a change cannot be displayed, Studio keeps the last successful preview and shows a warning. Correct the component settings and try again.

The Fast mode preview does not run your custom JavaScript, create orders, request live checkout quotes, send tracking events, or save visitor prefill. External media may not behave exactly as it does on the public page. Use the published page to verify those behaviors. Authored HTML Mode has its own preview, which simulates runtime methods; it does not create real orders either.

## Save and publish

Saving a draft leaves the published page unchanged. Publishing prepares Fast mode for the newly published content. If that preparation fails, Scalev uses the current standard view instead of substituting an older Fast mode version.

The publication window shows preparation and page-link checks. You can close it while work continues. If the check takes longer than expected or the status cannot be loaded, choose **Check again** or reopen page settings. Saving or publishing content is separate from confirming that Fast mode is ready.

If you publish again or change the setting while preparation is running, check the status of the latest publication. After completion, open the normal public URL and reload any already open tab to verify your changes. A completed readiness check does not guarantee that every cached copy worldwide refreshed at the same instant.

The public page is a real checkout. Submitting it can create orders and trigger inventory changes, notifications, tracking, or payment flows. Studio preview does not verify those outcomes.

## Understand the status

| Status | Meaning |
| --- | --- |
| Off | The page uses the standard view. |
| Ready on publication | Your choice is saved; Fast mode will be prepared when you publish. |
| Preparing | Scalev is preparing the published page. The current standard view remains available during preparation. |
| Active | Fast mode is prepared for the current published page. Use the activation or publication window to confirm its page-link check has completed. |
| Using standard view | Fast mode is enabled but unavailable for this publication. Your preference is saved, and visitors receive the current standard view. |
| Updating page | The latest delivery change is still being made available to visitors. |

A fallback preserves the current page's publication and visibility rules; it cannot make an unpublished or restricted page public.

## Retry or disable Fast mode

If settings show **Using standard view**, read the message and check any **Affected component**. Correct unsupported or overly complex content, publish content changes when needed, and choose **Try again**. Share the **Support code** with support if the problem continues.

Choose **Disable** to return to the standard view. This keeps your page content and published version, and you can enable Fast mode again later. Delivery changes can take time to reach cached pages.

## Shared updates and troubleshooting

Fast mode automatically attaches the shared page interactions, including forms and the checkout loading overlay. You do not need to add a loading script to each page. Compatible updates to shared behavior apply to existing and new Fast mode pages when their public documents refresh; they do not require you to republish. Changes to the prepared page layout may require Scalev to rebuild it, which does not add a content version to your page history.

To report a difference, compare the same published content and visitor state at the same viewport width. Check images, fonts, buttons, galleries, folding, product choices, form fields, and the checkout destination. Include the public URL, viewport, steps, visible result, and support code when available. Do not share customer details or credentials.

For public JavaScript methods and checkout error handling, see the [HTML Mode runtime](/docs/html-mode-runtime).
