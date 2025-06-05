# Configuration
DOCKER_IMAGE=bankgen-cli
PROJECT_NAME=bankgen

# Build the docker image
build:
	docker build -t $(DOCKER_IMAGE) .

# Run the container (default runs both stages)
run:
	docker run --rm -v $(PWD)/data:/app/data $(DOCKER_IMAGE)

# Run specific step
run-personas:
	docker run --rm -v $(PWD)/data:/app/data $(DOCKER_IMAGE) -r personas

run-transactions:
	docker run --rm -v $(PWD)/data:/app/data $(DOCKER_IMAGE) -r transactions

# Run dry-run
dry:
	docker run --rm -v $(PWD)/data:/app/data $(DOCKER_IMAGE) --dry-run

# Validate config
validate:
	docker run --rm -v $(PWD)/data:/app/data $(DOCKER_IMAGE) --validate-config

# Update config
config:
	@echo "Usage: make config KEY=your_key VALUE=your_value"
	docker run --rm -v $(PWD)/data:/app/data $(DOCKER_IMAGE) set-config $(KEY) $(VALUE)
