# Streamlit app image for Kiniela Predictor.
# Build: docker build -t kiniela-predictor .
# Run:   docker run --rm -p 8501:8501 kiniela-predictor
FROM python:3.12-slim

# No .pyc files, unbuffered logs (visible in `docker logs`), no pip cache in the image
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    PORT=8501

# LightGBM needs the OpenMP runtime, which the slim image does not include
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Dependencies first, so this layer is cached while only the code changes
COPY requirements.txt .
# XGBoost pulls NVIDIA NCCL (~345 MB) for multi-GPU training; the app predicts on CPU only.
# The package name follows the CUDA version (cu12, cu13…), so match any nvidia-nccl-*
RUN pip install -r requirements.txt \
    && pip freeze | grep -i '^nvidia-nccl' | cut -d= -f1 | xargs -r pip uninstall -y

COPY src ./src
COPY app ./app
# Promoted model, if any; .dockerignore lets in only the model file and its model card
COPY models ./models

# Run as an unprivileged user instead of root
RUN useradd --create-home --uid 1000 appuser
USER appuser

EXPOSE 8501

# Streamlit exposes /_stcore/health; urllib avoids installing curl in the image
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://localhost:{os.environ[\"PORT\"]}/_stcore/health', timeout=4)"

# sh -c expands $PORT (cloud hosts such as Render inject their own port), and exec makes
# Streamlit PID 1 so it receives the stop signal from `docker stop`
CMD ["sh", "-c", "exec streamlit run app/streamlit_app.py --server.address=0.0.0.0 --server.port=${PORT} --server.headless=true"]
