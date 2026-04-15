FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ARG TORCH_INDEX_URL=https://download.pytorch.org/whl/cu121

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libxcb1 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libx11-xcb1 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --index-url ${TORCH_INDEX_URL} torch==2.7.0 torchvision==0.22.0
RUN pip install -r requirements.txt

COPY . .
RUN chmod +x ./entrypoint.sh

EXPOSE 8005
CMD ["sh", "./entrypoint.sh"]
