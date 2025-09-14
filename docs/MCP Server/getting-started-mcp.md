---
title: Getting Started
excerpt: This page outlines how to get started using Scalev MCP.
deprecated: false
hidden: false
metadata:
  robots: index
---
This guide will walk you through connecting your AI assistant to the Scalev MCP server and making your first API call through MCP.

## Prerequisites

Before you begin, ensure you have:

1. **A Scalev Account**
2. **An OAuth Access Token or API Key**
   * Follow our guides on authorization, namely <Anchor label="Authorization with OAuth" target="_blank" href="https://developers.scalev.id/docs/authorization">Authorization with OAuth</Anchor> or <Anchor label="Authentication with API Key" target="_blank" href="https://developers.scalev.id/docs/authentication-with-api-key">Authentication with API Key</Anchor>. You can use either of those as bearer token to call the MCP server.
3. **An MCP-Compatible AI Assistant** such as:
   * Claude Desktop App
   * Custom AI application with MCP client support
   * Any LLM framework that supports MCP protocol

## MCP Server Endpoints

The Scalev MCP server provides two endpoints for different connection methods:

| Endpoint         | URL                         | Protocol                          | Use Case                                                      |
| ---------------- | --------------------------- | --------------------------------- | ------------------------------------------------------------- |
| **Standard MCP** | `https://mcp.scalev.id/mcp` | Streaming HTTP (current standard) | Modern MCP clients, recommended for new integrations          |
| **SSE**          | `https://mcp.scalev.id/sse` | Server-Sent Events (legacy)       | Compatibility with older clients or SSE-based implementations |

Choose the endpoint based on your client's capabilities. The `/mcp` endpoint with Streaming HTTP is recommended for better performance and reliability.

## Configuration Examples

### Claude Desktop App

Edit your Claude configuration file (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "scalev": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://mcp.scalev.id/sse",
        "--header",
        "Authorization: Bearer ${ACCESS_TOKEN}"
      ],
      "env": {
        "ACCESS_TOKEN": "..."
      }
    }
  }
}
```

#### TypeScript Example with Types

```typescript
import OpenAI from "openai";
import dotenv from "dotenv";

dotenv.config();

interface MCPTool {
  type: "mcp";
  server_label: string;
  server_url: string;
  headers: {
    Authorization: string;
  };
  allowed_tools?: string[];
  require_approval?: "never" | "always" | "auto";
}

const ACCESS_TOKEN: string = "API_KEY_OR_OAUTH_ACCESS_TOKEN";
const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

async function queryScalev(prompt: string, allowedTools?: string[]): Promise<string> {
  const response = await openai.responses.create({
    model: "gpt-4.1",
    input: prompt,
    tools: [
      {
        type: "mcp",
        server_label: "scalev",
        server_url: "https://mcp.scalev.id/mcp",
        headers: {
          Authorization: `Bearer ${ACCESS_TOKEN}`,
        },
        allowed_tools: allowedTools,
        require_approval: "never",
      } as MCPTool,
    ],
  });

  return response.output_text;
}

// Example usage
const result = await queryScalev(
  "List my latest 3 orders on Scalev",
  ["list_order"]
);
console.log(result);
```

## Verify Your Connection

Once configured, verify that your AI assistant can connect to the MCP server:

### Test 1: List Available Tools

Ask your AI assistant:

```
"What Scalev tools are available to you?"
```

The assistant should respond with a list of all Scalev API endpoints available as tools.

### Test 2: Simple API Call

Try a basic operation:

```
"Can you check my 3 latest orders on Scalev?"
```

This should trigger the AI to use the appropriate Scalev API endpoint through MCP.

## Available Tools

Once connected, your AI assistant will have access to all Scalev API endpoints as MCP tools. The tools are organized into the following categories:

* **Bundles Management** - Bundle creation, pricing options, and partner associations
* **Orders & Transactions** - Order processing, payments, shipments, and analytics
* **Products Catalog** - Product management, variants, and digital files
* **Stores Configuration** - Store setup, payment methods, and courier services
* **Shipping & Logistics** - Shipping cost calculations and warehouse management
* **Business Settings** - E-payment methods and location management

For a complete list of all available tools and their parameters, see the [List of Available Tools](https://developers.scalev.id/docs/list-of-available-tools) page or visit the [scalev-mcp npm package documentation](https://www.npmjs.com/package/scalev-mcp).

## Example Workflow

Here's how an AI assistant might use the MCP server:

```
User: "Show me my 10 latest orders on Scalev and their current status"

AI Assistant (via MCP):
1. Calls the /order endpoint tool
2. Retrieves order details
3. Formats and presents the information

User: "Update the order status for Order #250101QWERTY to confirmed"

AI Assistant (via MCP):
1. Calls the /order/{id} endpoint tool with PATCH method
2. Updates the order status
3. Confirms the successful update
```

## Troubleshooting

### Connection Issues

| Problem              | Solution                                                  |
| -------------------- | --------------------------------------------------------- |
| "Unauthorized" error | Verify your access token is valid and not expired         |
| "Connection refused" | Check the MCP endpoint URL is correct                     |
| SSE connection drops | Implement reconnection logic with exponential backoff     |
| Tools not appearing  | Ensure proper Authorization header format: `Bearer TOKEN` |

### Debugging Tips

1. **Test with curl first** to isolate connection issues:
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" \
        https://mcp.scalev.id/mcp/tools
   ```

2. **Enable verbose logging** in your MCP client to see detailed request/response

3. **Monitor token expiration** and ensure refresh is working properly

4. **Check network connectivity** and firewall rules if connection fails

## Best Practices

### 1. Rate Limiting

Respect API rate limits:

* Implement exponential backoff for retries
* Cache responses when appropriate
* Batch operations where possible

### 2. Security

* Never expose access tokens in client-side code
* Use environment variables for sensitive data
* Implement proper token storage and rotation

<br />
