# Revature-Documentation-Digester

## Running locally

### Frontend

```bash
cd frontend
# Todo
```

### Backend

You need to open up **two** terminals. In the first terminal, run these commands:

```bash
ollama serve
ollama pull nomic-embed-text:latest
ollama pull qwen2.5:1.5b
```

In the second terminal, run these commands:

```bash
cd backend
uv run start
```
