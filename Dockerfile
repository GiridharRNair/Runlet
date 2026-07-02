FROM python:3.13-slim

ENV DEBIAN_FRONTEND=noninteractive

# ── system deps + all languages in one layer ─────────────────
RUN apt-get update && apt-get install -y \
    build-essential \
    libcap-dev \
    libseccomp-dev \
    libsystemd-dev \
    pkg-config \
    git \
    nodejs \
    openjdk-21-jdk-headless \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Build minimal runtime for execution only
RUN jlink \
    --no-header-files \
    --no-man-pages \
    --compress=zip-6 \
    --strip-debug \
    --add-modules java.base \
    --output /usr/lib/jvm/java-min

# ── isolate ──────────────────────────────────────────────────
RUN git clone https://github.com/ioi/isolate /isolate \
    && cd /isolate \
    && make install \
    && rm -rf /isolate

# ── isolate user (required for user namespace mappings) ──────
RUN useradd --system --no-create-home isolate \
    && echo "isolate:100000:65536" >> /etc/subuid \
    && echo "isolate:100000:65536" >> /etc/subgid

# ── app ──────────────────────────────────────────────────────
WORKDIR /app

COPY pyproject.toml README.md ./
RUN pip install .

COPY . .
RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
