---
title: "Scalev MCP connector"
excerpt: "Connect supported AI assistants to Scalev businesses with OAuth-approved access."
deprecated: false
hidden: false
metadata:
  robots: index
---
Scalev MCP lets AI assistants that support remote MCP connect to one or more Scalev businesses. Use it when you want an assistant to inspect business data, find available Scalev API v3 actions, or run approved business API requests through a permissioned OAuth connection.

The connector URL is:

```text
https://mcp.scalev.com/mcp
```

Do not paste Scalev API keys into an AI assistant. Use the MCP connector so Scalev can authenticate you with OAuth, show the requested permissions, and enforce access on every request.

## How it works

The flow is:

```text
AI assistant
  -> Scalev MCP connector
  -> Scalev API v3
```

When you connect an assistant, Scalev opens an OAuth approval flow. You sign in, choose one or more businesses, review the requested permissions, and approve access.

After approval, the assistant calls the Scalev MCP connector. The connector forwards the OAuth token to Scalev API v3. Scalev validates the token, resolves the user and the selected business for each business API request, checks scopes, and runs the requested API action.

You only need to enter the MCP connector URL. The assistant discovers the Scalev OAuth issuer at `https://api.scalev.com/v3/oauth`, then reads its metadata and opens the approval page at `https://app.scalev.com/oauth/authorize`.

Do not use `https://app.scalev.com/oauth/authorize` as the MCP connector URL. That URL is the browser approval page used during OAuth.

## Available tools

Scalev MCP exposes 25 tools:

- `get_me`: shows the connected user, OAuth app, businesses, and permission context.
- `get_docs`: reads Scalev Developers documentation bundled into MCP from every page under the Developers tab in the docs navigation when the assistant cannot browse `docs.scalev.com`. This is a local read-only lookup that does not call the Scalev API or change business data.
- `search`: finds business-authenticated Scalev API v3 endpoints that the assistant can ask to use.
- `get`: reads one GET endpoint returned by `search`.
- `execute_safe`: runs one non-destructive non-GET endpoint returned by `search`, such as create, update, validation, or status-change actions.
- `execute_destructive`: runs one destructive non-GET endpoint returned by `search`, such as delete, cancel, revoke, remove, or disconnect actions.
- `list_landing_pages`: lists business landing pages.
- `list_landing_page_tags`: lists landing page tags visible to the business.
- `get_landing_page`: reads one business landing page.
- `get_landing_page_public_view`: reads authenticated public rendering data for one landing page.
- `create_landing_page`: creates a landing page. For HTML Mode publishing in one call, include `is_published: true` with `page_display`.
- `update_landing_page`: updates landing page metadata or publish state.
- `update_landing_page_tags`: replaces tags assigned to one landing page.
- `delete_landing_page`: soft-deletes one landing page.
- `list_landing_page_displays`: lists saved display versions for one landing page.
- `create_landing_page_display`: creates a new display version with HTML/CSS/JS, analytics pixels, or checkout form data.
- `validate_landing_page_display`: validates a display payload without saving it.
- `get_landing_page_display`: reads one saved display version.
- `delete_landing_page_display`: deletes one saved display version.
- `list_orders`: lists business orders.
- `get_order`: reads one business order.
- `create_order`: creates one business order.
- `update_order`: updates one business order.
- `change_order_status`: changes order or payment status after explicit user intent.
- `get_order_statistics`: reads aggregated order statistics for the selected business.

This keeps a generic catalog surface while adding semantic tools for the full public Landing Pages operation set and the Orders workflows most useful during review. OAuth flow routes, dashboard-only routes, and storefront browser routes are not exposed through MCP.

`search` results can include `docs_topic`, `docs_url`, and `docs_hint`. When those fields are present, ask the assistant to call `get_docs` before creating a request payload or running a write action.

`search` returns `execution_tool` as `get`, `execute_safe`, or `execute_destructive`. Use that value. The connector refuses wrong-tool calls, so destructive operations cannot run through `execute_safe`, safe write actions cannot run through `execute_destructive`, and GET operations must use `get` or a read-only semantic tool.

`get_me` returns `connected_businesses[]`. If the connection includes more than one business, the assistant must pass `business_unique_id` on business-scoped tools. Top-level `business_unique_id` is preferred. If a client accidentally places the exact `business_unique_id` key in `body`, `query`, `query_params`, `header_params`, `headers`, or a concrete path query string, Scalev MCP recovers it and forwards it to Scalev as the business selector. If the connection includes one business, the assistant can omit it.

For write actions, the assistant can send endpoint fields directly or inside the `body` field. Scalev MCP forwards the resulting JSON body to Scalev API v3 unchanged.

Typical tasks include:

- showing the connected user, OAuth app, and businesses
- reading Scalev docs for the selected API area before making changes
- listing orders, products, bundles, customers, stores, or landing pages
- reading page, order, product, or WhatsApp account details
- validating or creating allowed business resources through Scalev API v3
- running any approved business-authenticated API action that appears in `search`, using `get` for GET endpoints and `execute_safe` or `execute_destructive` for non-GET endpoints

## Requirements

You need:

- a Scalev account with access to a business
- an AI assistant or MCP client that supports remote MCP servers with OAuth
- access to the Scalev MCP connector URL

Some AI assistants limit custom connectors by plan, workspace, or administrator setting. Check your AI assistant settings if you do not see an option to add a custom MCP server.

## Connect an AI assistant

1. Open the connector or tools settings in your AI assistant.
2. Add a custom MCP server or connector.
3. Enter `https://mcp.scalev.com/mcp` as the connector URL.
4. Continue to the Scalev OAuth approval screen.
5. Sign in to Scalev if prompted.
6. Choose the business or businesses you want the assistant to access.
7. Review the requested permissions.
8. Click **Authorize**.
9. Return to the AI assistant and test the connection.

Useful first prompts:

- "Show my Scalev business profile."
- "Read the Scalev docs for Landing Pages API, then search for the action to create a landing page."
- "Search for the Scalev endpoint to list landing pages."
- "Find the API action for reading an order, then show me the required fields."

## Use with ChatGPT

ChatGPT can connect to Scalev through a custom MCP connector when that feature is available for your account or workspace.

1. Make sure custom MCP connectors or developer mode are enabled for your ChatGPT account or workspace.
2. Create a custom MCP app or connector.
3. Use `https://mcp.scalev.com/mcp` as the MCP server URL.
4. Publish or enable the connector for the workspace if your plan requires admin review.
5. Connect Scalev and complete the Scalev OAuth approval flow.
6. In a new chat, select Scalev from the tools menu before asking it to work with your Scalev business.

ChatGPT may ask you to confirm write actions before they run. Review those confirmations before approving changes in Scalev.

Reference: [Apps in ChatGPT](https://help.openai.com/docs/introduction/articles/11487775-connectors-in-chatgpt) and [Building MCP servers for ChatGPT](https://platform.openai.com/docs/mcp/).

## Use with Claude

Claude supports remote MCP servers through custom connectors.

For individual Claude plans:

1. Open **Customize > Connectors** in Claude.
2. Click **+**.
3. Choose **Add custom connector**.
4. Enter `https://mcp.scalev.com/mcp` as the remote MCP server URL.
5. Click **Add**.
6. Click **Connect** and complete the Scalev OAuth approval flow.

For Claude Team and Enterprise workspaces:

1. Ask an Owner or Primary Owner to open **Organization settings > Connectors**.
2. Click **Add**.
3. Choose **Custom > Web**.
4. Enter `https://mcp.scalev.com/mcp` as the remote MCP server URL.
5. Click **Add**.
6. Each member can then open **Customize > Connectors**, find Scalev, and click **Connect**.

To use Scalev in a Claude conversation, open the **+** menu in the composer, choose **Connectors**, and enable Scalev for that chat.

Reference: [Claude custom connectors using remote MCP](https://support.claude.com/docs/introduction/articles/11175166-get-started-with-custom-connectors-using-remote-mcp).

## Use with Claude Code

Claude Code supports remote MCP servers over Streamable HTTP and handles the OAuth flow automatically.

1. Add the connector at the user scope so it loads across every project:

   ```bash
   claude mcp add --transport http --scope user scalev https://mcp.scalev.com/mcp
   ```

2. Verify it was registered:

   ```bash
   claude mcp list
   claude mcp get scalev
   ```

3. Start Claude Code and run the `/mcp` slash command.

4. Choose **scalev** from the MCP server list.

5. Choose **Authenticate**. Claude Code opens your browser for the Scalev OAuth approval flow. Sign in, choose the business or businesses you want the assistant to access, review the requested permissions, and approve.

6. Return to Claude Code after the browser flow finishes. The Scalev server should show as authenticated, and the Scalev tools appear in the `/mcp` panel. Tool names follow the `mcp__scalev__<tool>` pattern (for example, `mcp__scalev__list_landing_pages`).

If you want the connector available only for a specific project or to share its configuration with your team in version control, omit `--scope user` (local) or use `--scope project` to write the entry into a checked-in `.mcp.json`.

Reference: [Claude Code MCP documentation](https://docs.claude.com/docs/introduction/docs/claude-code/mcp).

## Use with Codex

The OpenAI Codex CLI supports remote MCP servers over Streamable HTTP natively. No bridge package is needed.

1. Register the connector. Either run:

   ```bash
   codex mcp add scalev --url https://mcp.scalev.com/mcp
   ```

   or add this block to `~/.codex/config.toml`:

   ```toml
   [mcp_servers.scalev]
   url = "https://mcp.scalev.com/mcp"
   ```

2. Trigger the Scalev OAuth flow:

   ```bash
   codex mcp login scalev
   ```

   Codex prints the Scalev authorization URL and listens on its OAuth callback port. Open the URL in a browser, sign in to Scalev, choose the business or businesses you want the assistant to access, review the requested permissions, and approve. Codex completes the token exchange when the callback returns.

3. Verify the connector and inspect its tools:

   ```bash
   codex mcp list
   codex mcp get scalev
   ```

   Inside the Codex TUI, the `/mcp` slash command lists the active MCP servers and their tools. `/mcp verbose` adds server diagnostics.

To disconnect later, run `codex mcp logout scalev`. To revoke from the Scalev side, follow the "Revoke access" steps below.

Reference: [Codex MCP documentation](https://developers.openai.com/codex/mcp).

## Use with OpenClaw

OpenClaw supports MCP servers but currently expects a static `Authorization` header for remote HTTP servers. Because Scalev uses OAuth Dynamic Client Registration rather than static API keys, connect Scalev through the `mcp-remote` bridge so the OAuth flow runs locally and the resulting tools are exposed to OpenClaw over stdio.

1. Register the bridge:

   ```bash
   openclaw mcp set scalev '{"command":"npx","args":["-y","mcp-remote","https://mcp.scalev.com/mcp"]}'
   ```

   You can also edit `openclaw.json` directly under `mcp.servers`:

   ```json
   {
     "scalev": {
       "command": "npx",
       "args": ["-y", "mcp-remote", "https://mcp.scalev.com/mcp"]
     }
   }
   ```

2. Verify the server is registered:

   ```bash
   openclaw mcp list
   openclaw mcp show scalev --json
   ```

3. Start a session that triggers Scalev. On first use, `mcp-remote` discovers the Scalev OAuth issuer, opens an authorization URL, and listens on the OAuth callback port. Open the printed URL in a browser if it does not open automatically, sign in to Scalev, choose the business or businesses you want the assistant to access, review the requested permissions, and approve. `mcp-remote` caches the resulting tokens under `~/.mcp-auth` and refreshes them automatically.

4. After approval, the Scalev tools appear in OpenClaw's tool list and are addressable from prompts.

Reference: [OpenClaw MCP CLI documentation](https://docs.openclaw.ai/cli/mcp) and [`mcp-remote` on npm](https://www.npmjs.com/package/mcp-remote).

## Use with Hermes Agent

Hermes Agent (Nous Research) supports MCP servers but currently documents only static `Authorization` headers for remote HTTP servers. Because Scalev uses OAuth Dynamic Client Registration rather than static API keys, connect Scalev through the `mcp-remote` bridge so the OAuth flow runs locally and the resulting tools are exposed to Hermes over stdio.

1. Add the bridge to `~/.hermes/config.yaml` under `mcp_servers`:

   ```yaml
   mcp_servers:
     scalev:
       command: npx
       args:
         - "-y"
         - "mcp-remote"
         - "https://mcp.scalev.com/mcp"
   ```

2. Reload the MCP servers in a running Hermes session:

   ```
   /reload-mcp
   ```

   Or start a fresh session:

   ```bash
   hermes chat
   ```

3. The first time Hermes calls a Scalev tool, `mcp-remote` discovers the Scalev OAuth issuer, opens an authorization URL, and listens on the OAuth callback port. Open the printed URL in a browser if it does not open automatically, sign in to Scalev, choose the business or businesses you want the assistant to access, review the requested permissions, and approve. `mcp-remote` caches the resulting tokens under `~/.mcp-auth` and refreshes them automatically.

4. Hermes registers each Scalev tool with the naming pattern `mcp_scalev_<tool>` (for example, `mcp_scalev_list_landing_pages`). Ask Hermes to use those tools directly in the conversation.

Reference: [Hermes Agent MCP documentation](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp) and [`mcp-remote` on npm](https://www.npmjs.com/package/mcp-remote).

## Permissions

The approval screen shows the permissions requested by the connector. Scalev only grants permissions that the official Scalev MCP connector is allowed to request.

The first connection may request the Scalev API v3 permissions supported by MCP so the assistant can discover and use the available business API actions. Dashboard-only permissions are not part of MCP approval.

Scalev enforces permissions on every API request. If the assistant tries to perform an action outside the approved scopes, Scalev rejects the request.

## Write actions

The `execute_safe` and `execute_destructive` tools can call non-GET Scalev API v3 endpoints when the connected OAuth token has the required scope. Some of those endpoints create, update, delete, validate, or run business actions. Review write actions in your AI assistant before you confirm them.

`execute_safe` is a non-destructive write or API action tool. It is not read-only or risk-free. Use it for operations whose `search` result says `execution_tool: "execute_safe"`.

`execute_destructive` is for destructive operations whose `search` result says `execution_tool: "execute_destructive"`.

The connector does not bypass Scalev authorization. Your Scalev business role, the approved OAuth scopes, and the target API endpoint still determine whether the action is allowed.

## Multiple businesses

A single OAuth connection can authorize multiple Scalev businesses when your user role permits app authorization in each business. Scalev tracks access separately for each business, and the assistant can use the same OAuth connection for the connected set.

Ask the assistant to call `get_me` first. The response includes active `connected_businesses[]` entries with each business `unique_id`, username, name, enabled state, and approved scopes.

When more than one business is connected, each business-scoped tool call must include `business_unique_id`. Use the `unique_id` from `connected_businesses[]`. Top-level `business_unique_id` is the canonical MCP input. For robustness, Scalev MCP also recovers this exact key from `body`, `query`, `query_params`, `header_params`, `headers`, or a concrete path query string, then strips it from the API payload/query before forwarding the request.

If access to one business is revoked or disabled, requests for that business fail, but the assistant can still use the remaining active connected businesses. Revoked businesses are omitted from `get_me`; if no active connected business remains, `get_me` returns `403` and the assistant must reconnect.

## Revoke access

You can revoke the connection at any time:

1. Open Scalev.
2. Go to **Settings > Apps**.
3. Find **Scalev MCP**.
4. Click **Revoke Access**.

After revocation, the assistant must reconnect and complete OAuth approval again before it can call that business through Scalev. If the same OAuth connection still has access to other businesses, those businesses can remain usable.

## Troubleshooting

### The assistant says authentication is required

Reconnect the Scalev MCP connector and complete the OAuth approval flow again.

### The assistant gets a forbidden or insufficient permission error

The connected business, your user role, or the approved scopes do not allow the requested action. Reconnect if you need to approve different scopes.

### The assistant cannot discover the connector

Check that the connector URL is exactly `https://mcp.scalev.com/mcp`. Your AI assistant must support remote MCP servers with OAuth.

If your assistant asks for an authorization server URL, use `https://api.scalev.com/v3/oauth`. If it asks for a connector or MCP server URL, use `https://mcp.scalev.com/mcp`.

### The assistant does not show any landing pages

Ask the assistant to call `get_me` and check `connected_businesses[]`. If more than one business is connected, make sure the assistant is using the correct `business_unique_id` and that the selected business has landing pages available to your user.

## Related docs

- [Authorization with OAuth](/docs/authorization-with-o-auth)
- [Authentication with API key](/docs/authentication-with-api-key)
- [Scalev API v3 introduction](/docs/introduction)
