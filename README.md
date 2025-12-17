<div align="center">

<img src="https://media.istockphoto.com/id/961649530/vector/finance-graphic-bars-up-rising-arrow-vector-illustration-design.jpg?s=612x612&w=0&k=20&c=sXxosOL8SggL-XNdrm3QP05YFcmTlerS9wqkmB6O-TM=" width="200"/>



# Stock Web Service


A website where you can overview stock data and generate videos from each stock

[Explore the docs »](https://web-service-data-platform.onrender.com/docs)

<br/>

[View Demo](https://please-teacher-grade-us-well.onrender.com) · [Report Bug](https://github.com/PolJaimejuanCaubet/web-service-data-platform/issues) · [Request Feature](https://github.com/PolJaimejuanCaubet/web-service-data-platform/issues)

<br/>

[![Contributors 1](https://img.shields.io/badge/contributors-1-green)](https://github.com/PolJaimejuanCaubet/web-service-data-platform/contributors) 
[![Issues 0 open](https://img.shields.io/github/issues/username/repo?color=green)](https://github.com/PolJaimejuanCaubet/web-service-data-platform/issues) 
[![License not specified](https://img.shields.io/badge/license-not%20specified-lightgrey)]()

</div>





# Web Service Platform
### Technologies used
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![FastApi](https://img.shields.io/badge/fastapi-05998b?style=for-the-badge&logo=fastapi&logoColor=white)
![Angular](https://img.shields.io/badge/angular.js-%23E23237.svg?style=for-the-badge&logo=angular&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-%234ea94b.svg?style=for-the-badge&logo=mongodb&logoColor=white)
![Render](https://img.shields.io/badge/Render-black.svg?style=for-the-badge&logo=render&logoColor=white)
![Jupyter Notebook](https://img.shields.io/badge/jupyter-%23FA0F00.svg?style=for-the-badge&logo=jupyter&logoColor=white)
![Git](https://img.shields.io/badge/git-%23F05033.svg?style=for-the-badge&logo=git&logoColor=white)

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
### Start backend service
```bash
chmod +x backend.sh
./backend.sh
```
The API locally will be available at:

[localhost](http://127.0.0.1/docs#/)

also to see all endpoints as it's deployed with **Render** you can visit:

[Web-Service-Platform-Backend](https://web-service-data-platform.onrender.com/docs)

### Start frontend service

```bash
chmod +x frontend.sh
./frontend.sh
```
Frontend locally will be exposed at:

[localhost](http://localhost:4200)

and also it's delpoyed on **Render** so you van visit.

[Web-Service-Platform-Frontend](https://please-teacher-grade-us-well.onrender.com)

---

### Example API Calls

Below are example REST endpoints your service may expose.

**Register**  
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"full_name":"John","username":"john", "email":"john@test.com","password":"1234"}'
```
**Login**
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john&password=1234"
```
**Get All Users** (Only Admin)
```bash
curl -X GET http://localhost:8000/users
```
**Get AI Correaltion**
```bash
curl -X GET http://localhost:8000/etl/analytics/correlation/AAPL
```
---
### Project Structure
```text
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
```




