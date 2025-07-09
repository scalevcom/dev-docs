---
title: Enabling Webhooks
excerpt: This page outlines the steps to enable webhooks feature.
deprecated: false
hidden: false
metadata:
  robots: index
---
To use webhooks feature in Scalev, you must enable it in your account and register your webhook URL.

1. Create Scalev account if you don't have one. Register <Anchor label="here" target="_blank" href="https://app.scalev.id/register">here</Anchor>.
2. Be at one of the subscription plans that allow webhooks. Hint: it's only available for Basic plan and above. For more information about our subscription plans, you can read <Anchor label="this page" target="_blank" href="https://scalev.id/plan">this page</Anchor>.
3. Create a valid public endpoint in your app / system that will receive webhook requests from Scalev.
4. Go to <Anchor label="Settings > Developers > Webhooks" target="_blank" href="https://app.scalev.id/setting/developers">Settings > Developers > Webhooks</Anchor>.
5. Select all events that you want to listen.
6. Enter your endpoint (from point 3) in the **Webhook URL** field.
7. Turn the toggle on or off depending on your development step at the moment.
   1. If you turn the toggle off, you can save your settings but no actual webhook requests will be sent by Scalev to you.
   2. If you turn the toggle on, Scalev will start sending the events to your endpoint and your webhook will be considered as **LIVE**. When you first save the webhook settings with the toggle on, we send an initial request with the following payload:
      ```json
      {
        "event": "business.test_event",
        "timestamp": "2025-07-09T03:42:53.616800Z",
        "data": {}
      }
      ```
      You must return response with status code 200, otherwise it will fail. Also, you need to verify the request using the mechanism explained in the next page.
8. Click save.