---
title: Introduction
excerpt: This document outlines the general overview of Scalev API.
hidden: false
---
Welcome to Scalev Docs. In this space, we will introduce how to interact with Scalev system so that you can utilize it in your own app or system. We currently provide endpoints for managing orders, products, and bundles. The API uses JSON for request and response payloads and implements role-based access control for security.

## Base URL

```
https://api.scalev.id/v2
```

## Authentication

The API uses token-based authentication. Include your authentication token in the Authorization header:

```
Authorization: Bearer YOUR_TOKEN_HERE
```

## Common Response Format

All API responses follow a consistent format:

### Success Response

```json
{
  "code": 200,
  "status": "Success",
  "data": {
    // Response data here
  }
}
```

### Error Response

```json
{
  "error": "Error message",
  "details": {
    "field_name": ["Validation error message"]
  }
}
```

## HTTP Status Codes

The API uses standard HTTP status codes:

* `200 OK` - Successful GET, PUT, PATCH requests
* `201 Created` - Successful POST requests
* `204 No Content` - Successful DELETE requests
* `400 Bad Request` - Invalid request format or parameters
* `401 Unauthorized` - Authentication required
* `403 Forbidden` - Insufficient permissions
* `404 Not Found` - Resource not found
* `422 Unprocessable Entity` - Validation errors
* `429 Too Many Requests` - Rate limit exceeded
* `500 Internal Server Error` - Server error

## Rate Limiting

API requests are subject to rate limiting:

* **All endpoints**: 30 requests per 5 seconds per IP

Rate limit information is included in response headers:

* `X-Ratelimit-Limit`: Request limit
* `X-Ratelimit-Remaining`: Remaining requests
* `X-Ratelimit-Reset`: Reset timestamp

## Pagination

For cursor-based paginated responses, the `data` field contains:

* `results`: Array of items in the current page
* `has_next`: Boolean indicating if there are more pages
* `last_id`: ID of the last item in the current page (for cursor-based pagination)
* `page_size`: Number of items per page

```json
{
  "code": 200,
  "status": "Success",
  "data": {
    "results": [
      // Array of items
    ],
    "has_next": true,
    "last_id": 123,
    "page_size": 25
  }
}
```

For standard paginated responses, the `data` field contains:

* `results`: Array of items in the current page
* `has_next`: Boolean indicating if there are more pages
* `page`: Current page number
* `page_size`: Number of items per page

```json
{
  "code": 200,
  "status": "Success",
  "data": {
    "results": [
      // Array of items
    ],
    "has_next": true,
    "page": 1,
    "page_size": 25
  }
}
```

## Support

If you encounter any issues, please visit the Discussions or contact our support team at [tech@scalev.id](mailto:tech@scalev.id).

***

This documentation is subject to change as the Scalev API evolves. For the most up-to-date information, please refer to our developer portal.