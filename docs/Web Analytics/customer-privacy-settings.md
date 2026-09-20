---
title: "Customer privacy settings"
excerpt: "Read and update the countries where your business asks for analytics or marketing consent."
deprecated: false
hidden: false
metadata:
  robots: index
---
Use `/v3/customer-privacy` to configure where your business requires a visitor's choice before analytics or marketing runs. The two country lists are independent:

- `analytics_consent_countries`: requires permission for Scalev traffic and order measurement.
- `marketing_consent_countries`: requires permission for configured advertising and marketing providers.

A country **in** a list requires a choice for that category. A country **outside** the list allows that category without waiting for a choice; it does not mean tracking is disabled. If neither category requires consent for the visitor's country, the hosted page does not show the cookie banner or privacy-settings control.

## Authenticate

Use a business API key or OAuth bearer token from your backend:

| Operation | Scope |
| --- | --- |
| `GET /v3/customer-privacy` | `business:read` |
| `PATCH /v3/customer-privacy` | `business:update` |

The authenticated business owns the settings. Use the usual `b_uid` selector for a multi-business OAuth connection. Do not send a numeric `business_id` in the update body.

Reading [Web Analytics reports](/docs/web-analytics) requires `web_analytics:read` instead. Report access alone cannot read or change these administrative settings.

## Read before editing

```bash
curl 'https://api.scalev.com/v3/customer-privacy' \
  --header "Authorization: Bearer $SCALEV_API_TOKEN"
```

The response includes the current integer `revision`, both consent-country lists, and `country_codes`, the complete supported list. Use uppercase ISO 3166-1 alpha-2 codes from `country_codes`, such as `ID`, `AU`, and `GB`. The United Kingdom is `GB`, not `UK`.

The initial selections contain the United Kingdom and EEA countries. Indonesia and Australia are not initially selected. Always read the saved values; a merchant can change them. Unknown location is not a selectable country and currently follows the no-consent-required default.

Other response fields include `business_id`, `notice_version`, `marketing_generation`, and compatibility legal-acceptance information. Treat these as read-only. They are not fields you can use to grant a visitor's consent, and the compatibility owner-acceptance fields are not a new prerequisite for collection.

## Replace the country selections

PATCH requires exactly the current integer `revision` and **both complete lists**. An empty list is valid. Omitted lists, unsupported codes, additional fields, or a string revision return `400 invalid_customer_privacy_settings`.

To add Indonesia to the analytics selection while preserving the other settings, build the update from the latest GET response:

```javascript
// Run on your backend. Keep SCALEV_API_TOKEN out of browser code.
const endpoint = new URL("https://api.scalev.com/v3/customer-privacy");
// For multi-business OAuth, set endpoint.searchParams.set("b_uid", businessUniqueId).
const headers = { Authorization: `Bearer ${process.env.SCALEV_API_TOKEN}` };

const read = await fetch(endpoint, { headers });
if (!read.ok) throw new Error(`Read failed: ${read.status}`);
const current = await read.json();

const update = await fetch(endpoint, {
  method: "PATCH",
  headers: { ...headers, "Content-Type": "application/json" },
  body: JSON.stringify({
    revision: current.revision,
    analytics_consent_countries: [
      ...new Set([...current.analytics_consent_countries, "ID"]),
    ],
    marketing_consent_countries: current.marketing_consent_countries,
  }),
});

if (update.status === 409) {
  throw new Error("Settings changed. Reload them and review your edit before saving again.");
}
if (!update.ok) throw new Error(`Update failed: ${update.status}`);
const saved = await update.json();
```

A successful update returns `200` with the updated resource. The revision advances by one; country lists are deduplicated and sorted.

If another change occurred after your GET, PATCH returns `409` with `error_code: "customer_privacy_conflict"`. Fetch the new resource, compare the changed selections, and reapply the intended edit. Do not automatically overwrite the newer lists or replay the old whole response as a PATCH body.

A successful save also starts refreshing the affected public page caches across the business's domains. Propagation is asynchronous, so an already open or recently cached page may retain the earlier configuration briefly. New page responses carry the updated settings after refresh.

## Understand what visitors and orders measure

On hosted pages, the browser combines the country's requirements with the visitor's saved local choices. Where consent is required, unanswered or declined categories do not run. Where it is not required, earlier refusal choices do not block the category. Selecting individual marketing partners can further restrict those partners where consent is required.

A visitor's new choice takes effect locally without waiting for a network receipt. Granting permission starts collection from that point; it does not replay earlier activity. A later refusal stops new browser dispatch where consent is required. Browser blocking and unavailable storage can still affect the measured traffic.

An order retains the applicable tracking decision captured when it was created. Later settings or browser-choice changes do not rewrite that saved order decision. An explicit saved refusal prevents later tracking for its category or recipient; an older order with no saved choice does not gain a new consent block merely because that context is absent. Provider configuration and other delivery requirements still apply.

These operations change business policy, not an individual visitor's preferences. They do not provide a visitor-consent database or an API to reset everyone's choices. In HTML Mode, use the supported page runtime for configured behavior; independently added scripts must honor the visitor's choices too.

## Use settings through MCP

With the [Scalev MCP connector](/docs/scalev-mcp-connector), discover these operations with `search`. Use `get` to read the current settings and `execute_safe` to PATCH the reviewed selections with the current revision. The update is a business-wide change, so review the intended country additions and removals before submitting it. The same scopes and conflict handling apply.
