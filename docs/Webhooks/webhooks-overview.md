---
title: "Overview"
excerpt: "Receive event notifications from Scalev through signed HTTP webhooks."
deprecated: false
hidden: false
metadata:
  robots: index
---
Webhooks are ways for Scalev to notify you when certain events happen. When the specified events occur, Scalev will send an HTTP POST request to the webhook URL you provided. You can use webhooks to trigger custom code or actions in your system.

Webhooks are sent as POST requests with a JSON payload in the request body. The payload contains the event type and the data associated with the event. The webhook URL must be a publicly accessible URL that can receive POST requests from Scalev.
