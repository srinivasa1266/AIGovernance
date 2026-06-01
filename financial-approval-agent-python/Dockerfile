# ── Stage 1: install dependencies ─────────────────────────────────────────
FROM python:3.12-slim AS deps

WORKDIR /app

# Install deps first (layer cache — only re-runs if requirements.txt changes)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# ── Stage 2: production image ──────────────────────────────────────────────
FROM python:3.12-slim AS runner

WORKDIR /app

# Non-root user for security
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Copy installed packages from deps stage
COPY --from=deps /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin

# Copy application source
COPY src/    ./src/
COPY public/ ./public/
COPY main.py ./

RUN chown -R appuser:appgroup /app
USER appuser

ENV PORT=3000
ENV PYTHONUNBUFFERED=1

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:3000/api/health')" || exit 1

CMD ["python", "main.py"]
