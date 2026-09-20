---
title: "Web Analytics"
excerpt: "Read traffic, audience, engagement, and conversion reports for your Scalev business."
deprecated: false
hidden: false
metadata:
  robots: index
---
Use the Web Analytics API to build reports for your landing pages, product pages, storefront, and checkout. You can read business totals or narrow a report to a store, page type, individual page owner, domain, or path.

These reports describe traffic measured by Scalev. Advertising events sent to Meta, TikTok, or Kwai are a separate workflow; see [Storefront advertising conversion events](/docs/storefront-api-advertising-conversion-events). Sending a provider event does not create a Web Analytics page view.

## Authenticate and select a business

Call the API from your backend with a [business API key](/docs/authentication-with-api-key) or [OAuth access token](/docs/authorization-with-o-auth):

```http
Authorization: Bearer <token>
```

All reporting and filter-selection endpoints require `web_analytics:read`. You do not need operational product, page, or store list permissions to populate the analytics filters. Keep business credentials out of browser code; publishable storefront keys and customer access tokens cannot read these business reports.

An API key selects its own business. With OAuth, use `b_uid` when your connection covers multiple businesses, following the normal business-selection rules. Do not send a numeric `business_id` to select another business.

Customer privacy settings use separate `business:read` and `business:update` permissions. See [customer privacy settings](/docs/customer-privacy-settings).

## Read traffic

Set `SCALEV_API_TOKEN` to your business API key or OAuth token on your server:

```bash
curl --get 'https://api.scalev.com/v3/web-analytics/traffic' \
  --header "Authorization: Bearer $SCALEV_API_TOKEN" \
  --data-urlencode 'from=2026-09-13' \
  --data-urlencode 'to=2026-09-19' \
  --data-urlencode 'timezone=Asia/Jakarta'
```

For a multi-business OAuth connection, also send `--data-urlencode 'b_uid=<business_unique_id>'`.

The response is one report object:

```json
{
  "buckets": [
    { "day": "2026-09-13", "views": 120, "visitors": 80, "sessions": 95 },
    { "day": "2026-09-14", "views": 140, "visitors": 90, "sessions": 110 }
  ],
  "totals": { "views": 260, "visitors": 130, "sessions": 180 },
  "from": "2026-09-13",
  "to": "2026-09-19",
  "timezone": "Asia/Jakarta"
}
```

`views` counts distinct recorded page views. `visitors` and `sessions` count distinct identified visitors and sessions. Use `totals` for the whole range: someone can visit on multiple days, so adding daily visitor or session counts overstates the total. The same caution applies across pages, sources, and location buckets. An identified browser is not a verified person, and identities do not span domains.

## Choose a report

All paths below start with `/v3/web-analytics`. The twelve reports require `from` and `to`.

| GET path | What you receive |
| --- | --- |
| `/traffic` | Daily `buckets` and range-level `totals` for views, visitors, and sessions. |
| `/pages` | Top host/path pairs with views and visitors. |
| `/sources` | Traffic grouped by one UTM dimension. |
| `/audience` | Devices, countries, regions, cities, and aggregate map points. |
| `/conversion` | In-range page views and paid-order events, split by available visitor attribution. |
| `/engagement` | Average visible time and the share of visits that reported duration. |
| `/ad-clicks` | Traffic classified using advertising click identifiers. |
| `/order-funnel` | Checkout-capable page views linked to created and paid orders. |
| `/journey` | Navigation between pages, grouped by distinct sessions. |
| `/entity-journey` | The pages immediately before and after a selected page type, owner, or path. |
| `/entity-funnel` | Forward navigation for sessions starting on the selected page type, owner, or path. |
| `/source-revenue` | First-touch traffic and checkout-attributed revenue for linked paid orders. |

See [journeys, funnels, and revenue](/docs/web-analytics-journeys-and-revenue) for the different time and attribution meanings of the last five reports.

`pages`, `sources`, `ad-clicks`, and `journey` return `{ "data": [...], "is_paginated": false }`. Other reports return a report object directly. Report row limits select leading results; they do not provide cursor pagination or an exhaustive export.

## Dates and shared filters

| Parameter | Meaning |
| --- | --- |
| `from`, `to` | Required `YYYY-MM-DD` dates, inclusive, with `from` on or before `to`. Select at most 180 days. |
| `timezone` | IANA time zone used for day boundaries; defaults to `Asia/Jakarta`. For example, `Australia/Melbourne` or `Etc/UTC`. |
| `store_id` | Numeric owning store ID from the analytics store selector. |
| `entity_type` | One of the ten page types below. On its own, selects all owners of that type. |
| `entity_id` | Text representation of the owning ID; requires `entity_type`. |
| `entity_path` | Optional known path used to include older or untyped views of the same owner. Supply it with `entity_type` and `entity_id`. |
| `page_host` | Hostname, such as `shop.example.com`. Combine with `page_path` to select one address. |
| `page_path` | Exact recorded path, such as `/summer-sale` or `/`. Omitting it means all paths; an empty string does not. |
| `ad_click` | `paid`, `organic`, `meta`, `tiktok`, or `google`. Omit it for all traffic. |
| `limit` | Leading rows to return where supported. Defaults to 25; positive values are capped at 100. Audience geography uses its own limits. |

Dates refer to local calendar days in the selected time zone. The raw reporting window retains 180 days; older dates cannot recover expired events. Use the same time zone and filters when comparing reports.

`entity_id` follows the owner across slug changes. `page_path` narrows to one recorded address and can therefore exclude traffic from earlier slugs. Paths returned for sensitive pages can be generalized; use the returned reporting path instead of constructing a buyer's order URL.

`page_id` remains a compatibility alias for `entity_type=landing_page&entity_id=<id>`. Do not combine `page_id` with `entity_type` or `entity_id`; prefer the entity parameters for new integrations.

### Page types and their owners

| `entity_type` | Page | `entity_id` |
| --- | --- | --- |
| `landing_page` | Landing page, including HTML Mode | Landing page ID |
| `product` | Product page | Product ID |
| `bundle_price_option` | Bundle price option page | Bundle price option ID |
| `store_home` | Store home page | Store ID |
| `cart` | Cart page | Store ID |
| `checkout` | Checkout page | Store ID |
| `payment_link` | Payment link page | Opaque `plscope_...` ID from the payment-link selector |
| `order_detail` | Order detail page | Store ID |
| `order_success` | Order success page | Store ID |
| `order_invoice` | Order invoice page | Store ID |

Order-related page types describe the store's traffic, not an individual order. Payment-link scope IDs are reporting identifiers, not payment URLs or order IDs.

### Populate filter choices

These three GET endpoints need no date range:

| Path | Results |
| --- | --- |
| `/v3/web-analytics/entities?entity_type=landing_page` | `{id, name}` for landing pages. Also accepts `product` or `bundle_price_option`. |
| `/v3/web-analytics/stores` | `{id, name}` for stores. |
| `/v3/web-analytics/payment-links` | `{id, store_id, created_at, label}` with an opaque reporting ID and generic creation-time label. |

All three accept `search` and `page_size` from 1 to 25. Search is case-insensitive literal text, up to 200 characters, with surrounding and repeated whitespace normalized. Payment links search the date/time label, not the opaque ID or its suffix. Inactive records can remain selectable for historical reporting.

Follow `next_cursor` or `previous_cursor` from the standard paginated response. Send only one cursor at a time, and keep the business, `entity_type`, search, and page size unchanged. A changed filter starts a new pagination sequence. Do not construct cursors or use `page`, `cursor`, or `last_id`.

```http
GET /v3/web-analytics/entities?entity_type=product&search=coffee&page_size=25
Authorization: Bearer <token>
```

Use a returned ID as text in the report query, for example `entity_type=product&entity_id=101`. Do not substitute a catalog `unique_id`.

## Interpret traffic sources and ad clicks

For `/sources`, choose `utm_type=source|medium|campaign|content|term`; the default is `source`. Rows describe `first_touch` traffic attribution. Join or compare rows by both `bucket_kind` and the exact `value`:

- `direct`: the selected UTM dimension was empty. For the source dimension, label this Direct.
- `label`: a recorded UTM value, including literal labels named “Direct” or “Unknown”.
- `unknown`: the attribution label could not be resolved. Counts are `null` and status fields are `unavailable`; do not render them as zero.

For `/ad-clicks`, choose `ad_click_type`:

| Value | Buckets |
| --- | --- |
| `status` (default) | `paid`, `organic` |
| `network` | `meta`, `tiktok`, `google`, `organic` |
| `evidence` | `clicked`, `returned`, `organic` |

These rows have `basis: "ad_click_id"`. `clicked` means the page view carried a recognized advertising click identifier; `returned` means the browser remembered an earlier click. They are page-view measurements, not a provider's billable-click total. `organic` means no recognized click evidence was available and can include unrecognized or no-longer-remembered paid traffic. UTM labels and ad-click evidence answer different questions.

## Show audience data responsibly

`audience` returns `location_basis: "ip_estimate"`. Location is approximate, not a buyer's confirmed address. Region and city labels include their country or region to distinguish places with the same name.

Regions, cities, and map points require at least five distinct identified visitors per bucket. Each of these three outputs returns at most 100 eligible buckets. Read its entry in `location_metadata`: `returned_buckets`, `total_buckets`, `limit`, and `truncated`. Suppressed buckets are excluded from those counts; device and country breakdowns are independent. Map coordinates are coarse aggregate points, not individual visitor coordinates.

## Show engagement with coverage

`engagement` reports visible time in milliseconds. Divide `avg_page_ms` and `avg_session_ms` by 1,000 to display seconds. These averages use measured visits only: a browser that closes before reporting duration is not counted as a zero-second visit.

Display `page_coverage` and `session_coverage` alongside the averages. They are percentages from 0 to 100. The report also gives measured and total visit/session counts and `visible_ms_total`. An average is `null` when nothing was measured; coverage is `null` when there is no denominator. Low coverage means the average describes only a small part of the traffic.

## Compare conversion measures carefully

`conversion` counts page views and paid-order events whose event times fall in the selected dates. `matched_orders_paid` have a recorded visitor attribution; `unattributed_orders_paid` do not. Their sum is `orders_paid`.

This report is useful for spotting attribution gaps. It is not the same as the page-view cohort in `order-funnel`, where a selected visit can convert after the end date. Do not compare the two paid counts as if their date rules were identical. Neither report is a complete operational order ledger or proof that an advertising provider accepted a Purchase event.

## Refresh reports and handle errors

Web Analytics machine requests share a limit of **600 requests per hour per credential**, including filter selectors, in addition to the normal hourly and burst limits. Cache results for repeated filter selections and avoid polling every panel every few seconds. Read the `X-Ratelimit-*` headers and back off on `429`; rate-limit responses may be plain text.

An invalid date, range, time zone, entity, or report dimension returns `400`. A missing/expired credential returns `401`, and a missing scope returns `403`. A source-revenue request with too many linked paid orders asks you to select a shorter range. Do not turn a failed report into an empty successful result.

Recently collected events may take time to appear. Collection is affected by regional consent requirements, visitor choices, browser blocking, missing identities, and excluded self-traffic. Granting consent starts current collection; it does not reconstruct earlier activity. Check [customer privacy settings](/docs/customer-privacy-settings) when investigating missing measurements.

## Use the reports through MCP

With the [Scalev MCP connector](/docs/scalev-mcp-connector), select the business with `get_me`, discover a report with `search`, and read it with `get`. Ask `get_docs` for the Web Analytics guide before interpreting funnels or revenue. When multiple businesses are connected, pass `business_unique_id` at the top level of the tool call. The same API scopes, filters, and reporting limits apply.
