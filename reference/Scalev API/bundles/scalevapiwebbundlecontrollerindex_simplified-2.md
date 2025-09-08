---
title: List bundles (simplified)
excerpt: >-
  Retrieves a paginated list of bundles with optional filtering. The data is
  sorted by id in descending order and cannot be changed. Uses cursor-based
  pagination with default page size of 25 and maximum of 25. This endpoint
  returns a simplified version of the bundle data, including only essential
  fields and active bundle price options.
api:
  file: openapi.documented.yml
  operationId: ScalevApiWeb.BundleController.index_simplified
hidden: false
---