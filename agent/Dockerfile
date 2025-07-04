FROM python:3.11-slim

WORKDIR /app

# Install build dependencies for psutil and other native extensions
RUN apt-get update && apt-get install -y gcc python3-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

CMD ["python3", "agent.py"]