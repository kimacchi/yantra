FROM python:3.11-slim

# Install the Docker CLI
# We need to install docker-ce-cli (the client) to run 'docker' commands.
# We are NOT running the docker daemon, just the client.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    gnupg \
  && install -m 0755 -d /etc/apt/keyrings \
  && curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg \
  && chmod a+r /etc/apt/keyrings/docker.gpg \
  && echo \
     "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
     $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
     tee /etc/apt/sources.list.d/docker.list > /dev/null \
  && apt-get update \
  && apt-get install -y docker-ce-cli \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY worker.py .
CMD ["python", "worker.py"]
