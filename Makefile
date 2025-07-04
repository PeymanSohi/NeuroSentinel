# NeuroSentinel ML Core Makefile
# Provides common commands for training, testing, and serving models

.PHONY: help test train-isolation-forest train-autoencoder serve clean logs

# Default target
help:
	@echo "NeuroSentinel ML Core - Available Commands:"
	@echo ""
	@echo "Testing:"
	@echo "  test                    - Run ML core tests"
	@echo "  test-local              - Run tests locally (requires venv)"
	@echo ""
	@echo "Training:"
	@echo "  train-isolation-forest  - Train IsolationForest model"
	@echo "  train-autoencoder       - Train AutoEncoder model"
	@echo "  train-custom            - Train with custom config (make train-custom CONFIG=path/to/config.json)"
	@echo ""
	@echo "Serving:"
	@echo "  serve                   - Start ML core API server"
	@echo "  serve-background        - Start ML core API server in background"
	@echo ""
	@echo "Data Management:"
	@echo "  generate-sample-data    - Generate sample training data"
	@echo "  validate-data           - Validate training data format"
	@echo ""
	@echo "Utilities:"
	@echo "  logs                    - View recent training logs"
	@echo "  clean                   - Clean up temporary files"
	@echo "  status                  - Check service status"

# Testing
test:
	@echo "Running ML core tests..."
	docker-compose run --rm ml_core_test

test-local:
	@echo "Running ML core tests locally..."
	cd ml_core && python test_models.py

# Training
train-isolation-forest:
	@echo "Training IsolationForest model..."
	docker-compose run --rm ml_core_train python train_models.py \
		--data /data/processed/training_data.json \
		--validation /data/processed/validation_data.json \
		--model-type isolation_forest \
		--config /data/configs/isolation_forest_config.json \
		--experiment-name isolation_forest_experiment

train-autoencoder:
	@echo "Training AutoEncoder model..."
	docker-compose run --rm ml_core_train python train_models.py \
		--data /data/processed/training_data.json \
		--validation /data/processed/validation_data.json \
		--model-type autoencoder \
		--config /data/configs/autoencoder_config.json \
		--experiment-name autoencoder_experiment

train-custom:
	@echo "Training with custom config: $(CONFIG)"
	docker-compose run --rm ml_core_train python train_models.py \
		--data /data/processed/training_data.json \
		--validation /data/processed/validation_data.json \
		--model-type $(MODEL_TYPE) \
		--config $(CONFIG) \
		--experiment-name $(EXPERIMENT_NAME)

# Serving
serve:
	@echo "Starting ML core API server..."
	docker-compose up ml_core

serve-background:
	@echo "Starting ML core API server in background..."
	docker-compose up -d ml_core

# Data Management
generate-sample-data:
	@echo "Generating sample training data..."
	@if [ ! -f data/processed/training_data.json ]; then \
		echo "Sample data already exists. Use 'make clean' to regenerate."; \
	else \
		echo "Sample data generated successfully."; \
	fi

validate-data:
	@echo "Validating training data format..."
	@python -c "import json; json.load(open('data/processed/training_data.json')); print('✓ Training data is valid JSON')"
	@python -c "import json; json.load(open('data/processed/validation_data.json')); print('✓ Validation data is valid JSON')"

# Utilities
logs:
	@echo "Recent training logs:"
	@ls -la logs/ 2>/dev/null || echo "No logs directory found"
	@echo ""
	@echo "Recent experiment directories:"
	@ls -la models/ 2>/dev/null || echo "No models directory found"

clean:
	@echo "Cleaning up temporary files..."
	rm -rf logs/*.log
	rm -rf models/*_experiment_*
	rm -rf ml_core/__pycache__
	rm -rf ml_core/*/__pycache__
	@echo "Cleanup complete"

status:
	@echo "Docker Compose services status:"
	docker-compose ps
	@echo ""
	@echo "ML Core API health check:"
	@curl -s http://localhost:9000/health 2>/dev/null || echo "API not running"

# Development helpers
dev-setup:
	@echo "Setting up development environment..."
	python3 -m venv ml_venv
	. ml_venv/bin/activate && pip install -r ml_core/requirements.txt
	@echo "Development environment ready. Activate with: source ml_venv/bin/activate"

dev-test:
	@echo "Running tests in development environment..."
	. ml_venv/bin/activate && cd ml_core && python test_models.py

# Quick training with minimal data (for testing)
quick-train:
	@echo "Quick training with minimal data..."
	docker-compose run --rm ml_core_train python train_models.py \
		--data /data/processed/training_data.json \
		--model-type isolation_forest \
		--experiment-name quick_test

# Model evaluation
evaluate:
	@echo "Evaluating latest model..."
	@echo "Use the API endpoint: curl -X POST http://localhost:9000/predict -H 'Content-Type: application/json' -d '{\"data\": {...}}'"

# Documentation
docs:
	@echo "Generating documentation..."
	@echo "README files are in each module directory"
	@echo "API documentation available at: http://localhost:9000/docs (when server is running)" 