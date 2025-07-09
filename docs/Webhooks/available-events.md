---
title: Available Events
deprecated: false
hidden: false
metadata:
  robots: index
---
Scalev currently supports the following webhook events:

* `order.created`: Triggered when a new order is created.
* `order.epayment_created`: Triggered when the payment of an order using e-payment is successfully created. When this event occurs, customers can actually pay with the various methods provided by the e-payment provider in your account.
* `order.updated`: Triggered when an existing order is updated.
* `order.deleted`: Triggered when an order is deleted.
* `order.status_changed`: Triggered when the status of an order changes.
* `order.payment_status_changed`: Triggered when the payment status of an order changes.
* `order.spam_created`: Triggered when a spam order is created.