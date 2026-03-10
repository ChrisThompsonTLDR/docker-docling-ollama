# docker-docling-ollama

Docling PDF extraction with Ollama API for picture description (alt-text). CPU-only.

Used by [eyejay](https://github.com/ChrisThompsonTLDR/eyejay) for RunPod and local Docker.

## Build

```bash
docker build -t ghcr.io/christhompsontldr/docker-docling-ollama:latest .
```

## Publish

Push to `main`; GitHub Actions builds and pushes to ghcr.io. Then make the package public: GitHub → Your profile → **Packages** → `docker-docling-ollama` → Package settings → **Change visibility** → Public
