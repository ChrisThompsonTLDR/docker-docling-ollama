# docker-docling-ollama

Docling PDF extraction with Ollama API for picture description. CPU-only. FastAPI service that converts PDFs to DoclingDocument and exports JSON and Markdown. RunPod-friendly.

## API

- **POST /extract** – JSON body `{filename, document_id}`. Expects PDF at `DATA_DIR/filename`, returns `docling_document`, `docling_markdown`, and `docling_images`.
- **GET /health** – Health check.

## Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `DOCLING_DATA_DIR` | `/workspace` | Directory containing PDFs (mount volume here) |
| `DOCLING_OLLAMA_BASE_URL` | `http://ollama:11434` | Ollama API URL for picture description |
| `DOCLING_OLLAMA_MODEL` | `qwen3.5:397b-cloud` | Model for VLM alt-text |
| `DOCLING_OLLAMA_DO_PICTURE_DESCRIPTION` | `true` | Enable picture/table description via Ollama |

## Build

```bash
docker build --platform linux/amd64 -t ghcr.io/christhompsontldr/docker-docling-ollama:latest .
```

## Run (local, with Ollama)

```bash
docker run -p 8000:8000 \
  -v /path/to/pdfs:/workspace:ro \
  -e DOCLING_OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  ghcr.io/christhompsontldr/docker-docling-ollama:latest
```

## GitHub Actions

Build and push to ghcr.io on push to main. Same workflow as docker-docling.

## License

MIT
