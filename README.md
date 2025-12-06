# Web Service Data Platform

Web service that provides and manages data through a clear and easy to use REST API. The project is organized into separate services, making it a solid base for building data features, small independent microservices, and systems that need to connect or share information.

### Instructions
``` bash
git clone https://github.com/PolJaimejuanCaubet/web-service-data-platform.git
cd web-service-data-platform
```
### Install dependencies
```bash
pip install uv
uv sync
```
### Environment variables
Complete with your own variables
```bash
cp .env.example .env
cp backend/app/config/config.example.py backend/app/config/config.py
```
### Start the service
```bash
uv run uvicorn backend.main:app --reload 
```
The API will typically be available at:

http://127.0.0.1/docs#/

### Example API Calls

Below are example REST endpoints your service may expose.

Health Check
curl -X GET http://localhost:3000/api/health


Example Response

{
  "status": "ok",
  "timestamp": "2025-01-01T12:00:00Z"
}

Get All Data
curl -X GET http://localhost:3000/api/data

Create a Data Entry
curl -X POST http://localhost:3000/api/data \
  -H "Content-Type: application/json" \
  -d '{
        "name": "example",
        "value": 123
      }'

Get Data by ID
curl -X GET http://localhost:3000/api/data/42

Delete Data
curl -X DELETE http://localhost:3000/api/data/42

### Project Structure

/backend
  /app
    /auth          # Authentication and business logic
    /config        # Configuration / settings modules
    /dependencies  # Shared dependencies and injections
    /models        # Data models / schemas
    /services      # Service layer / business operations
    /routes        # API route definitions
  main.py          # Application entry point

/frontend          # Frontend application (UI)
.env.example       # Sample environment configuration
pyproject.toml     # Project dependencies and settings (Python)
uv.lock            # Lockfile for version pinning
README.md          # Documentation


