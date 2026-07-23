# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Repository Overview

The Infosys Responsible AI Toolkit is a comprehensive suite of APIs and microservices designed to integrate safety, security, privacy, explainability, fairness, and hallucination detection into AI solutions. The repository follows a microservices architecture with multiple independent modules that can be deployed together or separately.

## Architecture

### Core Architecture Pattern
- **Microservices Architecture**: Each module is an independent microservice with its own API endpoints
- **Language Stack**: 
  - Backend: Python 3.11.x (Flask-based APIs)
  - Frontend: Angular 15 (Module Federation for micro-frontends)
- **Deployment**: Docker containers with Kubernetes support
- **Database Support**: MongoDB, PostgreSQL, CosmosDB
- **LLM Integration**: Supports multiple LLMs (GPT-4, GPT-3.5, Llama3, Claude, Gemini)

### Module Categories

1. **Core AI Safety Modules**:
   - `responsible-ai-moderationlayer`: Central guardrails for prompt/response moderation
   - `responsible-ai-moderationmodel`: ML models for moderation checks
   - `responsible-ai-safety`: Toxicity and profanity detection
   - `responsible-ai-security`: Attack detection and defense mechanisms
   - `responsible-ai-privacy`: PII detection and anonymization

2. **AI Quality & Transparency**:
   - `responsible-ai-explainability`: SHAP/LIME explainability for ML models
   - `responsible-ai-llm-explain`: LLM-specific explanation methods (CoT, ToT, GoT, CoVe)
   - `responsible-ai-fairness`: Bias detection and mitigation
   - `responsible-ai-Hallucination`: RAG hallucination detection

3. **Frontend & Infrastructure**:
   - `responsible-ai-mfe`: Angular micro-frontend
   - `responsible-ai-shell`: Shell application for micro-frontend orchestration
   - `responsible-ai-backend`: User authentication and registration
   - `responsible-ai-admin`: Configuration management

4. **Supporting Services**:
   - `responsible-ai-telemetry`: Elasticsearch-based telemetry
   - `responsible-ai-file-storage`: Azure Blob Storage integration
   - `responsible-ai-llm-benchmarking`: LLM performance benchmarking

## Common Development Commands

### Python Microservices (Backend)

```bash
# Navigate to any Python module (e.g., responsible-ai-moderationlayer)
cd responsible-ai-<module-name>

# Create and activate virtual environment
python3.11 -m venv myenv
source myenv/bin/activate  # On macOS/Linux
# OR
myenv\Scripts\activate  # On Windows

# Install dependencies
cd requirements  # or requirement folder
pip install -r requirement.txt

# Configure environment variables
cp src/.env.example src/.env  # Create from template if exists
# Edit src/.env with necessary configurations

# Run the service
cd src
python main.py

# Run tests (if available)
python test.py
# OR
pytest tests/

# Build Docker image
docker build -t responsible-ai-<module-name> .

# Run with Docker
docker run -p <PORT>:<PORT> responsible-ai-<module-name>
```

### Angular Frontend (MFE)

```bash
cd responsible-ai-mfe

# Install dependencies
npm install --legacy-peer-deps

# Development server
npm start  # Runs on port 30055

# Build for production
npm run build

# Run tests
npm test

# Run all micro-frontends together
npm run run:all

# Build Docker image
docker build -t responsible-ai-mfe .
```

### Shell Application

```bash
cd responsible-ai-shell

# Install dependencies
npm install --legacy-peer-deps

# Start development server
npm start

# Build
npm run build
```

## Key Development Patterns

### API Endpoints Structure
- All APIs follow RESTful patterns
- Base paths: `/rai/v1/<module>/<endpoint>`
- Swagger documentation available at: `http://localhost:<PORT>/rai/v1/<module>/docs`

### Environment Configuration
Each module uses `.env` files with these common patterns:
- LLM credentials (Azure OpenAI, AWS Bedrock, Google AI)
- Database connections (MongoDB/PostgreSQL)
- Service URLs for inter-service communication
- Cache configuration (TTL, size)
- Telemetry flags

### Testing Strategy
- Unit tests: Located in `tests/` or as `test.py`
- Integration tests: Test inter-service communication
- API tests: Using Swagger UI at `/docs` endpoints

## Module-Specific Notes

### Moderation Layer Setup
1. **Must install Moderation Model first** before Moderation Layer
2. Download `en_core_web_lg` model and place in `lib/` folder
3. Configure all model URLs in `.env`
4. Supports both model-based and template-based guardrails

### Database Initialization
For modules requiring database:
1. Admin module includes initial DB setup JSONs in `Initial DB setup/`
2. Configure DB type in `.env`: `mongo`, `psql`, or `cosmos`
3. Run migrations/setup scripts if available

### Multi-LLM Support
Configure at least one LLM in `.env`:
- GPT-4/GPT-3.5: Azure OpenAI credentials
- Llama3-70b: Self-hosted endpoint
- Claude: AWS Bedrock credentials
- Gemini: Google AI API key

## Deployment

### Kubernetes Deployment
Most modules include Kubernetes manifests:
```bash
cd responsible-ai-<module>/Kubernetes/
kubectl apply -f responsible-ai-<module>.yaml
```

### Docker Compose (if available)
```bash
docker-compose up -d
```

## Inter-Service Dependencies

Critical service order:
1. **Database services** (MongoDB/PostgreSQL)
2. **responsible-ai-moderationmodel** (provides ML models)
3. **responsible-ai-admin** (configuration management)
4. **responsible-ai-moderationlayer** (depends on models)
5. **responsible-ai-backend** (authentication)
6. **responsible-ai-mfe** & **responsible-ai-shell** (frontend)

## Port Mapping Reference

Common default ports:
- Moderation Layer: 5000 (configurable)
- Admin: 8019
- MFE: 30055
- Backend services: Various (check `.env`)

## Troubleshooting

### Common Issues
1. **Module import errors**: Ensure Python 3.11.x is used
2. **npm install failures**: Use `--legacy-peer-deps` flag
3. **Service connection errors**: Verify all dependent services are running
4. **LLM errors**: Ensure at least one LLM is properly configured
5. **Database errors**: Check connection strings and credentials

### Debug Mode
Most Python services support debug mode:
```python
# In main.py
app.run(debug=True)
```

## Security Considerations

- Never commit `.env` files with credentials
- Use vault for production secrets (configure `ISVAULT=True`)
- Enable SSL verification in production (`VERIFY_SSL=True`)
- Configure OAuth2 for API authentication when required
- Follow the security ruleset for all code changes

## Quick Module Reference

| Module | Purpose | Language | Default Port |
|--------|---------|----------|--------------|
| moderationlayer | Central guardrails | Python/Flask | 5000 |
| moderationmodel | ML models API | Python/Flask | Configurable |
| admin | Configuration UI | Python/Flask | 8019 |
| mfe | Angular frontend | TypeScript | 30055 |
| backend | Authentication | Python/Flask | Configurable |
| telemetry | Elasticsearch integration | Python | Configurable |

## Additional Resources

- Full documentation: https://infosys.github.io/Infosys-Responsible-AI-Toolkit/
- API specifications: Check `api-spec/` folders
- Contribution guidelines: See CONTRIBUTING.md
- Support: Infosysraitoolkit@infosys.com
