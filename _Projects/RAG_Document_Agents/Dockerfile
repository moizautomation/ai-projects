# Hugging Face Spaces (Docker SDK) requires the app to listen on port 7860
# and run as a non-root user with write access to its own home directory.

FROM python:3.11-slim

# System dependencies some of your packages (faiss, torch) may need at build time
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user, since HF Spaces containers run as this user by default
RUN useradd -m -u 1000 appuser
USER appuser
ENV PATH="/home/appuser/.local/bin:$PATH"

WORKDIR /app

# Install dependencies first (better Docker layer caching — code changes
# won't force a full reinstall of torch etc. every time)
COPY --chown=appuser requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Cache directories for the cross-encoder model + HF downloads need to be
# writable — point them at a folder appuser actually owns
ENV HF_HOME=/app/hf_cache
ENV TRANSFORMERS_CACHE=/app/hf_cache
RUN mkdir -p /app/hf_cache

# Copy the rest of the app
COPY --chown=appuser . .

# HF Spaces routes traffic to port 7860 specifically
EXPOSE 7860

CMD ["uvicorn", "ragagent:app", "--host", "0.0.0.0", "--port", "7860"]
