# Revature-Documentation-Digester

## Running locally

### Frontend

```bash
cd frontend
npm install
npm start
```

### Backend

```bash
cd backend
ollama serve
ollama pull nomic-embed-text:latest
ollama pull qwen2.5:1.5b
uv run start
```

docker compose up --watch