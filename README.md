# 🧠 NeuroSentinel  
### Powered by AI, LLMs, Federated Learning, Threat Intelligence, and Forensics

---

## 🔍 Overview

This project is a **next-generation cybersecurity platform** designed to provide **autonomous, intelligent, and distributed defense** across multiple systems and networks. Combining the power of **machine learning**, **large language models (LLMs)**, **federated learning**, **threat intelligence APIs**, and **automated response mechanisms**, the platform detects, analyzes, and reacts to threats in real-time — without human intervention.

Unlike traditional, centralized security solutions, this system empowers each node to monitor itself, learn local behavior, detect anomalies, and participate in a collaborative learning ecosystem — all while preserving user privacy through **differential privacy**.

---

## 🔑 Key Features

- **Local Behavioral Anomaly Detection** using ML (AutoEncoders, Isolation Forest, etc.)
- **Federated Learning Engine** for collaborative model training across distributed nodes
- **Differential Privacy** to protect sensitive data while aggregating models
- **LLM-Powered Log Analysis** using local language models (LLaMA/Mistral) for natural language summarization of system events and security incidents
- **Autonomous Threat Response** (block malicious IPs, isolate processes, lock accounts, etc.)
- **Threat Intelligence Integration** with APIs like VirusTotal, AbuseIPDB, and OTX for enrichment
- **Real-Time Forensic Snapshot** creation after threat detection
- **Web-Based Dashboard** (React/Vue) for monitoring agents, alerts, and analysis results
- **DevOps-Ready** with full Docker support, Prometheus/Grafana observability, and CI/CD pipelines

---

## 🚀 Quick Start

### Prerequisites

- **Docker & Docker Compose**: Version 20.10+ and 2.0+
- **Git**: For cloning the repository
- **8GB+ RAM**: Recommended for running all services
- **10GB+ Disk Space**: For containers, models, and data

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/NeuroSentinel.git
   cd NeuroSentinel
   ```

2. **Build all containers**
   ```bash
   docker-compose build
   ```

3. **Start core infrastructure**
   ```bash
   docker-compose up -d postgres redis prometheus
   ```

4. **Initialize the database**
   ```bash
   make db-init
   ```

5. **Start all services**
   ```bash
   docker-compose up -d
   ```

6. **Generate sample data and train models**
   ```bash
   make generate-sample-data
   make train-isolation-forest
   make train-autoencoder
   ```

### 🎯 Running the Project

#### Start All Services
```bash
# Start everything
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

#### Access Services

| Service | URL | Description |
|---------|-----|-------------|
| **Dashboard** | http://localhost:5173 | React frontend |
| **API Server** | http://localhost:8000 | FastAPI backend |
| **ML Core API** | http://localhost:9000 | ML model serving |
| **Prometheus** | http://localhost:9090 | Metrics monitoring |
| **PostgreSQL** | localhost:5432 | Database |
| **Redis** | localhost:6379 | Cache/Queue |

#### API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Get all events
curl http://localhost:8000/events

# Get all agents
curl http://localhost:8000/agents

# ML prediction
curl -X POST http://localhost:9000/predict \
  -H "Content-Type: application/json" \
  -d '{"data": {...}}'
```

#### Training ML Models

```bash
# Train Isolation Forest
make train-isolation-forest

# Train AutoEncoder
make train-autoencoder

# Quick training with minimal data
make quick-train

# Run tests
make test
```

#### Database Management

```bash
# Initialize database
make db-init

# Check database status
make db-check

# View database stats
make db-stats

# Reset database (DESTRUCTIVE)
make db-reset
```

#### Development Commands

```bash
# View service status
make status

# View recent logs
make logs

# Clean up temporary files
make clean

# Run tests locally
make test-local
```

### 📊 Monitoring & Observability

#### Check System Health
```bash
# All services status
docker-compose ps

# Service health
curl http://localhost:8000/health | jq

# Database connectivity
make db-check

# ML API health
curl http://localhost:9000/health
```

#### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f server
docker-compose logs -f agent
docker-compose logs -f ml_core

# Recent training logs
make logs
```

#### Metrics & Monitoring
- **Prometheus**: http://localhost:9090
- **Grafana**: Available via Prometheus data source
- **Application Metrics**: Available via `/metrics` endpoints

### 🔧 Configuration

#### Environment Variables

Create `.env` file for custom configuration:

```bash
# Database
POSTGRES_DB=neurosentinel
POSTGRES_USER=neurosentinel
POSTGRES_PASSWORD=your_password

# Redis
REDIS_URL=redis://redis:6379

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# Agent
AGENT_ID=agent-001
AGENT_SERVER_URL=http://server:8000
AGENT_COLLECTION_INTERVAL=30

# ML Core
ML_CORE_HOST=0.0.0.0
ML_CORE_PORT=9000
```

#### Model Configuration

Edit config files in `ml_core/data/configs/`:

```json
{
  "model_type": "autoencoder",
  "model_params": {
    "hidden_dims": [64, 32, 16],
    "dropout_rate": 0.2,
    "activation": "relu"
  },
  "training": {
    "epochs": 50,
    "batch_size": 32
  }
}
```

### 🧪 Testing

#### Run All Tests
```bash
# ML core tests
make test

# Local tests (requires venv)
make test-local

# Quick training test
make quick-train
```

#### Manual Testing

```bash
# Test agent data collection
docker-compose logs agent

# Test server API
curl http://localhost:8000/health

# Test ML predictions
curl -X POST http://localhost:9000/predict \
  -H "Content-Type: application/json" \
  -d '{"data": {"cpu_percent": 85, "memory_percent": 90}}'

# Test WebSocket connection
wscat -c ws://localhost:8000/ws
```

### 🚨 Troubleshooting

#### Common Issues

**1. Database Connection Errors**
```bash
# Reinitialize database
make db-init

# Check database status
make db-check
```

**2. Container Build Failures**
```bash
# Clean rebuild
docker-compose build --no-cache

# Remove all containers and volumes
docker-compose down -v
docker-compose up -d
```

**3. ML Training Failures**
```bash
# Check config files
ls -la ml_core/data/configs/

# Regenerate sample data
make generate-sample-data

# Clean and retrain
make clean
make train-isolation-forest
```

**4. Port Conflicts**
```bash
# Check what's using ports
lsof -i :8000
lsof -i :9000
lsof -i :5173

# Stop conflicting services
sudo systemctl stop conflicting-service
```

#### Log Analysis

```bash
# Check for errors
docker-compose logs | grep -i error

# Check for warnings
docker-compose logs | grep -i warn

# Follow specific service
docker-compose logs -f server | grep -i error
```

### 🧹 Cleanup

#### Stop All Services
```bash
# Stop and remove containers
docker-compose down

# Stop and remove containers + volumes
docker-compose down -v

# Stop and remove containers + volumes + images
docker-compose down -v --rmi all
```

#### Clean Development Environment
```bash
# Clean temporary files
make clean

# Remove all containers
docker system prune -a

# Remove volumes
docker volume prune
```

---

## 🧱 Architecture Overview

```
+----------------+        +--------------------+        +-----------------+
|   Agent Node   | <----> | Central Intelligence| <----> |  Threat APIs    |
|  (Python App)  |        |   (FastAPI Server)  |        |  (VirusTotal…)  |
+----------------+        +--------------------+        +-----------------+
       |                            |                            |
       |     Federated Learning     |                            |
       |--------------------------->|                            |
       |                            |                            |
+------+----------------------------+----------------------------+
|              ML + LLM Core (Analysis Engine)                  |
|  - Autoencoder, IsolationForest, Opacus for DP                |
|  - LLaMA/Mistral for log summarization and detection          |
+---------------------------------------------------------------+
```

---

## 📂 Components

| Module              | Description |
|---------------------|-------------|
| **Agent Node**      | Collects logs, monitors behavior, runs local ML models, performs automated actions, and takes forensic snapshots. |
| **FastAPI Backend** | Central server to manage agents, collect alerts, aggregate models, and interact with the dashboard. |
| **ML Engine**       | Trains anomaly detection models locally and aggregates them using Federated Learning with DP. |
| **LLM Engine**      | Parses and summarizes system logs using embedded language models to extract threats in plain English. |
| **Threat Intel**    | Queries VirusTotal, AbuseIPDB, and Shodan to enrich IP/domain/file analysis. |
| **Forensic Module** | Captures system state snapshots (RAM, open connections, process tree, etc.) for post-incident investigation. |
| **Dashboard**       | Web UI for visualizing node health, alerts, threat intelligence, model performance, and policies. |

---

## 🛠️ Technologies Used

- **Backend**: FastAPI, PostgreSQL, Redis
- **Frontend**: React.js or Vue.js, WebSockets
- **Machine Learning**: Scikit-learn, PyTorch, Opacus (DP)
- **LLM Integration**: LLaMA, Mistral, llama.cpp or Ollama
- **Security & Forensics**: psutil, scapy, watchdog, gcore, volatility
- **DevOps**: Docker, Docker Compose, Prometheus, Grafana, GitHub Actions

---

## 🔄 Comparison with Industry Tools

| Feature                                       | This Project ✅                              | Industry Tools (Darktrace, Wazuh, etc.) ❌ |
|----------------------------------------------|----------------------------------------------|--------------------------------------------|
| Distributed Autonomous Agents                | ✅ Each node acts independently               | ❌ Centralized detection only               |
| Federated Learning                           | ✅ Collaborative model training               | ❌ Not supported                            |
| Differential Privacy                         | ✅ Protects sensitive data in training        | ❌ Not implemented                          |
| LLM-Based Log Summarization (e.g. LLaMA)     | ✅ Embedded language model for log analysis   | 🔶 Rare (experimental in research only)     |
| Forensic Snapshot Engine                     | ✅ Real-time memory/process dump              | ❌ Requires manual or external tools        |
| Open Source + Modular Architecture           | ✅ Fully modular & extensible                 | ❌ Mostly closed-source or limited modules  |
| Threat Intel Enrichment with APIs            | ✅ Integrated with public APIs                | ✅ Available but often commercial           |
| DevOps-Friendly (Docker, CI/CD, Monitoring)  | ✅ Full stack ready for deployment            | ❌ Often heavy or proprietary stack         |

---

## 🚧 Development Roadmap

### Phase 1 – MVP
- [x] Basic agent for monitoring logs and files
- [x] FastAPI backend with alert ingestion and REST API
- [x] Basic dashboard UI
- [x] ML-based local anomaly detection
- [x] Database integration and persistence

### Phase 2 – Core Intelligence
- [ ] Federated model sharing with DP
- [ ] Snapshot module for forensic capture
- [ ] Enhanced threat detection algorithms

### Phase 3 – LLM & Threat API Integration
- [ ] LLM-powered log summarization
- [ ] VirusTotal and AbuseIPDB enrichment
- [ ] AI-generated threat reports in dashboard

### Phase 4 – Privacy and Scalability
- [ ] Differential Privacy with Opacus
- [ ] Role-based access control
- [ ] Multi-node scalability with Kubernetes (optional)

---

## 📜 License

This project is released under the MIT License. Contributions are welcome.

---

## 🙋 About the Author

This project was designed and developed by PeymanSohi, a DevOps & Python Engineer passionate about AI, cybersecurity, and building resilient distributed systems.

> *"Security is not just a feature — it's a self-adaptive, intelligent organism in the modern cloud era."*


---

## 📝 License

This project is licensed under the **Apache License 2.0**.  
See the [LICENSE](LICENSE) file for full details.

- ✅ Free for commercial use  
- ✅ Open to contributions and forks  
- ✅ Includes patent grant protection  
- ✅ Requires proper attribution

> By using this project, you agree not to use it for malicious or unethical purposes.


---

## 📝 License

This project is licensed under the **Apache License 2.0**.  
See the [LICENSE](LICENSE) file for full license text.

## Project Overview
A smart, distributed cyber defense platform that learns system behaviors, detects and predicts threats, and responds autonomously when needed. It uses collaborative learning, large language models (LLMs), forensic analysis, and threat intelligence APIs to enhance its defense power.

## Directory Structure

- `agent/` — Distributed agent node (collects, monitors, reports)
- `server/` — Central FastAPI server (API, aggregation, orchestration)
- `ml_core/` — ML engine (anomaly detection, federated learning)
- `llm_core/` — LLM-based log analysis, summarization, reporting
- `forensics/` — Forensic snapshot and analysis tools
- `threat_api/` — Threat intelligence API integrations
- `dashboard/` — Frontend dashboard (React/Vite)
- `shared/` — Shared code (schemas, utils, config)

See module READMEs for more details.

# NeuroSentinel - Autonomous Distributed Cyber Defense Platform

A comprehensive, ML-powered cyber defense platform that provides real-time threat detection, anomaly analysis, and automated response capabilities.

## 🚀 Features

- **Advanced System Monitoring**: Comprehensive data collection from system, process, network, file, user, and security tools
- **ML-Powered Anomaly Detection**: Local machine learning models for real-time threat detection
- **Distributed Architecture**: Scalable agent-server architecture with containerized deployment
- **Real-time Processing**: WebSocket and REST API support for live data streaming
- **Threat Intelligence**: Integration with external threat feeds and indicators
- **Automated Response**: Configurable response actions based on detected threats

## 🏗️ Architecture

```
NeuroSentinel/
├── agent/                 # Lightweight monitoring agent
│   ├── collectors/        # Data collection modules
│   ├── agent.py          # Main agent daemon
│   └── Dockerfile        # Agent container
├── server/               # Central server (FastAPI)
│   ├── main.py          # API server
│   └── Dockerfile       # Server container
├── ml_core/             # Machine learning module
│   ├── detectors/       # Anomaly detection algorithms
│   ├── models/          # Neural network models
│   ├── preprocessing/   # Data preprocessing
│   ├── utils/           # ML utilities
│   └── train_models.py  # Training script
├── dashboard/           # React frontend
├── data/               # Training and validation data
├── models/             # Trained model artifacts
└── docker-compose.yml  # Orchestration
```

## 🛠️ Quick Start

### Prerequisites

- **Docker & Docker Compose**: Version 20.10+ and 2.0+
- **Git**: For cloning the repository
- **8GB+ RAM**: Recommended for running all services
- **10GB+ Disk Space**: For containers, models, and data

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/peymansohi/NeuroSentinel.git
   cd NeuroSentinel
   ```

2. **Build all containers**
   ```bash
   docker-compose build
   ```

3. **Start core infrastructure**
   ```bash
   docker-compose up -d postgres redis prometheus
   ```

4. **Initialize the database**
   ```bash
   make db-init
   ```

5. **Start all services**
   ```bash
   docker-compose up -d
   ```

6. **Generate sample data and train models**
   ```bash
   make generate-sample-data
   make train-isolation-forest
   make train-autoencoder
   ```

### 🎯 Running the Project

#### Start All Services
```bash
# Start everything
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

#### Access Services

| Service | URL | Description |
|---------|-----|-------------|
| **Dashboard** | http://localhost:5173 | React frontend |
| **API Server** | http://localhost:8000 | FastAPI backend |
| **ML Core API** | http://localhost:9000 | ML model serving |
| **Prometheus** | http://localhost:9090 | Metrics monitoring |
| **PostgreSQL** | localhost:5432 | Database |
| **Redis** | localhost:6379 | Cache/Queue |

#### API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Get all events
curl http://localhost:8000/events

# Get all agents
curl http://localhost:8000/agents

# ML prediction
curl -X POST http://localhost:9000/predict \
  -H "Content-Type: application/json" \
  -d '{"data": {...}}'
```

#### Training ML Models

```bash
# Train Isolation Forest
make train-isolation-forest

# Train AutoEncoder
make train-autoencoder

# Quick training with minimal data
make quick-train

# Run tests
make test
```

#### Database Management

```bash
# Initialize database
make db-init

# Check database status
make db-check

# View database stats
make db-stats

# Reset database (DESTRUCTIVE)
make db-reset
```

#### Development Commands

```bash
# View service status
make status

# View recent logs
make logs

# Clean up temporary files
make clean

# Run tests locally
make test-local
```

### 📊 Monitoring & Observability

#### Check System Health
```bash
# All services status
docker-compose ps

# Service health
curl http://localhost:8000/health | jq

# Database connectivity
make db-check

# ML API health
curl http://localhost:9000/health
```

#### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f server
docker-compose logs -f agent
docker-compose logs -f ml_core

# Recent training logs
make logs
```

#### Metrics & Monitoring
- **Prometheus**: http://localhost:9090
- **Grafana**: Available via Prometheus data source
- **Application Metrics**: Available via `/metrics` endpoints

### 🔧 Configuration

#### Environment Variables

Create `.env` file for custom configuration:

```bash
# Database
POSTGRES_DB=neurosentinel
POSTGRES_USER=neurosentinel
POSTGRES_PASSWORD=your_password

# Redis
REDIS_URL=redis://redis:6379

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# Agent
AGENT_ID=agent-001
AGENT_SERVER_URL=http://server:8000
AGENT_COLLECTION_INTERVAL=30

# ML Core
ML_CORE_HOST=0.0.0.0
ML_CORE_PORT=9000
```

#### Model Configuration

Edit config files in `ml_core/data/configs/`:

```json
{
  "model_type": "autoencoder",
  "model_params": {
    "hidden_dims": [64, 32, 16],
    "dropout_rate": 0.2,
    "activation": "relu"
  },
  "training": {
    "epochs": 50,
    "batch_size": 32
  }
}
```

### 🧪 Testing

#### Run All Tests
```bash
# ML core tests
make test

# Local tests (requires venv)
make test-local

# Quick training test
make quick-train
```

#### Manual Testing

```bash
# Test agent data collection
docker-compose logs agent

# Test server API
curl http://localhost:8000/health

# Test ML predictions
curl -X POST http://localhost:9000/predict \
  -H "Content-Type: application/json" \
  -d '{"data": {"cpu_percent": 85, "memory_percent": 90}}'

# Test WebSocket connection
wscat -c ws://localhost:8000/ws
```

### 🚨 Troubleshooting

#### Common Issues

**1. Database Connection Errors**
```bash
# Reinitialize database
make db-init

# Check database status
make db-check
```

**2. Container Build Failures**
```bash
# Clean rebuild
docker-compose build --no-cache

# Remove all containers and volumes
docker-compose down -v
docker-compose up -d
```

**3. ML Training Failures**
```bash
# Check config files
ls -la ml_core/data/configs/

# Regenerate sample data
make generate-sample-data

# Clean and retrain
make clean
make train-isolation-forest
```

**4. Port Conflicts**
```bash
# Check what's using ports
lsof -i :8000
lsof -i :9000
lsof -i :5173

# Stop conflicting services
sudo systemctl stop conflicting-service
```

#### Log Analysis

```bash
# Check for errors
docker-compose logs | grep -i error

# Check for warnings
docker-compose logs | grep -i warn

# Follow specific service
docker-compose logs -f server | grep -i error
```

### 🧹 Cleanup

#### Stop All Services
```bash
# Stop and remove containers
docker-compose down

# Stop and remove containers + volumes
docker-compose down -v

# Stop and remove containers + volumes + images
docker-compose down -v --rmi all
```

#### Clean Development Environment
```bash
# Clean temporary files
make clean

# Remove all containers
docker system prune -a

# Remove volumes
docker volume prune
```

---

## 📜 License

This project is licensed under the **Apache License 2.0**.  
See the [LICENSE](LICENSE) file for full details.

- ✅ Free for commercial use  
- ✅ Open to contributions and forks  
- ✅ Includes patent grant protection  
- ✅ Requires proper attribution

> By using this project, you agree not to use it for malicious or unethical purposes.

