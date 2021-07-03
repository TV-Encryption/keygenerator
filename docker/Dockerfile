FROM python:3.9.2-slim-buster@sha256:42c8f29231de3ac4b6bee92ed1313ad7650bc5a2a4cd56fdd890c9df8c320646 as base

ENV PYTHONUNBUFFERED 1

COPY requirements.txt ./
RUN pip --no-cache-dir install -r requirements.txt

RUN mkdir -p /app /srv/keys /srv/queues

WORKDIR /app

CMD ["python", "-m", "cli"]

### Development Image ###
### ---------------- ###
FROM base as dev

# Disable python bytecode caches
ENV PYTHONDONTWRITEBYTECODE 1

### Production Image ###
### ---------------- ###
FROM base as prod

# Copy project folder to current directory.
COPY . .
