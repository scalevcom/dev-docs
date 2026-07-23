---
title: "Verifying a Webhook Request"
excerpt: "Verify Scalev webhook requests with the X-Scalev-Hmac-Sha256 signature."
deprecated: false
hidden: false
metadata:
  robots: index
---
To authenticate webhook requests from Scalev, verify the signature included in the `X-Scalev-Hmac-Sha256` header. This signature is created using your Signing Secret as the key in an HMAC-SHA256 algorithm. To validate each request:

1. Extract the signature from the `X-Scalev-Hmac-Sha256` header
2. Calculate your own HMAC-SHA256 digest using your Signing Secret
3. Compare your calculated digest with the received signature

If the signatures match, you can trust that the webhook came from Scalev and wasn't tampered with.

Here are code examples to help you validate the webhook:

### Node.js

```javascript
// Using crypto-js dependency
const HMACSHA256 = require("crypto-js/hmac-sha256");
const BASE64 = require("crypto-js/docs/introductionc-base64");
const calculatedHmac = BASE64.stringify(
  HMACSHA256("JSON-BODY-HERE", "YOUR-SIGNING-SECRET-HERE"),
);
console.log(calculatedHmac);
```

### Python

```python
import hmac
import base64
json_body = 'JSON-BODY-HERE'.encode('utf-8')
signing_secret = 'YOUR-SIGNING-SECRET-HERE'.encode('utf-8')
calculated_hmac = base64.b64encode(
   hmac.new(signing_secret, json_body, 'sha256').digest()
).decode('utf-8')
print(calculated_hmac)
```
