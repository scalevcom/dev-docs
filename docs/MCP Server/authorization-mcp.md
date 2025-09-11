---
title: Authorization
excerpt: This page outlines how you can interact with Scalev MCP using your API Key.
deprecated: false
hidden: false
metadata:
  robots: index
---
## Overview

This document describes the OAuth implementation for MCP (Model Context Protocol) with dynamic client registration support. The implementation follows the OAuth 2.0 Authorization Code flow with PKCE (Proof Key for Code Exchange), often known as OAuth 2.1, and allows third-party applications to securely access MCP resources on behalf of businesses.

### Important Architecture Note

The MCP OAuth implementation uses a **per-api-key client registration model**:

* Each business requires their own unique client registration
* 1 client registration = 1 API key
* Client credentials (client_id and client_secret) cannot be shared across multiple api keys
* Applications must dynamically register a new client for each business who wants to connect their Scalev account

## Authentication Flow

The MCP OAuth implementation uses the Authorization Code flow with PKCE (Proof Key for Code Exchange) for enhanced security. The complete flow consists of five main steps:

1. Dynamic Client Registration
2. User Authorization
3. Token Exchange
4. API Access
5. Token Refresh

## Base URL

All OAuth endpoints are available at: `https://mcp.scalev.id`

## Step 1: Dynamic Client Registration

Before initiating the OAuth flow, applications must register as a client with the MCP authorization server.

### Endpoint

```
POST https://mcp.scalev.id/register
```

### Request Headers

```
Content-Type: application/json
```

### Request Payload

```json
{
  "client_name": "Your User and App Identifier",
  "redirect_uris": ["https://yourapp.com/callback"],
  "grant_types": ["authorization_code", "refresh_token"],
  "response_types": ["code"],
  "logo_uri": "https://yourapp.com/logo.png",
  "client_uri": "https://yourapp.com"
}
```

### Request Parameters

| Parameter        | Type   | Required | Description                                                                                  |
| ---------------- | ------ | -------- | -------------------------------------------------------------------------------------------- |
| `client_name`    | string | Yes      | Human-readable name of the client application                                                |
| `redirect_uris`  | array  | Yes      | Array of allowed redirect URIs for the authorization response                                |
| `grant_types`    | array  | Yes      | OAuth grant types the client will use. Must include `authorization_code` and `refresh_token` |
| `response_types` | array  | Yes      | OAuth response types. Must include `code` for authorization code flow                        |
| `logo_uri`       | string | No       | URL of the client application's logo                                                         |
| `client_uri`     | string | No       | URL of the client application's homepage                                                     |

### Response

```json
{
    "client_id": "abc123def456",
    "redirect_uris": ["https://yourapp.com/callback"],
    "client_name": "Your Application Name",
    "client_uri": "https://yourapp.com",
    "grant_types": ["authorization_code", "refresh_token"],
    "response_types": ["code"],
    "token_endpoint_auth_method": "client_secret_basic",
    "registration_client_uri": "/register/abc123def456",
    "client_id_issued_at": 1757554272,
    "client_secret": "xyz789secret123"
}
```

### Response Parameters

| Parameter                    | Type    | Description                                                                       |
| ---------------------------- | ------- | --------------------------------------------------------------------------------- |
| `client_id`                  | string  | Unique identifier for the registered client                                       |
| `client_secret`              | string  | Client secret for authentication (keep this secure!)                              |
| `token_endpoint_auth_method` | string  | Method for authenticating at the token endpoint (typically `client_secret_basic`) |
| `registration_client_uri`    | string  | URI for managing this client registration                                         |
| `client_id_issued_at`        | integer | Unix timestamp of when the client was registered                                  |

**Important:** Store the `client_id` and `client_secret` securely. The client secret should never be exposed in client-side code or public repositories.

## Step 2: User Authorization

Direct the user to the authorization endpoint to grant permissions to your application.

### Endpoint

```
GET https://mcp.scalev.id/authorize
```

### Request Parameters

| Parameter               | Type   | Required | Description                                                 |
| ----------------------- | ------ | -------- | ----------------------------------------------------------- |
| `response_type`         | string | Yes      | Must be `code`                                              |
| `client_id`             | string | Yes      | The client ID obtained during registration                  |
| `redirect_uri`          | string | Yes      | Must match one of the registered redirect URIs              |
| `state`                 | string | Yes      | Opaque value to maintain state between request and callback |
| `code_challenge`        | string | Yes      | PKCE code challenge (for enhanced security)                 |
| `code_challenge_method` | string | Yes      | Must be `S256` when using PKCE                              |

### Example Authorization URL

```
https://mcp.scalev.id/authorize?
  response_type=code&
  client_id=abc123def456&
  redirect_uri=https://yourapp.com/callback&
  state=xyz789&
  code_challenge=E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM&
  code_challenge_method=S256
```

### User Authentication on Authorization Page

When users are redirected to the authorization page, they will be presented with an OAuth consent screen where they need to:

1. **Enter their Scalev API Key** - Users must authenticate themselves by providing their Scalev API Key
2. **Approve or deny the authorization request** - Users can choose to grant or deny access to the requesting application

**Note:** The Scalev API Key is used to authenticate the user and link their Scalev account with the OAuth authorization. Users should have their API Key ready, which can be obtained from their Scalev account dashboard. Read [this guide](https://developers.scalev.id/docs/authentication-with-api-key#/) to learn how to obtain API Key.

### Authorization Response

After the user enters their API Key and approves the authorization request, they will be redirected to your specified `redirect_uri` with an authorization code:

```
https://yourapp.com/callback?code=AUTH_CODE_HERE&state=xyz789
```

The authorization code will be URL-encoded so you need to decode it first before using it for the next step.

## Step 3: Exchange Authorization Code for Access Token

Exchange the authorization code for an access token and refresh token.

### Endpoint

```
POST https://mcp.scalev.id/token
```

### Request Headers

```
Content-Type: application/x-www-form-urlencoded
```

### Request Body

```
client_id=CLIENT_ID_HERE&
client_secret=CLIENT_SECRET_HERE&
grant_type=authorization_code&
code=AUTH_CODE_HERE&
redirect_uri=https://yourapp.com/callback&
code_verifier=PKCE_VERIFIER_HERE
```

### Request Parameters

| Parameter       | Type   | Required | Description                                                     |
| --------------- | ------ | -------- | --------------------------------------------------------------- |
| `client_id`     | string | Yes      | The client ID obtained during registration                      |
| `client_secret` | string | Yes      | The client secret obtained during registration                  |
| `grant_type`    | string | Yes      | Must be `authorization_code`                                    |
| `code`          | string | Yes      | The authorization code received from the authorization endpoint |
| `redirect_uri`  | string | Yes      | Must match the redirect URI used in the authorization request   |
| `code_verifier` | string | Yes      | Required since PKCE was used in the authorization request       |

### Response

```json
{
    "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "refresh_token": "def50200c4f7e9b4d6a8b9c2...",
    "scope": ""
}
```

### Response Parameters

| Parameter       | Type    | Description                                                 |
| --------------- | ------- | ----------------------------------------------------------- |
| `access_token`  | string  | The access token for making API requests                    |
| `token_type`    | string  | Type of token (always `Bearer`)                             |
| `expires_in`    | integer | Token lifetime in seconds (typically 3600 seconds = 1 hour) |
| `refresh_token` | string  | Token for obtaining new access tokens                       |
| `scope`         | string  | Granted scopes (space-separated)                            |

## Step 4: Making Authenticated API Requests

Include the access token in the Authorization header when making requests to MCP endpoints.

### Request Header

```
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Step 5: Refreshing the Access Token

When the access token expires or is close to expiring, use the refresh token to obtain a new access token without requiring user interaction.

### Endpoint

```
POST https://mcp.scalev.id/token
```

### Request Headers

```
Content-Type: application/x-www-form-urlencoded
```

### Request Body

```
grant_type=refresh_token&
refresh_token=def50200c4f7e9b4d6a8b9c2...&
client_id=abc123def456&
client_secret=xyz789secret123
```

### Request Parameters

| Parameter       | Type   | Required | Description                                                  |
| --------------- | ------ | -------- | ------------------------------------------------------------ |
| `grant_type`    | string | Yes      | Must be `refresh_token`                                      |
| `refresh_token` | string | Yes      | The refresh token obtained during the initial token exchange |
| `client_id`     | string | Yes      | The client ID obtained during registration                   |
| `client_secret` | string | Yes      | The client secret obtained during registration               |

### Response

The response format is identical to the initial token exchange response, providing a new access token and potentially a new refresh token.

## Security Best Practices

### Client Secret Management

* Never expose the client secret in client-side code
* Store credentials securely using environment variables or secure key management systems

### Token Handling

* Store tokens securely (use secure storage on mobile, httpOnly cookies for web)
* Implement token refresh logic before expiration
* Never log or expose tokens in error messages

### State Parameter

* Always use the state parameter to prevent CSRF attacks
* Generate a unique, random state value for each authorization request
* Verify the state parameter matches when handling the callback

## Error Handling

### OAuth Error Response Format

```json
{
    "error": "invalid_request",
    "error_description": "The request is missing a required parameter",
    "error_uri": "https://mcp.scalev.id/docs/errors#invalid_request"
}
```

### Common Error Codes

| Error Code               | Description                                                   |
| ------------------------ | ------------------------------------------------------------- |
| `invalid_request`        | The request is missing a required parameter or is malformed   |
| `invalid_client`         | Client authentication failed                                  |
| `invalid_grant`          | The authorization code or refresh token is invalid or expired |
| `unauthorized_client`    | The client is not authorized to use this grant type           |
| `unsupported_grant_type` | The grant type is not supported                               |
| `invalid_scope`          | The requested scope is invalid or exceeds granted scope       |

## Token Lifecycle Management

### Access Token Expiration

* Default expiration: 3600 seconds (1 hour)
* Monitor the `expires_in` value from the token response
* Implement preemptive refresh (e.g., refresh when 80% of lifetime has passed)

### Refresh Token Rotation

* Some implementations rotate refresh tokens on each use
* Always store the latest refresh token
* Handle cases where refresh tokens may expire

### Example Token Refresh Implementation

```javascript
async function ensureValidToken(tokenData) {
    const now = Date.now() / 1000;
    const expiresAt = tokenData.issued_at + tokenData.expires_in;
    
    // Refresh if token expires in less than 5 minutes
    if (expiresAt - now < 300) {
        return await refreshAccessToken(tokenData.refresh_token);
    }
    
    return tokenData;
}
```

<br />
