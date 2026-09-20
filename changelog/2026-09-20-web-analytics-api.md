---
title: Web Analytics reports and customer privacy settings
slug: web-analytics-api-and-customer-privacy-settings
type: none
created_at: 2026-09-20T10:30:00+10:00
privacy:
  view: public
---

**You can now integrate the full Web Analytics reporting API with business API keys, OAuth, and Scalev MCP.**

Read traffic, top pages, UTM sources, audience, ad-click attribution, engagement, conversion, navigation, funnels, and source revenue with `web_analytics:read`. Analytics-specific selectors let you choose landing pages, products, bundle price options, stores, and payment links without requesting their operational list permissions.

The [Web Analytics guide](/docs/web-analytics) explains date ranges, time zones, page filters, pagination, and measurement coverage. The [journeys and revenue guide](/docs/web-analytics-journeys-and-revenue) distinguishes page-view cohorts from in-range payment events and explains revenue currencies and missing values.

You can also read and update the business's [customer privacy country selections](/docs/customer-privacy-settings). Reads require `business:read`; updates require `business:update`, both country lists, and the current revision to protect concurrent edits.
