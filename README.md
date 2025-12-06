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
```bash
cp .env.example .env
```

### Start the service
```bash
uv run uvicorn backend.main:app --reload 
```
The API will typically be available at:

http://localhost:3000

# Database Configuration
DB_USER=user
DB_PASSWORD=password
DB_NAME=database_name


📡 Example API Calls

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

📂 Project Structure (Example)
/src
  /routes        # API route definitions
  /controllers   # Business logic
  /services      # Data access layer
  /models        # Data models / schemas
/config          # Configuration files
/tests           # Automated tests
.env.example     # Sample environment configuration
README.md        # Documentation

