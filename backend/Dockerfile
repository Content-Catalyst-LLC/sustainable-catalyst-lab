FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=10000

RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential \
      gfortran \
      golang-go \
      rustc \
      cargo \
      nodejs \
      npm \
    && npm install --global typescript \
    && rm -rf /var/lib/apt/lists/* /root/.npm

WORKDIR /app
COPY backend/requirements.txt /app/backend/requirements.txt
RUN python -m pip install --upgrade pip && python -m pip install -r /app/backend/requirements.txt

COPY backend /app/backend
ENV PYTHONPATH=/app/backend
WORKDIR /app/backend

RUN useradd --create-home --uid 10001 sccompute \
    && chown -R sccompute:sccompute /app /home/sccompute
USER sccompute

EXPOSE 10000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000} --workers 1"]
