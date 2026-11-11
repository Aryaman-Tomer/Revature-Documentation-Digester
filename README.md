# Documentation-Digester

## Todo

- [ ] Restructure the project files.
- [ ] Dockerize the entire repo (including frontend and Ollama).

## About

This repository holds the final project for our Revature Java Full Stack Engineering training. This is a simple RAG application that integrates a FastAPI backend, an Angular frontend, a Chroma vector database, and a local Ollama server.

### Features

- Document uploading.
- Different chunking strategies (by character count or by semantic meaning).

### Limitations

- No conversational history.
- The LLM doesn't have access to the internet.

## Local Development Setup

### Frontend Setup

Make sure you have [Node.js](https://nodejs.org/en/download) installed first. Then run the following in your terminal:

```bash
cd frontend
npm i
npm start
```

### Backend Setup

Make sure you have [uv](https://docs.astral.sh/uv/getting-started/installation/) installed first. Then run the following in your terminal:

```bash
cd backend
uv run start
```

> [!IMPORTANT]
>
> <details>
>
> <summary><strong>If you have an Intel-based Mac</strong></summary>
>
> The Python dependencies resolve just fine on Windows, Linux, and Apple Silicon Macs. Intel-based Macs aren't compatible for some reason. A (not-so-ideal) workaround is to run the backend in a Docker container. The first step is to create a new environment file at `./backend/.env` with the following:
>
> ```env
> OLLAMA_BASE_URL=http://host.docker.internal:11434
> ```
>
> Next, make sure your Docker daemon is running by opening the Docker app. Then run the following commands:
>
> ```bash
> cd backend
> docker compose up --build --watch
> ```
>
> </details>

> [!TIP]
> If your linter isn't picking up the installed dependencies properly in VS Code, try opening up the `backend` folder directly instead of the project root. (Unfortunately this trick still won't work for Intel-based Macs because you won't be able to install the dependencies in the first place.)

### Ollama Setup

Make sure you have [Ollama](https://ollama.com/download) installed first. Then run the following in your terminal:

```bash
ollama serve
```

While keeping the previous terminal open, run the following in a separate terminal:

```bash
ollama pull nomic-embed-text:latest
ollama pull qwen2.5:1.5b
```

Not that these are just the models that have worked best for us. They are relatively small and pretty fast, even on older hardware. They might not be as smart, but they are still good for testing. If you'd like to use different models, pull them from Ollama, and make a new `./backend/.env` file with the following structure:

```env
OLLAMA_LLM_MODEL=qwen2.5:1.5b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text:latest
```
