# Documentation-Digester

## About

⚠️ TODO ⚠️

## Local Setup Steps

### Frontend Setup

Make sure you have [Node.js](https://nodejs.org/en/download) installed first. Then run the following in your terminal:

```bash
cd frontend
npm i
npm start
```

### Backend Setup

Make sure you have [Ollama](https://ollama.com/download) installed first. Then run the following in your terminal:

```bash
ollama serve
```

While keeping the first terminal open, run the following in a separate terminal:

```bash
ollama pull nomic-embed-text:latest
ollama pull qwen2.5:1.5b
```

> [!NOTE]
>
> <details>
>
> <summary><strong>How to use different models</strong></summary>
>
> These are just the models that have worked best for us. They are relatively small and pretty fast, even on older hardware. They might not be as smart, but they are still good for testing. If you'd like to use different models, pull them from Ollama, and make a new `./backend/.env` file with the following:
>
> ```env
> OLLAMA_LLM_MODEL=qwen2.5:1.5b
> OLLAMA_EMBEDDING_MODEL=nomic-embed-text:latest
> ```
>
> </details>

Once the previous commands have finished, run the following in the second terminal whilst still keeping the first terminal running:

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
> The Python dependencies resolve just fine on Windows, Linux, and Apple Silicon Macs. Intel Macs aren't compatible for some reason. A (not-so-ideal) workaround is to run the backend in a Docker container. The first step is to create a new environment file at `./backend/.env` with the following:
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
> If your linter isn't picking up the installed dependencies properly in VS Code, try opening up the `backend` folder directly instead of the project root.
