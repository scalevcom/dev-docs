---
title: Upload orders from CSV file
excerpt: >-
  Upload orders from CSV file. (1) Archive mode. Choose this mode if you want to
  import old data from another platform you've been using. You can directly
  create products that you made on your previous platform. Orders that are
  created will immediately have 'Completed' status. Download template for
  Archive mode here: https://app.scalev.id/example/template_archive.csv. (2)
  Regular mode. Choose this mode if you want to enter current data that you wish
  to input in bulk, not one by one via order input. It will take inventory into
  account if your products have inventory enabled. Successfully created orders
  will have 'Created', 'Pending', or 'Confirmed' status, depending on the
  completeness of the data. Download template for Regular mode here:
  https://app.scalev.id/example/template_regular.csv.
api:
  file: openapi.documented.json
  operationId: ScalevApiWeb.OrderController.upload_orders
hidden: false
---