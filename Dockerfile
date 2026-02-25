FROM nvidia/cuda:12.1.1-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

RUN apt-get update && apt-get install -y \
    python3 python3-pip git ffmpeg libsndfile1 \
 && rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip

# Install CUDA Torch (matches cu121)
RUN pip3 install torch --index-url https://download.pytorch.org/whl/cu121

COPY requirements-server.txt .
RUN pip3 install -r requirements-server.txt

# ---- Prefetch Silero repo into torch hub cache (no runtime download) ----
RUN python3 -c "import torch; torch.hub.load('snakers4/silero-vad','silero_vad',trust_repo=True); print('Silero cached')"

COPY server.py .

EXPOSE 8000
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]