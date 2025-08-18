---
title: Authentication with API Key
excerpt: >-
  This document outlines the process of using API Key for authentication, as
  alternative to using OAuth 2.0 flow.
deprecated: false
hidden: false
metadata:
  robots: index
---
## Overview

The Scalev API also supports API key authentication for server-to-server integrations. API keys provide direct access to your business data without requiring OAuth flows, making them ideal for backend services, automation tools, and integrations.

## API Key Types

### Secret Keys (`sk_...`)

* **Full Access**: Complete access to all business data and operations
* **No Permission Restrictions**: Can perform any action available to the business
* **Use Case**: Trusted backend services, administrative tools
* **Security**: Store securely, never expose in client-side code

```bash
Authorization: Bearer sk_1a2b3c4d5e6f7g8h9i0j...
```

### Restricted Keys (`rk_...`)

* **Limited Access**: Access based on explicitly assigned scopes
* **Scope-Based**: Must specify exact scopes needed
* **Use Case**: Third-party integrations, specialized tools, least-privilege access
* **Security**: Safer for external integrations with limited scope

```bash
Authorization: Bearer rk_9z8y7x6w5v4u3t2s1r0q...
```

## Creating API Keys

1. Navigate to **Settings** → **Developers** → **API Keys** in your business dashboard
2. Click **"Create API Key"**
3. Configure the key:
   * **Name**: Descriptive name (e.g., "Inventory Sync", "Analytics Bot")
   * **Description**: Optional purpose description
   * **Key Type**: Choose `secret` or `restricted`
   * **Scopes**: For restricted keys, select specific scopes
   * **Expiration**: Optional expiration date

> ⚠️ **Important**: The full API key is only shown once during creation. Store it securely!

### View API Keys

1. Go to **Settings** → **Developers** → **API Keys**
2. View list of all your API keys with:
   * Key name and description
   * Key type (Secret or Restricted)
   * Scopes (for restricted keys)
   * Status (Active/Expired)
   * Created at
   * Expired at (if applicable)

### Update API Key

API key updates have different restrictions based on key type:

#### Secret Keys

* **Can Update**: Name, description
* **Cannot Update**: Key type, scopes (has full access by default), expiration

#### Restricted Keys

* **Can Update**: Name, description, scopes
* **Cannot Update**: Key type, expiration

**To update an API key:**

1. Go to **Settings** → **Developers** → **API Keys**
2. Click on the API key you want to update
3. Click **Edit**
4. Modify the allowed fields
5. Click **Save**

### Rotate API Key

Generate a new API key string while preserving all metadata and settings. The old key becomes invalid immediately.

**To rotate an API key:**

1. Go to **Settings** → **API Keys**
2. Click on the API key you want to rotate
3. Click **Regenerate Key**
4. Confirm the action
5. Copy the new API key (shown only once)
6. Update your applications with the new key

> ⚠️ **Important**: Update your applications immediately with the new key. The old key stops working as soon as regeneration completes.

### Delete/Revoke API Key

Permanently revoke an API key. This action cannot be undone.

**To delete an API key:**

1. Go to **Settings** → **API Keys**
2. Click on the API key you want to delete
3. Click **Delete Key**
4. Confirm the deletion

> ⚠️ **Important**: Deleted API keys cannot be recovered. Any applications using the deleted key will immediately lose access.

## Authentication Methods

API keys must be provided in the Authorization header using the Bearer token format:

```bash
curl -X GET https://api.scalev.id/v2/order \
  -H "Authorization: Bearer sk_your_api_key_here"
```

## Rate Limiting

Each API key has a rate limit (default: 10.000 requests/hour). When exceeded, you'll receive a `429 Too Many Requests` response.

## Error Responses

### Invalid API Key (401)

```json
{
  "error": "Invalid API key",
  "status": "Unauthorized",
  "code": 401
}
```

### Expired API Key (401)

```json
{
  "error": "API key has expired",
  "status": "Unauthorized",
  "code": 401
}
```

### Insufficient Permissions (403)

```json
{
  "status": "Forbidden",
  "code": 403
}
```

## Security Best Practices

### 1. Store API Keys Securely

* Never commit API keys to version control
* Use environment variables or secure key management systems
* Rotate keys regularly, especially secret keys

### 2. Use Least Privilege Principle

* Use restricted keys with minimal required permissions
* Create separate keys for different purposes
* Regularly audit and update permissions

### 3. Monitor Usage

* Set up alerts for unusual API usage patterns
* Regularly review API key usage statistics
* Monitor for unauthorized access attempts

### 4. Network Security

* Use HTTPS for all API calls
* Consider IP whitelisting for sensitive operations
* Implement proper error handling to avoid information leakage

### 5. Key Management

* Set expiration dates for temporary integrations
* Immediately revoke compromised keys
* Use descriptive names to identify key purposes

## Environment Variables Example

```bash
# .env file
SCALEV_API_KEY=sk_1a2b3c4d5e6f7g8h9i0j...
SCALEV_API_BASE_URL=https://api.scalev.com/v2
```

## Webhook Integration

For real-time updates, combine API keys with webhooks:

1. Use API keys for pulling data and making updates
2. Configure webhooks for real-time event notifications
3. Verify webhook signatures for security
4. Use restricted keys with webhook endpoints when possible