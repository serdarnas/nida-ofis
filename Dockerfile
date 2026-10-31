FROM python:3.12-slim

WORKDIR /app

# tmux isteğe bağlı koşular için kurulur
RUN apt-get update && apt-get install -y --no-install-recommends tmux git && rm -rf /var/lib/apt/lists/*

COPY . /app

# Konteyner içinde dışarıdan erişim ve varsayılan port
ENV OFIS_HOST=0.0.0.0
ENV OFIS_PORT=8796

EXPOSE 8796

CMD ["python3", "sunucu.py"]
