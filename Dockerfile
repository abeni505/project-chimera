FROM python:3.11-slim

WORKDIR /app

# Copy source
COPY . /app

# Install system deps needed for building and running verify
RUN apt-get update \
    && apt-get install -y --no-install-recommends make git \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps used by CI/checks
RUN python -m pip install --upgrade pip \
    && pip install -r requirements.txt pytest pre-commit

# Install pre-commit hooks and run repository verification during image build
RUN pre-commit install --install-hooks || true
RUN make verify

CMD ["/bin/bash"]
