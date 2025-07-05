# 🧠 NeuroSentinel
### Autonomous Distributed Cyber Defense Platform
*Powered by AI, Machine Learning, and Real-time Threat Intelligence*

[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-green?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-red?logo=fastapi)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🔍 Overview

NeuroSentinel is a **next-generation cybersecurity platform** that provides **autonomous, intelligent, and distributed defense** for your **host machine**. The platform combines **machine learning**, **real-time monitoring**, **threat intelligence**, and **automated response mechanisms** to detect, analyze, and react to threats in real-time.

> **🎯 Key Point:** NeuroSentinel is designed and configured to monitor and secure the **host system** (not just the container it runs in). All data collected is from the host machine.

## 🏗️ System Architecture

![NeuroSentinel Architecture](diagram.svg)

*NeuroSentinel's distributed architecture showing the relationship between agents, central server, ML core, threat intelligence APIs, and the web dashboard.*

### 🌟 Key Features

- **🔍 Real-time Host Monitoring**: Comprehensive data collection from system metrics, processes, network connections, and security events on the host
- **🤖 ML-Powered Anomaly Detection**: Local machine learning models (Isolation Forest, AutoEncoder) for real-time threat detection
- **🌐 Cross-Platform Support**: Works on Linux (full), macOS (good), and Windows (basic)
- **🌐 Distributed Architecture**: Scalable agent-server architecture with containerized deployment
- **⚡ Real-time Processing**: WebSocket and REST API support for live data streaming
- **🛡️ Threat Intelligence**: Integration with external threat feeds and indicators
- **🚨 Automated Response**: Configurable response actions based on detected threats
- **📊 Web Dashboard**: Modern React-based interface for monitoring and analysis
- **📈 Observability**: Prometheus metrics and comprehensive logging
- **🔒 Host Security**: Privileged monitoring with read-only access to host system

---

## 🚀 Quick Start

### Prerequisites

- **Docker & Docker Compose**: Version 20.10+ and 2.0+
- **Git**: For cloning the repository
- **8GB+ RAM**: Recommended for running all services
- **10GB+ Disk Space**: For containers, models, and data

### 🏠 Host Monitoring Mode (Required)

To monitor and secure your **host machine**, the agent must be run with:
- `privileged: true` (full access to host resources)
- `network_mode: host` (uses host's network stack)
- **Host filesystem and system directories mounted read-only:**
  - `/:/host:ro`
  - `/var/run:/var/run:ro`
  - `/proc:/proc:ro`
  - `/sys:/sys:ro`
  - `/var/log:/var/log:ro`
- Environment variable: `HOST_ROOT=/host`

**Example agent service in `docker-compose.yml`:**
```yaml
agent:
  build: ./agent
  privileged: true
  network_mode: host
  volumes:
    - /:/host:ro
    - /var/run:/var/run:ro
    - /proc:/proc:ro
    - /sys:/sys:ro
    - /var/log:/var/log:ro
  depends_on:
    - server
  environment:
    - SEND_MODE=websocket
    - WS_URL=ws://localhost:8000/ws/events
    - SNAPSHOT_WS_PORT=8080
    - HOST_ROOT=/host
  ports:
    - "8080:8080"
```

### 📦 Installation & Setup

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

5. **Generate sample data and train models**
   ```bash
   make generate-sample-data
   make train-isolation-forest
   make train-autoencoder
   ```

6. **Start all services**
   ```bash
   docker-compose up -d
   ```

7. **Verify system health**
   ```bash
   docker-compose ps
   curl http://localhost:8000/health
   curl http://localhost:9000/health
   ```

---

## ✅ Verifying Host Monitoring

To confirm that the agent is monitoring your **host machine** (not just the container):

1. **Run the included test script in the agent container:**
   ```bash
   docker exec neurosentinel-agent-1 python3 /app/test_host_monitoring.py
   ```
   - You should see output like:
     - `monitoring_host: True`
     - Hostname, OS, process list, users, and logs from your host
     - Real host processes (e.g., `init`, `kthreadd`), users, and log files

2. **Check for real host data:**
   - Add a file or user on your host, or start a new process
   - Run the test script again and confirm it appears in the output

---

## 🔒 Security Note

> **⚠️ Warning:** Running the agent in privileged mode with host mounts gives it full read access to your host system. This is required for full host monitoring, but you should:
> - Only run trusted code in this mode
> - Review the agent's code and configuration
> - Limit access to the agent container and its network
> - Ensure your host system is properly secured

---

## 🎯 Running the Project

### Start All Services
```bash
# Start everything
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 🌐 Access Services

| Service | URL | Description |
|---------|-----|-------------|
| **Dashboard** | http://localhost:5173 | React frontend |
| **API Server** | http://localhost:8000 | FastAPI backend |
| **ML Core API** | http://localhost:9000 | ML model serving |
| **Prometheus** | http://localhost:9090 | Metrics monitoring |
| **Nginx Gateway** | http://localhost:80 | Reverse proxy |
| **PostgreSQL** | localhost:5432 | Database |
| **Redis** | localhost:6379 | Cache/Queue |

### 🔌 API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Get all events
curl http://localhost:8000/events

# ML prediction
curl -X POST http://localhost:9000/predict \
  -H "Content-Type: application/json" \
  -d '{"data": {"cpu_usage": 0.5, "memory_usage": 0.6, "network_connections": 10, "process_count": 50}, "model_type": "isolation_forest"}'

# List available models
curl http://localhost:9000/models
```

---

## 🛠️ Development Commands

### 🤖 Training ML Models
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

### 🗄️ Database Management
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

### 🔧 Development Utilities
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

---

## 📊 Monitoring & Observability

### Check System Health
```bash
# All services status
docker-compose ps

# Service health
curl http://localhost:8000/health | jq
curl http://localhost:9000/health | jq

# Database connectivity
make db-check

# ML API health
curl http://localhost:9000/health
```

### View Logs
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

### 📈 Metrics & Monitoring
- **Prometheus**: http://localhost:9090
- **Application Metrics**: Available via `/metrics` endpoints
- **Real-time Events**: WebSocket connections for live data

---

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Agent Node    │◄──►│  Central Server  │◄──►│  ML Core API    │
│ (Host Monitor)  │    │   (FastAPI)      │    │  (Model Serving)│
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │      Redis       │    │   Prometheus    │
│   (Database)    │    │   (Cache/Queue)  │    │   (Metrics)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                                 ▼
                    ┌──────────────────┐
                    │   Dashboard      │
                    │   (React UI)     │
                    └──────────────────┘
```

---

## 📂 Project Structure

```
NeuroSentinel/
├── agent/                 # Lightweight monitoring agent
│   ├── collectors/        # Data collection modules
│   │   ├── system.py      # System metrics collection (cross-platform)
│   │   ├── process.py     # Process monitoring (cross-platform)
│   │   ├── network.py     # Network connections
│   │   ├── file.py        # File system monitoring
│   │   ├── user.py        # User activity (cross-platform)
│   │   ├── logs.py        # Log file monitoring (cross-platform)
│   │   ├── security_tools.py # Security tool integration
│   │   └── snapshot.py    # System snapshot capture
│   ├── agent.py          # Main agent daemon
│   └── Dockerfile        # Agent container
├── server/               # Central server (FastAPI)
│   ├── main.py          # API server with WebSocket support
│   ├── models.py        # Database models
│   ├── database.py      # Database connection
│   └── Dockerfile       # Server container
├── ml_core/             # Machine learning module
│   ├── detectors/       # Anomaly detection algorithms
│   │   ├── isolation_forest.py
│   │   └── autoencoder_detector.py
│   ├── models/          # Trained model artifacts
│   ├── preprocessing/   # Data preprocessing
│   ├── utils/           # ML utilities
│   ├── train_models.py  # Training script
│   └── main.py         # ML API server
├── dashboard/           # React frontend
│   ├── src/            # React components
│   └── package.json    # Frontend dependencies
├── data/               # Training and validation data
│   ├── raw/           # Raw data
│   ├── processed/     # Processed data
│   └── configs/       # Model configurations
├── shared/            # Shared utilities and schemas
├── nginx/             # Nginx configuration
├── docker-compose.yml # Service orchestration
├── Makefile          # Development commands
├── CROSS_PLATFORM.md # Cross-platform compatibility guide
└── README.md         # This file
```

---

## 🔧 Configuration

### Environment Variables

The system uses Docker Compose for configuration. Key environment variables:

```yaml
# Database
POSTGRES_DB=neurosentinel
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# Redis
REDIS_URL=redis://redis:6379/0

# Server
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/neurosentinel

# Agent
SEND_MODE=websocket
WS_URL=ws://server:8000/ws/events
SNAPSHOT_WS_PORT=8080
HOST_ROOT=/host

# ML Core
PYTHONUNBUFFERED=1
```

### Model Configuration

Edit config files in `data/configs/`:

```json
{
  "model_type": "isolation_forest",
  "model_params": {
    "contamination": 0.1,
    "random_state": 42
  },
  "training": {
    "test_size": 0.2,
    "random_state": 42
  }
}
```

---

## 🧪 Testing

### Run All Tests
```bash
# ML core tests
make test

# Local tests (requires venv)
make test-local

# Quick training test
make quick-train
```

### Manual Testing

```bash
# Test agent data collection
docker logs neurosentinel-agent-1

# Test server API
curl http://localhost:8000/health

# Test ML predictions
curl -X POST http://localhost:9000/predict \
  -H "Content-Type: application/json" \
  -d '{"data": {"cpu_usage": 0.5, "memory_usage": 0.6, "network_connections": 10, "process_count": 50}, "model_type": "isolation_forest"}'

# Test WebSocket connection
wscat -c ws://localhost:8000/ws/events

# Test host monitoring
docker exec neurosentinel-agent-1 python3 /app/test_host_monitoring.py
```

---

## 🚨 Troubleshooting

### Common Issues

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
ls -la data/configs/

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

**5. Host Monitoring Issues**
```bash
# Verify host monitoring is working
docker exec neurosentinel-agent-1 python3 /app/test_host_monitoring.py

# Check agent configuration
docker-compose config agent
```

### Log Analysis

```bash
# Check for errors
docker-compose logs | grep -i error

# Check for warnings
docker-compose logs | grep -i warn

# Follow specific service
docker-compose logs -f server | grep -i error
```

---

## 🧹 Cleanup

### Stop All Services
```bash
# Stop and remove containers
docker-compose down

# Stop and remove containers + volumes
docker-compose down -v

# Stop and remove containers + volumes + images
docker-compose down -v --rmi all
```

### Clean Development Environment
```bash
# Clean temporary files
make clean

# Remove all containers
docker system prune -a

# Remove volumes
docker volume prune
```

---

## 🛠️ Technologies Used

- **Backend**: FastAPI, PostgreSQL, Redis
- **Frontend**: React.js, Vite
- **Machine Learning**: Scikit-learn, NumPy, Pandas
- **Monitoring**: Prometheus, Docker
- **DevOps**: Docker Compose, Make
- **Cross-Platform**: Platform detection and OS-specific collectors

## 🌐 Cross-Platform Support

NeuroSentinel supports multiple operating systems with varying levels of functionality:

- **Linux**: Full support with all features
- **macOS**: Good support with most features
- **Windows**: Basic support with limited features

See [CROSS_PLATFORM.md](CROSS_PLATFORM.md) for detailed platform-specific information and configuration.

---

## 🚧 Development Roadmap

### Phase 1 – MVP ✅
- [x] Basic agent for monitoring logs and files
- [x] FastAPI backend with alert ingestion and REST API
- [x] Basic dashboard UI
- [x] ML-based local anomaly detection
- [x] Database integration and persistence
- [x] Real-time WebSocket communication
- [x] System snapshot capabilities
- [x] Host monitoring with privileged access
- [x] Cross-platform compatibility

### Phase 2 – Enhanced Intelligence 🚧
- [ ] Federated model sharing
- [ ] Enhanced threat detection algorithms
- [ ] Advanced forensic capabilities
- [ ] Threat intelligence API integration

### Phase 3 – Advanced Features 📋
- [ ] LLM-powered log summarization
- [ ] Differential privacy for federated learning
- [ ] Advanced dashboard features
- [ ] Multi-node scalability

---

## 🙋 About

This project was designed and developed by **PeymanSohi**, a DevOps & Python Engineer passionate about AI, cybersecurity, and building resilient distributed systems.

> *"Security is not just a feature — it's a self-adaptive, intelligent organism in the modern cloud era."*

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow the existing code style
- Add tests for new features
- Update documentation
- Test cross-platform compatibility

---

## 📞 Support

For support, please:
- Open an issue on GitHub
- Check the [CROSS_PLATFORM.md](CROSS_PLATFORM.md) for platform-specific issues
- Review the troubleshooting section above
- Contact the maintainer

---

*NeuroSentinel - Defending the digital frontier with intelligent automation.* 🛡️

