FROM python:3.10-slim

# 1. Sistem paketlerini, ImageMagick'i ve Arial alternatifi Liberation fontlarını kur
RUN apt-get update && apt-get install -y \
    imagemagick \
    fonts-liberation \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 2. MoviePy'nin altyazı yazmasını engelleyen ImageMagick güvenlik politikasını devre dışı bırak
RUN sed -i 's/domain="path" rights="none" pattern="@\*"/domain="path" rights="read|write" pattern="@\*"/g' /etc/ImageMagick-6/policy.xml || \
    sed -i 's/domain="path" rights="none" pattern="@\*"/domain="path" rights="read|write" pattern="@\*"/g' /etc/ImageMagick-7/policy.xml

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]
