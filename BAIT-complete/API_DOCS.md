# BAIT PRO ULTIMATE - API Documentation

## Base URL
`http://localhost:8000/api/ultimate`

## 1. Voice Control
### Start Voice Control
`POST /voice/start`
- **Body**: `{"provider": "google"}` (google, whisper, sphinx)
- **Response**: `{"status": "started"}`

### Stop Voice Control
`POST /voice/stop`
- **Response**: `{"status": "stopped"}`

---

## 2. Vision & Camera
### Analyze Screen
`GET /vision/analyze-screen`
- **Response**:
```json
{
  "text_length": 150,
  "errors_detected": ["SyntaxError line 5"],
  "has_code": true,
  "language": "python"
}
```

### Camera Status
`GET /vision/camera-status`
- **Response**:
```json
{
  "is_active": true,
  "face_detected": true,
  "gesture": "thumbs_up"
}
```

---

## 3. Memory System
### Store Memory
`POST /memory/store`
- **Body**:
```json
{
  "content": "User likes dark mode",
  "memory_type": "preference",
  "importance": 8
}
```

### Recall Memory
`POST /memory/recall`
- **Body**: `{"query": "dark mode", "limit": 5}`

---

## 4. Automation & Workflows
### Create Workflow
`POST /workflow/create`
- **Body**: `{"description": "Every day at 9am open gmail"}`
- **Response**: `{"workflow_id": "uuid", "workflow": {...}}`

### List Workflows
`GET /workflow/list`

### Execute Workflow
`POST /workflow/execute`
- **Body**: `{"workflow_id": "uuid"}`

---

## 5. Browser Agent
### Search Google
`POST /browser/search`
- **Body**: `{"query": "latest AI news"}`
- **Response**: `{"results": [{"title": "...", "link": "..."}]}`

### Scrape Page
`POST /browser/scrape`
- **Body**: `{"url": "https://example.com"}`

---

## 6. Desktop Control
### List Windows
`GET /desktop/windows`

### Execute Command
`POST /desktop/command`
- **Body**:
```json
{
  "type": "window_maximize",
  "params": {"title": "Chrome"}
}
```

---

## 7. File Manager
### Search Files
`POST /files/search`
- **Body**: `{"query": "report", "directory": "C:/Docs"}`

### Organize Directory
`POST /files/organize`
- **Body**: `{"directory": "C:/Downloads", "method": "type"}`

### Find Duplicates
`GET /files/duplicates/{directory}`

---

## 8. AI Avatar
### Generate Lip Sync
`POST /avatar/lip-sync`
- **Body**: `{"audio_path": "path/to/audio.wav"}`

### Set Expression
`POST /avatar/expression`
- **Body**: `{"expression": "happy"}`

---

## 9. API Integrations
### Health Check
`GET /health`
- **Response**: `{"modules_available": true, "active_modules": [...]}`

---

## Error Handling
All endpoints return standard HTTP status codes:
- `200`: Success
- `400`: Bad Request
- `500`: Internal Server Error
- `501`: Module Not Available (check dependencies)
