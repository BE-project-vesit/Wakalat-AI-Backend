# MCP HTTP Integration Frontend Guide

## Goals

- Provide a lightweight, reusable frontend setup for consuming the Wakalat-AI HTTP MCP server
- Support both REST-based and WebSocket-based tool interaction for a plug-and-play developer experience

## Recommended Stack

- Framework: `React` or any SPA-friendly toolkit (Next.js, Vite React, SvelteKit)
- HTTP: `fetch` or `axios` for REST endpoints (`/health`, `/tools`, `/tools/execute`, `/resources`, `/prompts`)
- WebSocket: Native `WebSocket` API or abstraction (e.g., `socket.io-client` if reconnection helpers are desired)
- State management: lightweight solutions (`React Query`, `Zustand`) to cache tool catalogs and responses
- Serialization: Ensure JSON serialization/deserialization of tool arguments/results matches the server schemas
- Authentication: If you introduce auth, wrap requests with your token/session handling; current server assumes open access

## Integration Steps

1. **Fetch Server Metadata**
   - Call `GET /health` for readiness checks and version info
   - Call `GET /` to discover available endpoints dynamically

2. **Load Catalogs**
   - `GET /tools` → populate UI for tool selection, show `inputSchema`
   - `GET /resources` and `GET /resources/{uri}` → expose reference material
   - `GET /prompts` and `GET /prompts/{name}` → list reusable prompt templates

3. **Execute Tools**
   - REST: POST to `/tools/execute` with the chosen tool name and arguments matching its `inputSchema`
   - WebSocket: Open `ws://<host>/ws`, send `{ "type": "tool_call", "name": "tool_name", "arguments": { ... } }`, listen for `tool_response`

4. **Handle Responses**
   - REST: parse `ToolResponse` (`success`, `result`, `error`)
   - WebSocket: handle `tool_response`, `tools_list`, and error payloads

5. **Optional Enhancements**
   - Auto-refresh tool/resource catalogs at startup or on interval
   - Graceful WebSocket reconnection logic
   - UI components for argument builders based on `inputSchema`

## Plug-and-Play Tips

- Centralize server URL in configuration; allow swapping between local and production servers
- Use shared TypeScript interfaces mirroring `Tool`, `ToolCall`, `ToolResponse`, resource, and prompt shapes for compile-time safety
- Provide a generic executor utility that switches between REST and WebSocket transports to keep UI components transport-agnostic
- Wrap WebSocket events in an event emitter or observable for easy consumption across the app

With these pieces, the frontend can drop-in connect to the HTTP MCP server, leverage standardized tool metadata, and deliver the "plug-and-play" MCP experience on the web.

