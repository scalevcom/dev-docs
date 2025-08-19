---
title: Apps Webhooks
excerpt: This document explains how webhooks feature behave for apps.
deprecated: false
hidden: false
metadata:
  robots: index
---
Apps can also receive webhooks on behalf of their users. When a user authorizes your app, Scalev will send webhook events to the URL you specified in your business Webhooks settings. This allows your app to respond to events related to the user's business activities, such as order creation or updates. To use this feature, you must:

* Enable the Webhooks feature on your business and specify the webhook URL and events you want to receive
* Enable the Webhooks feature in your app settings and specify the events you want to receive
* Ensure your apps' requested events are within the specified events in your business settings
* Your users must authorize your app to receive webhooks on their behalf

Events sent to you on behalf of your users will have the signature calculated using **your business Signing Secret**, not the user's Signing Secret nor the app's Client Secret. This means:

* You don't need to ask your users for their Signing Secret to verify webhook requests. Instead, you can use your own Signing Secret to validate the signature.
* If you have multiple apps, you can use the same Signing Secret for all of them to verify webhooks. This simplifies the process of handling webhooks across different apps. We add `X-Scalev-App-Id` header to identify which app the webhook is for, so you can handle them accordingly.
* If you also receive webhooks for your own business, you can use the same Signing Secret to verify those webhooks as well. This means you don't need to maintain separate secrets for different webhook sources.