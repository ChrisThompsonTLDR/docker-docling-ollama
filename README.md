# docker-docling-ollama

Docling PDF extraction with Ollama API for picture description (alt-text). CPU-only.

Used by [eyejay](https://github.com/ChrisThompsonTLDR/eyejay) for RunPod and local Docker.

## Build

```bash
docker build -t ghcr.io/christhompsontldr/docker-docling-ollama:latest .
```

## Publish

Push to `main`; GitHub Actions builds and pushes to ghcr.io.

**If you get `permission_denied: write_package`:** Repo Settings → Actions → General → Workflow permissions → set **Read and write permissions**, then re-run the workflow.

After first successful push, make the package public: GitHub → Your profile → **Packages** → `docker-docling-ollama` → Package settings → **Change visibility** → Public
