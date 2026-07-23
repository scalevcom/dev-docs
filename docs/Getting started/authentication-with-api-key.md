---
title: "Authentication with API Key"
excerpt: "Authenticate trusted server-side integrations with a Scalev business API key."
deprecated: false
hidden: false
metadata:
  robots: index
---
## Overview

Scalev supports API keys for machine-authenticated server-to-server requests.

API keys are the simplest option when your own backend needs to call Scalev directly without running an OAuth install flow. They are intended for backend services, automation, internal tools, and other trusted machine integrations.

API keys authenticate business routes, primarily on the `/v3` API surface.

They are **not** used for:

- storefront public routes under `/v3/stores/{store_id}/public/*`
- customer-authenticated routes under `/v3/stores/{store_id}/customers/me/*`
- dashboard-only routes that are intentionally excluded from machine access
- OAuth-specific install and token flows

## Base URL

```text
https://api.scalev.com
```

Most machine-authenticated integrations should use `/v3` routes.

## API Key Types

### Secret Keys (`sk_...`)

Secret keys are full-access machine credentials.

Behavior:

- full scope coverage across machine-eligible business endpoints
- no per-scope restriction
- best for trusted backend services and internal automation
- must be stored securely and never exposed in browser or mobile code

### Restricted Keys (`rk_...`)

Restricted keys are scope-limited machine credentials.

Behavior:

- access is limited to explicitly assigned scopes
- must include at least one scope
- can only use machine-eligible global scopes
- good for least-privilege integrations and third-party backend connectors

## Creating API Keys

API keys are created from the Scalev dashboard at:

```text
Settings > Developers > API Keys
```

Current dashboard route:

```text
/setting/developers/api-keys
```

When creating a key, configure:

- **Name**
- **Description** (optional)
- **Key Type**: `secret` or `restricted`
- **Scopes**: required for restricted keys
- **Expiration**: optional

Important current rules:

- full key value is shown only once when the key is created
- restricted keys must have at least one scope
- secret keys ignore scopes
- a business can have at most **10 API keys**

## Viewing API Keys

From the dashboard, you can view the existing API keys.

Visible metadata includes:

- name
- description
- key type
- scopes
- `last_used_at`
- `expires_at`
- `is_expired`
- `usage_count`
- `rate_limit_per_hour`
- created by
- created at
- updated at

Important behavior:

- list and detail views show the key in masked form
- the raw key value is not shown again after creation unless you rotate it

## Updating API Keys

You can update API key metadata from the dashboard.

### Secret Keys

You can update:

- name
- description

You cannot update:

- key type
- raw key value
- expiration
- scopes

### Restricted Keys

You can update:

- name
- description
- scopes

You cannot update:

- key type
- raw key value
- expiration

## Rotating API Keys

Rotating a key generates a new raw API key value while preserving the existing metadata and settings.

Behavior:

- the old key becomes invalid immediately
- the new raw key is shown once
- key type, scopes, and expiration remain tied to the same key record

## Deleting API Keys

Deleting an API key revokes it permanently.

Behavior:

- the key stops working immediately
- deleted keys cannot be recovered

## Authentication

API keys are sent in the `Authorization` header using bearer format:

```bash
curl -X GET https://api.scalev.com/v3/stores \
  -H "Authorization: Bearer sk_your_api_key_here"
```

You can use either:

- `sk_...`
- `rk_...`

## Where API Keys Work

API keys are for machine-authenticated business requests.

They work on routes that allow machine auth through API keys.

They do **not** replace other auth models:

### Storefront public routes

Routes under `/v3/stores/{store_id}/public/*` use:

```text
X-Scalev-Storefront-Api-Key: sfpk_...
```

Storefront public API keys are generated from the store configuration page in the separate Storefront API section. They are publishable browser keys, not business API keys.

### Customer routes

Routes under `/v3/stores/{store_id}/customers/me/*` use customer bearer tokens.

### Dashboard-only routes

Some routes are intentionally dashboard-only. API keys cannot create, update, rotate, or delete dashboard-managed resources on those routes.

### OAuth-only routes

API keys are not a substitute for OAuth installation or OAuth app tokens.

## Permissions Model

Permission behavior depends on key type:

- **Secret keys**: treated as full-access for machine-eligible business scopes
- **Restricted keys**: must include the exact required scope

If a restricted key does not include the required scope, the request is rejected with `403 Forbidden`.

## Rate Limiting

Each API key has credential-scoped rate limits.

Current default:

- **10,000 requests per hour per key**
- **100 requests per 10 seconds per key** for short bursts

Storefront public requests using `X-Scalev-Storefront-Api-Key` or `X-Scalev-Guest-Token` are not API-key requests and are rate-limited as direct browser/client traffic on a separate client/IP bucket.

Rate-limit metadata is returned in response headers. The header values describe the bucket that applied to that response:

- `X-Ratelimit-Limit`
- `X-Ratelimit-Remaining`
- `X-Ratelimit-Reset`

When the limit is exceeded, the API returns:

- `429 Too Many Requests`

Some endpoints may apply stricter endpoint-specific limits.

Rate-limit responses may be plain text instead of the normal JSON error shape.

## Error Responses

For `/v3` routes, API key authentication errors use the v3 error shape.

### Invalid API Key (401)

```json
{
  "error": "Invalid API key"
}
```

### Expired API Key (401)

```json
{
  "error": "API key has expired"
}
```

### Insufficient Permissions (403)

```json
{
  "error": "Forbidden"
}
```

Note:

- rate-limit responses are not guaranteed to use the normal JSON error shape

## Security Best Practices

### 1. Store API Keys Securely

- never commit API keys to source control
- keep them in environment variables or a secret manager
- never expose them in frontend code

### 2. Prefer Restricted Keys

- use restricted keys whenever full access is not required
- grant only the scopes the integration actually needs
- create separate keys for separate integrations

### 3. Rotate and Revoke Quickly

- rotate keys if you suspect exposure
- revoke keys that are no longer needed
- replace old credentials in downstream systems immediately after rotation

### 4. Use Expiration When Appropriate

- set expirations for temporary or partner-specific integrations
- avoid long-lived keys unless there is a clear operational reason

### 5. Monitor Usage

- review `last_used_at` and `usage_count`
- watch for unexpected spikes or unusual access patterns

### 6. Use HTTPS Only

- send API keys only over HTTPS
- do not log full key values in plaintext application logs

## Environment Variables Example

```bash
SCALEV_API_KEY=sk_1a2b3c4d5e6f...
SCALEV_API_BASE_URL=https://api.scalev.com
```

## Webhooks

API keys are for authenticated API requests.

They are **not** webhook secrets and are **not** used to validate webhook deliveries. If your integration also uses webhook features, configure those separately and do not reuse API keys as webhook verification material.
