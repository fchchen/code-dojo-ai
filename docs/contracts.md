# Code Dojo AI Service Contracts

## Auth

### `POST /api/auth/demo`
Request:
```json
{"username": "demo"}
```

Response:
```json
{"token":"jwt","username":"demo","expiresIn":3600}
```

## Submissions

### `POST /api/submissions`
Headers: `Authorization: Bearer <jwt>`

Request:
```json
{"code":"print('x')","language":"python"}
```

Response:
```json
{
  "id":"uuid",
  "username":"demo",
  "language":"python",
  "status":"complete",
  "result":{
    "summary":"...",
    "score":81,
    "issues":["..."],
    "improved_code":"...",
    "best_practices":["..."],
    "concept_explanation":"..."
  },
  "error":null,
  "created_at":"...",
  "updated_at":"..."
}
```

### `POST /api/submissions/stream`
Headers: `Authorization: Bearer <jwt>`

Request same as `POST /api/submissions`.

SSE Events:
- `submission.created`
- `agent.step`
- `submission.completed`
- `submission.failed`

### `GET /api/submissions/{id}`
### `GET /api/submissions?page=1&pageSize=20`

## Health

### `GET /api/health`
```json
{
  "status": "healthy",
  "services": {"coachAgent": "healthy", "mlAnalyzer": "healthy"},
  "timestamp": "2026-02-16T00:00:00Z"
}
```
