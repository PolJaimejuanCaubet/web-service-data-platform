# Web Service Data Platform

Web service that provides and manages data through a clear and easy to use REST API. The project is organized into separate services, making it a solid base for building data features, small independent microservices, and systems that need to connect or share information.

### Instructions
``` bash
git clone https://github.com/PolJaimejuanCaubet/web-service-data-platform.git
cd web-service-data-platform
```
### To install dependencies and environment variables
Complete .env with your own variables
```bash
chmod +x config.sh
./config.sh
```
### Start backend and frontend service
```bash
chmod +x backend.sh
./backend.sh
```
The API will be available at:

http://127.0.0.1/docs#/

```bash
chmod +x frontend.sh
./frontend.sh
```
Frontend will be exposed at:

http://localhost:4200

### Example API Calls

Below are example REST endpoints your service may expose.

*Register*
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"full_name":"John","username":"john", "email":"john@test.com","password":"1234"}'

*Login*
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john&password=1234"

*Get All Users* (Only Admin)
curl -X GET http://localhost:8000/users

*Get AI Correaltion*
curl -X GET http://localhost:8000/etl/analytics/correlation/AAPL

### Project Structure

/backend
  /app
    /auth                   # Authentication logic (register, login, JWT handling)
    /config                 # Application configuration, settings & environment loading
    /dependencies           # Shared dependency injections for routes (DB, services, auth)
    /models                 # Pydantic models, request/response schemas, and database
    /services               # Core business logic (ETL, analytics, data processing, etc.)
    /routes                 # API route definitions grouped by feature (users, etl, auth)
  main.py                   # FastAPI application entry point

/frontend                   # Angular frontend application (UI)
  /src
    /app
      /guards               # Route guards (auth guard, admin guard, etc.)
      /interceptors         # HTTP interceptors (e.g., add JWT token, handle errors)
      /models               # Frontend interfaces/types for API responses
      /pages                # All page-level components (views)
        /dashboard          # User dashboard UI
        /dashboard-admin    # Admin dashboard UI
        /login              # Login page
        /register           # Registration page
      /services             # Frontend services (API clients, auth service, user service)
      
.env.example                # Template for environment variables
backend.sh                  # Script to start the backend server
config.sh                   # Script used for configuration setup tasks
frontend.sh                 # Script to start the Angular frontend
pyproject.toml              # Python dependencies and project configuration
README.md                   # Full project documentation
uv.lock                     # Locked dependency versions for reproducible builds
