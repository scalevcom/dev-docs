---
title: Introduction
excerpt: This page outlines Scalev MCP server.
deprecated: false
hidden: false
metadata:
  robots: index
---
The Model Context Protocol (MCP) server on Scalev provides a seamless bridge between AI assistants and the Scalev API ecosystem. It acts as a mirror to the [Scalev OpenAPI specification](https://api.scalev.id/v2/openapi), automatically exposing all API endpoints as ready-to-use tools that AI models can leverage to perform actions on behalf of users.

## What is MCP?

MCP (Model Context Protocol) is a protocol that enables AI assistants to interact with external systems through a standardized interface. By connecting to an MCP server, AI assistants gain the ability to:

* Access real-time data or execute actions on external APIs
* Maintain context across multiple operations
* Provide more comprehensive and actionable responses

## How Scalev's MCP Server Works

The Scalev MCP server transforms every endpoint from the Scalev OpenAPI specification into an MCP-compatible tool. This means:

* **Complete API Coverage**: Every endpoint available in the Scalev API is automatically available as an MCP tool
* **Real-time Synchronization**: Any updates to the Scalev API are immediately reflected in the MCP server
* **Type-safe Operations**: All tools maintain the same request/response schemas as defined in the OpenAPI specification

## Key Features

### 1. Full API Parity

The MCP server provides access to all Scalev REST API operations. Note: For optimal AI agent performance, we recommend whitelisting only the specific tools your application requires, as this helps prevent context overload and ensures more focused, efficient responses from the AI.

### 2. Authentication via API Key or Scalev OAuth 2.1

The MCP server uses the same authentication as the API. Use either API key or access token from OAuth 2.1 flow. No need for separate process.

### 3. Seamless AI Integration

AI assistants can directly:

* Query Scalev resources using natural language
* Provide intelligent suggestions based on Scalev data
* Automate repetitive tasks

## Use Cases

### For Developers

* Build AI-powered applications that interact with Scalev
* Create intelligent automation workflows
* Develop conversational interfaces for Scalev operations

### For End Users

* Use AI assistants to manage Scalev resources through natural conversation
* Get intelligent insights from Scalev data
* Automate complex multi-step processes without writing code

## Getting Started

To connect an AI assistant to the Scalev MCP server:

1. **Authenticate**: Either get API key or get access token from your users via OAuth authorization flow.
2. **Connect**: Configure your AI assistant with the MCP server endpoint.
3. **Start Using**: The AI assistant can now access all Scalev API endpoints as tools.

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

<br />
