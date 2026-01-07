# fabric-perf-test-repo
This repo generates 300 notebooks in your Fabric workspace

This was generate using the [Fabric MCP Server](https://marketplace.visualstudio.com/items?itemName=fabric.vscode-fabric-mcp-server&ssr=false#overview)

To execute the generation process, run:
```
python3 scripts/upload_items_to_fabric.py \\
  --endpoint https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/items \\
  --src generated_items \\
  --concurrency 8 \\
  --retries 3 \\
  --batch-size 50 \\
  --sleep-after 60 \\
  --token <YOUR_TOKEN> \\
```

Read about [Fabric Create Item API](https://learn.microsoft.com/en-us/rest/api/fabric/core/items/create-item?tabs=HTTP)