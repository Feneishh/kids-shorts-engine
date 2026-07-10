FROM python:3.9-slim

# Video render ve yazı yazma araçlarını sisteme ücretsiz kur
RUN apt-get update && apt-get install -y \
    ffmpeg \
    imagemagick \
    && rm -rf /var/lib/apt/lists/*

# ImageMagick güvenlik duvarını kaldır (Yazıların düzgün basılması için şart)
RUN sed -i 's/domain="path" rights="none"/domain="path" rights="read|write"/g' /etc/ImageMagick-6/policy.xml || true

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]
