---
title: Authorization with OAuth 2.0
excerpt: >-
  This document outlines the authorization process for integrating with Scalev
  API.
deprecated: false
hidden: false
metadata:
  robots: index
---
## Overview

Scalev API uses the OAuth 2.0 Authorization Code flow with PKCE (Proof Key for Code Exchange), which provides a secure way for your application to obtain permission to access resources on behalf of a user. PKCE is mandatory for all applications to enhance security. The flow consists of these key steps:

0. Verifying your business
1. Registering your application with Scalev
2. Generating PKCE code verifier and challenge
3. Redirecting users to Scalev's authorization page
4. Users authorizing your application
5. Receiving an authorization code
6. Exchanging the code for access and refresh tokens (with PKCE verification)
7. Using the access token to make API requests
8. Refreshing the access token when it expires

## Step 0: Verify Your Business

To start using the Scalev API, you must first verify your business as a prerequisite before your application can access the necessary resources and perform actions on behalf of users. This is to ensure that each application is associated with a verified legal business entity, which helps maintain the integrity and security of the platform. To verify your business, go to [**Settings > Business**](https://app.scalev.id/setting/business) in your Scalev account and follow the instructions provided there.

## Step 1: Register Your Application

Before you can begin the OAuth flow, you need to register your application:

1. Log into your Scalev account
2. Navigate to [**Settings > Developers > Apps**](https://app.scalev.id/setting/developers/apps)
3. Click on "Create New App"
4. Fill out the information:
   * Application name
   * Description
   * Redirect URI (where users will be sent after authorization)
   * Requested scopes (permissions your app requires)
   * Whitelisted IP addresses (requests not from these IPs will be rejected)
   * Enable "Webhooks" if you want to receive webhook events
   * Webhook events (select the events you want to receive)
5. Submit the form to create your application
6. You will receive a **Client ID** and **Client Secret** - store these securely

> ⚠️ **Security Note**: Keep your Client Secret confidential. Never expose it in client-side code or public repositories.

## Step 2: Generate PKCE Parameters

Before initiating the authorization flow, you must generate PKCE parameters for enhanced security:

1. **Generate a Code Verifier**: Create a cryptographically random string of 43-128 characters using the characters `[A-Z] / [a-z] / [0-9] / "-" / "." / "_" / "~"`

2. **Create a Code Challenge**: Generate a Base64-URL-encoded SHA256 hash of the code verifier. **Important**: don't remove the padding when you encode the binary string as Scalev will compare the hash with padding included.

Here's how to generate these values:

**Code Verifier Example (JavaScript):**

```javascript
function generateCodeVerifier(length = 100) {
  if (!Number.isInteger(length) || length < 43 || length > 128) {
    throw new Error("Length must be an integer between 43 and 128.");
  }
  const charset =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~";
  const randomValues = crypto.getRandomValues(new Uint8Array(length));
  return Array.from(
    randomValues,
    (byte) => charset[byte % charset.length],
  ).join("");
}
```

**Code Challenge Example (JavaScript):**

```javascript
function base64UrlEncode(buffer) {
  return btoa(String.fromCharCode(...new Uint8Array(buffer)))
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/, '');
}

async function generateCodeChallenge(codeVerifier) {
  const encoder = new TextEncoder();
  const data = encoder.encode(codeVerifier);
  const digest = await crypto.subtle.digest("SHA-256", data);
  return base64UrlEncode(digest);
}
```

<Callout icon="💡" theme="default">
  ### **Note**: Store the code verifier securely on your client as you'll need it in Step 6 to exchange the authorization code for tokens.
</Callout>

## Step 3: Authorization Request

When a user wants to connect your application to their Scalev account, redirect them to Scalev's authorization endpoint with the following parameters:

```
https://app.scalev.id/oauth/authorize?
  client_id=YOUR_CLIENT_ID&
  redirect_uri=YOUR_REDIRECT_URI&
  response_type=code&
  state=RANDOM_STATE_STRING&
  code_challenge=CODE_CHALLENGE&
  code_challenge_method=S256
```

| Parameter               | Required | Description                                                                                                        |
| ----------------------- | -------- | ------------------------------------------------------------------------------------------------------------------ |
| `client_id`             | Yes      | The Client ID you received when registering your application                                                       |
| `redirect_uri`          | Yes      | The URI where users will be sent after authorization (must match one registered with your app)                     |
| `response_type`         | Yes      | Must be set to `code` for the Authorization Code flow                                                              |
| `state`                 | Yes      | A random string you generate to protect against CSRF attacks. You should validate this when receiving the callback |
| `code_challenge`        | Yes      | The Base64-URL-encoded SHA256 hash of your code verifier (generated in Step 2)                                     |
| `code_challenge_method` | Yes      | Must be set to `S256` (SHA256 hashing method)                                                                      |

## Step 4: User Authorization

At the authorization page, users will:

1. Log in to their Scalev account (if not already logged in)
2. See information about your application and the permissions you're requesting
3. Choose to approve or deny the authorization request

## Step 5: Receiving the Authorization Code

If the user approves your request, Scalev will redirect them back to your `redirect_uri` with the following parameters:

```
https://your-redirect-uri.com/callback?code=AUTHORIZATION_CODE&state=RANDOM_STATE_STRING
```

| Parameter | Description                                                                                |
| --------- | ------------------------------------------------------------------------------------------ |
| `code`    | The authorization code that you'll exchange for an access token; only valid for 10 minutes |
| `state`   | The same state parameter you provided in the authorization request                         |

Important security steps:

1. Verify that the `state` parameter matches the one you sent in the original request
2. Exchange the code for tokens promptly as authorization codes expire quickly

## Step 6: Exchanging the Code for Tokens

Make a POST request to Scalev's token endpoint to exchange your authorization code for tokens. You must include the code verifier for PKCE verification:

```
POST https://api.scalev.id/v2/oauth/token
Content-Type: application/json

{
  "grant_type": "authorization_code",
  "code": "AUTHORIZATION_CODE",
  "client_id": "YOUR_CLIENT_ID",
  "client_secret": "YOUR_CLIENT_SECRET",
  "code_verifier": "CODE_VERIFIER"
}
```

| Field           | Required | Description                                                               |
| --------------- | -------- | ------------------------------------------------------------------------- |
| `grant_type`    | Yes      | Must be set to `authorization_code`                                       |
| `code`          | Yes      | The authorization code received from the authorization server             |
| `client_id`     | Yes      | Your application's Client ID                                              |
| `client_secret` | Yes      | Your application's Client Secret                                          |
| `code_verifier` | Yes      | The original code verifier string generated in Step 2 (not the challenge) |

If successful, you'll receive a JSON response containing:

```json
{
  "access_token": "ACCESS_TOKEN",
  "refresh_token": "REFRESH_TOKEN",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

| Field           | Description                                                               |
| --------------- | ------------------------------------------------------------------------- |
| `access_token`  | Token to use for authenticating API requests                              |
| `refresh_token` | Token to use for obtaining new access tokens                              |
| `token_type`    | Always "Bearer"                                                           |
| `expires_in`    | Time until the access token expires, in seconds (typically 3600 = 1 hour) |

## Step 7: Using the Access Token

Use the access token to authenticate requests to Scalev API by including it in the Authorization header:

```
GET https://api.scalev.id/v2/some-endpoint
Authorization: Bearer ACCESS_TOKEN
```

## Step 8: Refreshing Access Tokens

Access tokens expire after 1 hour. When an access token expires, use the refresh token to obtain a new one without requiring user interaction:

```
POST https://api.scalev.id/v2/oauth/token
Content-Type: application/json

{
  "grant_type": "refresh_token",
  "refresh_token": "REFRESH_TOKEN",
  "client_id": "YOUR_CLIENT_ID",
  "client_secret": "client_secret"
}
```

The response will contain a new access token and refresh token:

```json
{
  "access_token": "NEW_ACCESS_TOKEN",
  "refresh_token": "NEW_REFRESH_TOKEN",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

> ⚠️ **Important**: Always update both your access token AND refresh token after a refresh operation. The old refresh token will be invalidated.

## Token Lifecycle and Security

* **Access Tokens**: Short-lived (1 hour) to limit potential damage if compromised
* **Refresh Tokens**: Longer-lived (30 days) but can be revoked
* **Token Storage**: Store tokens securely and never expose them to client-side code
* **Token Expiration**: Implement proper token refresh mechanisms to ensure uninterrupted service

## Revoking Access

If your app needs to revoke its access to a user's account, you can do so by making a request to the revocation endpoint:

```
POST https://api.scalev.id/v2/oauth/revoke
Content-Type: application/json

{
  "token": "TOKEN_TO_REVOKE",
  "token_type": "refresh_token",
  "client_id": "YOUR_CLIENT_ID",
  "client_secret": "YOUR_CLIENT_SECRET"
}
```

## Application Limits

We impose the following limits on OAuth applications to ensure fair usage and security:

1. 3 apps per business, currently this is a hard limit
2. 50 connected users per app, can be increased upon request after usage review

## Best Practices

1. **Generate cryptographically secure PKCE parameters** using proper random number generators
2. **Store the code verifier securely** and never expose it in URLs or logs
3. **Validate all redirect URI parameters** to prevent open redirect vulnerabilities
4. **Use the state parameter** to protect against CSRF attacks
5. **Store tokens securely**, never in local storage or cookies accessible by JavaScript
6. **Implement proper error handling** for all OAuth-related operations, including PKCE validation errors
7. **Be prepared for token refresh failures** and redirect users to re-authenticate when necessary
8. **Use different code verifiers for each authorization request** - never reuse them

## Error Handling

The OAuth endpoints may return various error responses. Common error codes include:

| Error                 | Description                                                           |
| --------------------- | --------------------------------------------------------------------- |
| `invalid_request`     | The request is missing a required parameter or is otherwise malformed |
| `invalid_client`      | Client authentication failed                                          |
| `invalid_grant`       | The authorization code or refresh token is invalid or expired         |
| `unauthorized_client` | The client is not authorized to use the requested grant type          |
| `invalid_request`     | PKCE verification failed (code_verifier doesn't match code_challenge) |
| `server_error`        | The server encountered an unexpected error                            |

### PKCE-Specific Errors

When PKCE validation fails, you may receive:

* `invalid_request` with description indicating PKCE parameter issues
* `invalid_grant` when the code verifier doesn't match the original code challenge

Always generate new PKCE parameters for retry attempts.
