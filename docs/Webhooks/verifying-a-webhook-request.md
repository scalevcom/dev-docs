---
title: "Verifying a Webhook Request"
excerpt: "Verify Scalev webhook requests with the X-Scalev-Hmac-Sha256 signature."
deprecated: false
hidden: false
metadata:
  robots: index
---
To authenticate webhook requests from Scalev, verify the signature included in the `X-Scalev-Hmac-Sha256` header. Scalev creates this Base64 signature with your Signing Secret and HMAC-SHA256.

1. Read the request body as raw bytes. Do not parse and serialize the JSON first.
2. Read the signature from `X-Scalev-Hmac-Sha256`.
3. Calculate HMAC-SHA256 over the exact raw body bytes.
4. Decode the received Base64 signature and compare the two byte sequences in constant time.

Reject the request before processing it if the signatures do not match.

## Node.js

Register the raw-body route before `express.json()`:

```javascript
import crypto from "node:crypto";
import express from "express";

const app = express();
const signingSecret = process.env.SCALEV_WEBHOOK_SIGNING_SECRET;

function validScalevSignature(rawBody, signature) {
  if (!signingSecret || !signature) return false;

  const expected = crypto
    .createHmac("sha256", signingSecret)
    .update(rawBody)
    .digest();

  let received;
  try {
    received = Buffer.from(signature, "base64");
  } catch {
    return false;
  }

  return (
    received.length === expected.length &&
    crypto.timingSafeEqual(received, expected)
  );
}

app.post(
  "/webhooks/scalev",
  express.raw({ type: "application/json" }),
  (req, res) => {
    const signature = req.get("X-Scalev-Hmac-Sha256");

    if (!Buffer.isBuffer(req.body) || !validScalevSignature(req.body, signature)) {
      return res.sendStatus(401);
    }

    const event = JSON.parse(req.body.toString("utf8"));
    // Store the event durably before acknowledging it.
    return res.sendStatus(204);
  }
);

app.use(express.json());
```

## Python

```python
import hmac
import base64

raw_body = b"JSON-BODY-HERE"
signing_secret = b"YOUR-SIGNING-SECRET-HERE"
received_signature = "BASE64-SIGNATURE-HERE"

expected = hmac.new(signing_secret, raw_body, "sha256").digest()
received = base64.b64decode(received_signature, validate=True)

if not hmac.compare_digest(expected, received):
    raise ValueError("Invalid Scalev webhook signature")
```
