---
name: wrike-guide
description: Wrike operations via CLI. Replaces the 51-tool Wrike MCP with direct API calls. Use when the agent needs to interact with Wrike.
user-invocable: false
allowed-tools:
  - Bash
  - Read
---

# Wrike Guide — CLI Operations

The Wrike MCP has been replaced by direct API calls to save ~9K tokens of tool context. All operations use `curl` with the Wrike REST API.

## Auth

```bash
WRIKE_TOKEN="eyJ0dCI6InAiLCJhbGciOiJIUzI1NiIsInR2IjoiMiJ9.eyJkIjoie1wiYVwiOjY5MTk3NTIsXCJpXCI6OTY4ODYwOCxcImNcIjo0NzEwNDI0LFwidVwiOjIzMTE3NzUwLFwiclwiOlwiVVNcIixcInNcIjpbXCJXXCIsXCJGXCIsXCJJXCIsXCJVXCIsXCJLXCIsXCJDXCIsXCJEXCIsXCJNXCIsXCJBXCIsXCJMXCIsXCJQXCJdLFwielwiOltdLFwidFwiOjB9IiwiaWF0IjoxNzc0OTczNTMwfQ.0e5k3L-RUj10X58We7uKVBGsAUUYG2pDFwuFBHVUOG8"
WRIKE_API="https://www.wrike.com/api/v4"
```

## Common Operations

### List tasks in a folder
```bash
curl -s -H "Authorization: Bearer $WRIKE_TOKEN" "$WRIKE_API/folders/{folderId}/tasks?fields=[description]" | python3 -m json.tool
```

### Get a specific task
```bash
curl -s -H "Authorization: Bearer $WRIKE_TOKEN" "$WRIKE_API/tasks/{taskId}" | python3 -m json.tool
```

### Add a comment to a task
```bash
curl -s -X POST -H "Authorization: Bearer $WRIKE_TOKEN" -H "Content-Type: application/json" \
  -d '{"text":"Your comment here"}' \
  "$WRIKE_API/tasks/{taskId}/comments" | python3 -m json.tool
```

### Search tasks
```bash
curl -s -H "Authorization: Bearer $WRIKE_TOKEN" "$WRIKE_API/tasks?title=search+term" | python3 -m json.tool
```

### Get folder tree
```bash
curl -s -H "Authorization: Bearer $WRIKE_TOKEN" "$WRIKE_API/folders" | python3 -m json.tool
```

### Get spaces
```bash
curl -s -H "Authorization: Bearer $WRIKE_TOKEN" "$WRIKE_API/spaces" | python3 -m json.tool
```

### Get comments on a task
```bash
curl -s -H "Authorization: Bearer $WRIKE_TOKEN" "$WRIKE_API/tasks/{taskId}/comments" | python3 -m json.tool
```

## Guardrails

- **NEVER create new Wrike tasks.** Michael's board is executive-level only. Comment on existing ones.
- **NEVER delete Wrike tasks or folders.**
- Comments only on: AIC Related, Corporate Update, and other existing cards.
- See `reference_wrike_structure.md` for board layout.
