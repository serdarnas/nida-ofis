FROM python:3.12-slim

WORKDIR /app

# tmux isteğe bağlı koşular için kurulur
RUN apt-get update && apt-get install -y --no-install-recommends tmux git tzdata && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir openpyxl

COPY . /app

# Konteyner içinde dışarıdan erişim, varsayılan port ve kalıcı veri dizini
ENV TZ=Europe/Istanbul
ENV OFIS_HOST=0.0.0.0
ENV OFIS_PORT=8796
ENV OFIS_DATA_DIR=/app/data

# Kalıcı depolama volume (redeploy'larda verilerin sıfırlanmasını önler)
VOLUME ["/app/data"]

EXPOSE 8796

CMD ["python3", "sunucu.py"]
