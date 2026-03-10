# docker-docling-ollama

Docling PDF extraction with Ollama API for picture description (alt-text). CPU-only.

Used by [eyejay](https://github.com/ChrisThompsonTLDR/eyejay) for RunPod and local Docker.

## Build

```bash
docker build -t ghcr.io/christhompsontldr/docker-docling-ollama:latest .
```

## Publish

1. Create a GitHub PAT with `write:packages` scope
2. Add repo secret: Settings → Secrets → Actions → `GHCR_TOKEN` = your PAT
3. Push to `main`; workflow builds and pushes to ghcr.io
4. Make package public: Your profile → Packages → `docker-docling-ollama` → Package settings → Change visibility → Public
