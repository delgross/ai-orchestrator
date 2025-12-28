---
description: Graph Visualization Workflow
---
# Graph Visualization Implementation
This workflow describes how to implement the visualization of the Knowledge Graph using the newly created backend.

## 1. Backend API (Completed)
- `/ingest/graph` - Accepts Entities and Relations.
- `/stats` - Returns graph metrics (node/edge counts).

## 2. Frontend Visualization (Next Step)
To visualize the graph in the Dashboard (`dashboard/v2/chat_debug.html`):
1.  Add a new tab "Knowledge Graph".
2.  Use `force-graph` (2D or 3D) via CDN.
3.  Fetch data from `/stats` (or a new `/graph/snapshot` endpoint) to populate nodes/links.
4.  Render the graph with:
    - Nodes: Entities (Color by `type`)
    - Links: Relations (Label with `relation`)
    - Interaction: Click node to see `metadata/description`.

## 3. External Visualization
- Connect **Surrealist.app** to `ws://localhost:8000/rpc`
- Namespace: `orchestrator`, Database: `knowledge`
- Use the "Explore" or "Graph" view in Surrealist.
