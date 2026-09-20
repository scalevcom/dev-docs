---
title: "Journeys, funnels, and revenue"
excerpt: "Follow page navigation and connect measured visits to orders and payment revenue."
deprecated: false
hidden: false
metadata:
  robots: index
---
The [Web Analytics API](/docs/web-analytics) gives you several ways to follow a visit through checkout. Choose the report that matches your question: a navigation step, a group of visits, or a payment event. They have different denominators and date rules.

All examples use business bearer authentication with `web_analytics:read`. Add the normal `b_uid` selector for multi-business OAuth connections.

## Follow navigation between pages

`GET /v3/web-analytics/journey` returns the leading page-to-page transitions in the selected date range:

```http
GET /v3/web-analytics/journey?from=2026-09-13&to=2026-09-19&timezone=Asia%2FJakarta&limit=25
Authorization: Bearer <token>
```

Each row contains `from_node`, `to_node`, `sessions`, and `from_sessions`. Nodes can be an entity key such as `landing_page:101` or a recorded path when an entity identity is unavailable.

`sessions` counts distinct sessions taking that transition. `from_sessions` counts distinct sessions with an outgoing transition from that node and repeats on each outgoing row. Use it as the denominator for an edge's share. Do not sum the outgoing `sessions`: one session can take more than one outgoing edge. A session that ends at the node has no outgoing transition and is absent from this denominator.

With an entity or path filter, a transition is retained when either endpoint matches the focus. Neighboring pages remain visible. Payments do not become navigation steps.

## Inspect what happens around a page

`GET /v3/web-analytics/entity-journey` centers the report on `entity_type`, optionally narrowed by `entity_id`, or on `page_path`. A type alone is valid; it selects all owners of that page type. Use a stable owner ID when you mean one page.

```http
GET /v3/web-analytics/entity-journey?from=2026-09-13&to=2026-09-19&entity_type=landing_page&entity_id=101
Authorization: Bearer <token>
```

The response contains `came_from` and `went_to`, each with `node`, `path`, `is_terminal`, and `sessions`:

- `entered_here` with `is_terminal: true` means no earlier page was recorded in that session sequence.
- `left` with `is_terminal: true` means no following page was recorded.
- Other nodes identify the preceding or following page.

This report includes sessions that reached the focus after starting elsewhere. The date range bounds the observed sequence, so an entry or exit describes what was recorded in that range, not every visit the browser has ever made.

## Follow sessions that start on a page

`GET /v3/web-analytics/entity-funnel` uses the same focus parameters but selects sessions whose first recorded page view in the selected range matches the focus. It follows those sessions forward:

```http
GET /v3/web-analytics/entity-funnel?from=2026-09-13&to=2026-09-19&entity_type=landing_page&entity_id=101&max_steps=6
Authorization: Bearer <token>
```

The response contains:

- `sessions`: sessions in the starting group.
- `paid_sessions`: sessions with a linked paid-order outcome.
- `steps`: rows containing `step`, `node`, `path`, and `sessions` at that depth.

`max_steps` defaults to 6 and is capped at 10. The separate `limit` bounds the returned leading step rows; it does not change the requested depth. There is no synthetic exit step. Payments are separate outcomes, not extra page visits.

For both centered reports, the entity/path identifies the focus while store, host, date, and ad-click filters still restrict the observed traffic. A request without an entity type or path returns `400`.

## Measure the order funnel

`GET /v3/web-analytics/order-funnel` answers: “What happened to the checkout-capable page views in this range?”

The selected dates and filters choose the originating page views. Linked order creation and payment recorded later can update their outcomes, through report time and within retained history. For example, a visit on September 13 followed by payment on September 20 can appear as a paid outcome when you rerun the September 13 report.

```http
GET /v3/web-analytics/order-funnel?from=2026-09-13&to=2026-09-19&entity_type=landing_page&entity_id=101
Authorization: Bearer <token>
```

```json
{
  "visitors": 70,
  "views": 100,
  "unknown_eligibility_views": 3,
  "excluded_views": 12,
  "denominator_basis": "order_capable_pageviews",
  "views_with_order": 20,
  "views_with_paid_order": 15,
  "orders_created": 24,
  "orders_paid": 18,
  "linked_order_counts_only": true,
  "basis": "page_view_cohort"
}
```

Use these separate measures:

| Field | Meaning |
| --- | --- |
| `views` | Recorded checkout-capable page views; the funnel denominator. |
| `views_with_order` | Those page views with at least one linked created order. |
| `views_with_paid_order` | Those page views with at least one linked paid order. |
| `orders_created`, `orders_paid` | Actual distinct linked orders, including multiple orders from one page view. |
| `unknown_eligibility_views` | Views whose checkout eligibility could not be established from recorded data. |
| `excluded_views` | Views recorded as not checkout-capable. |

For the example, the view-to-order rate is `20 / 100 = 20%`, and the view-to-paid rate is `15 / 100 = 15%`. The 18 paid orders do not mean 18% of page views converted: some views produced multiple orders. If you label a count **Orders created**, use `orders_created`, not `views_with_order`.

Orders without a usable link to a measured originating view are not included in this funnel. A later page configuration change does not retroactively establish checkout eligibility for an older visit. Use `conversion` to inspect in-range paid events with and without visitor attribution; use operational Orders APIs for order records.

## Read revenue by source

`GET /v3/web-analytics/source-revenue` combines traffic grouped by the visited URL's UTM value with paid orders grouped by the UTM value captured at checkout:

```http
GET /v3/web-analytics/source-revenue?from=2026-09-13&to=2026-09-19&timezone=Asia%2FJakarta&utm_type=campaign&limit=25
Authorization: Bearer <token>
```

`utm_type` accepts `source` (default), `medium`, `campaign`, `content`, or `term`. The response has `first_touch`, `last_touch`, and `last_touch_scope`.

### Keep first and last touch distinct

`first_touch` contains traffic rows with views, visitors, and sessions. `last_touch` contains linked paid-order counts and revenue, attributed to the selected order-creation event's checkout UTM value. A visit's campaign and its checkout campaign can differ. Do not assume matching array positions or treat either as a multi-touch attribution model.

Match known source rows by **both** `bucket_kind` and exact `value`, and keep each revenue currency separate. A direct bucket has an empty value; a literal campaign named “Direct” is still a label bucket. An unknown bucket is unavailable data, not Direct and not zero.

The `last_touch_scope` identifies the applied filters and reports:

```json
{
  "status": "available",
  "applied_filters": ["from", "to", "timezone", "utm_type", "limit"],
  "unsupported_filters": [],
  "basis": "page_view_cohort",
  "linked_order_counts_only": true,
  "revenue_basis": "payment_snapshot_with_order_fallback"
}
```

The paid-order group follows the same originating checkout-capable views as `order-funnel`. Dates refer to those visits, not solely to payment dates. All shared store, entity, host, path, and ad-click filters apply to that originating group.

### Preserve currency and missing values

Each `last_touch` row represents one source and currency. `gross_revenue` and `net_revenue` are exact decimal strings, such as `"125000.00"`. Use decimal arithmetic, and never add different currencies together or invent an exchange rate.

Gross includes the recorded order's shipping, other, and service amounts. Net is product revenue after discounts; it is not profit. A complete payment snapshot preserves the first qualifying recorded amount. Later refunds, settlement updates, or edits do not rewrite it. This report is an observed-payment measure, not current cash after reversals.

Older paid events can use current order values when the original payment amounts were not recorded. Read the coverage fields:

| Field | Meaning |
| --- | --- |
| `snapshot_orders` | Paid orders with a complete recorded payment amount and currency. |
| `fallback_orders` | Older paid orders valued using their current order amounts. |
| `missing_revenue_orders` | Linked paid orders whose amounts remain unavailable. |
| `revenue_status` | `available` when the row's amounts are complete, otherwise `unavailable`. |
| `traffic_status` | Whether attribution is sufficiently resolved to report the traffic counterpart. |

A row with unresolved money returns null amounts rather than a partial total. Its known linked order count can still be present. An unresolved attribution label returns an unknown bucket with null counts. A measured zero is different from null. Show an unavailable state and coverage instead of turning null into zero or displaying a partial sum as the total.

`limit` selects leading source keys; all currency rows for a selected source are retained. Traffic leaders and revenue leaders may both appear, so an array can contain more rows than the requested limit. Results can still omit other sources. Missing counterparts and top-list sums do not establish zero revenue or complete business totals. Complete single-currency revenue ranks by gross revenue; mixed or incomplete currency reports rank by linked paid orders.

A report with more than 100,000 linked paid orders returns an error. Select a shorter date range rather than presenting a truncated revenue total.
