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
- [ ] Basic agent for monitoring logs and files
- [ ] FastAPI backend with alert ingestion and REST API
- [ ] Basic dashboard UI

### Phase 2 – Core Intelligence
- [ ] ML-based local anomaly detection
- [ ] Federated model sharing with DP
- [ ] Snapshot module for forensic capture

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

- Docker and Docker Compose
- Python 3.11+ (for local development)
- Git

### 1. Clone and Setup

```bash
git clone <repository-url>
cd NeuroSentinel
```

### 2. Start Services

```bash
# Start all services
docker-compose up -d

# Or start specific services
docker-compose up agent server ml_core dashboard
```

### 3. Train ML Models

```bash
# Train IsolationForest model
make train-isolation-forest

# Train AutoEncoder model
make train-autoencoder

# Or use Docker Compose directly
docker-compose run --rm ml_core_train
```

### 4. Test the System

```bash
# Run ML core tests
make test

# Check service status
make status

# View logs
make logs
```

## 📊 ML Core - Machine Learning Module

The ML Core module provides sophisticated anomaly detection capabilities using both statistical and deep learning approaches.

### Supported Models

1. **IsolationForest**: Fast, unsupervised anomaly detection for tabular data
2. **AutoEncoder**: Neural network-based approach for complex pattern recognition

### Training Best Practices

#### 1. Data Preparation
- Store training data in `data/processed/`
- Use validation data for threshold selection
- Version your data files with timestamps

#### 2. Configuration Management
- Use JSON config files in `data/configs/`
- Separate configs for different model types
- Include experiment metadata

#### 3. Experiment Tracking
- All experiments are logged with timestamps
- Git commit hashes are captured
- Metrics and artifacts are saved automatically

#### 4. Model Management
- Models are versioned and registered
- Artifacts include model, preprocessor, and config
- Easy deployment and rollback

### Training Commands

```bash
# Quick training
make train-isolation-forest
make train-autoencoder

# Custom training
make train-custom CONFIG=data/configs/custom_config.json MODEL_TYPE=isolation_forest EXPERIMENT_NAME=my_experiment

# Development training
make dev-setup
make dev-test
```

### API Usage

```bash
# Start ML API server
make serve

# Predict anomalies
curl -X POST http://localhost:9000/predict \
  -H "Content-Type: application/json" \
  -d '{"data": {"system": {"cpu_percent": 85.5}}}'

# List models
curl http://localhost:9000/models
```

## 🔧 Configuration

### Agent Configuration

Environment variables in `agent/config.py`:
- `SERVER_URL`: Central server endpoint
- `AGENT_ID`: Unique agent identifier
- `INTERVAL`: Data collection interval
- `SEND_MODE`: Communication mode (rest/websocket)

### ML Core Configuration

Configuration files in `data/configs/`:
- Model hyperparameters
- Training settings
- Evaluation metrics
- Experiment metadata

### Docker Configuration

Services in `docker-compose.yml`:
- `agent`: Monitoring agent
- `server`: Central API server
- `ml_core`: ML training and inference
- `ml_core_test`: Testing service
- `ml_core_train`: Training service
- `dashboard`: Web interface

## 📈 Monitoring and Logging

### Logs

- Training logs: `logs/` directory
- Experiment artifacts: `models/` directory
- Service logs: `docker-compose logs <service>`

### Health Checks

```bash
# Check all services
make status

# API health
curl http://localhost:8000/health
curl http://localhost:9000/health

# Dashboard
open http://localhost:3000
```

## 🧪 Testing

### Run Tests

```bash
# All tests
make test

# Local development
make test-local

# Specific service
docker-compose run --rm ml_core_test
```

### Test Coverage

- Unit tests for ML components
- Integration tests for API endpoints
- Data validation tests
- Security scans

## 🚀 Deployment

### Development

```bash
# Setup development environment
make dev-setup

# Run tests
make dev-test

# Start services
docker-compose up
```

### Production

```bash
# Build and deploy
docker-compose -f docker-compose.prod.yml up -d

# Monitor deployment
make status
```

### CI/CD Pipeline

The project includes GitHub Actions workflows for:
- Automated testing
- Security scanning
- Docker image building
- Staging deployment
- Production deployment

## 📚 Documentation

- [ML Core Documentation](ml_core/README.md)
- [Agent Documentation](agent/README.md)
- [API Documentation](http://localhost:8000/docs)
- [ML API Documentation](http://localhost:9000/docs)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Development Guidelines

- Follow PEP 8 for Python code
- Add type hints
- Include docstrings
- Write unit tests
- Update documentation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- Issues: [GitHub Issues](https://github.com/your-repo/issues)
- Documentation: [Wiki](https://github.com/your-repo/wiki)
- Discussions: [GitHub Discussions](https://github.com/your-repo/discussions)

## 🔮 Roadmap

- [ ] Advanced threat hunting capabilities
- [ ] Integration with SIEM systems
- [ ] Automated incident response
- [ ] Cloud-native deployment options
- [ ] Advanced ML models (LSTM, Transformer)
- [ ] Real-time threat correlation
- [ ] Multi-tenant support
- [ ] Advanced visualization dashboard

