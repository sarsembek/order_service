# Order Service

## Introduction
This is a **FastAPI-based microservice** that handles product ordering. It includes the following features:
- Order creation, listing, and soft deletion
- Product management (create, list, retrieve)
- Basic authentication (user registration, login, token refresh)
- PostgreSQL for data persistence
- Redis for caching orders
- Logging of user actions
- Event logging for order status changes
- Metrics collection and exposure
- Unit testing for main components

## Tech Stack
- **Python 3.13**
- **FastAPI / Uvicorn**
- **Poetry** for dependency management
- **Alembic** for database migrations
- **PostgreSQL**
- **Redis**
- **Pytest** for unit testing

## Directory Structure
```
app/
│── core/          # Shared core modules (models, schemas, exceptions)
│── repositories/  # Database access logic
│── services/      # Business logic for orders, products, authentication
│── routers/       # FastAPI routers
│── migrations/    # Alembic migration scripts
│── utils/         # Utility functions and middleware
│── tests/         # Unit tests
```

## Installation & Setup

### 1. Install Poetry (if not already installed)
Follow the official [Poetry installation guide](https://python-poetry.org/docs/#installation).

### 2. Install dependencies
```sh
poetry install
```

### 3. Configure environment variables
Create a .env file in the project root and set values for:
```
DB_USER=order_user
DB_PASSWORD=order_service2025
DB_NAME=order_service
DB_HOST=db
DB_URL=postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}/${DB_NAME}
SECRET_KEY=your_secret_key
REDIS_HOST=redis
REDIS_PORT=6379
```

### 4. Build and start the Docker containers
```sh
docker-compose up --build
```

### 5. Run Alembic migrations
```sh
docker-compose exec web alembic upgrade head
```

## Usage

- Access the application at: **[http://localhost:8000](http://localhost:8000)**
- Use the `/auth` endpoints for **registration and login**
- Create and list orders via `/orders`
- Access metrics via `/metrics`

## Features

### Logging
- Logs user actions such as registration, login, and order creation, update, and deletion.
- Logs are saved to a file located at app.log.

### Caching with Redis
- Uses Redis to cache orders for faster retrieval.
- Redis configuration is set via environment variables `REDIS_HOST` and `REDIS_PORT`.

### Events
- Logs events when the status of an order changes.
- Logs include `order_id`, `old_status`, and `new_status`.

### Metrics
- Collects basic API metrics such as the number of calls to each endpoint, successful and unsuccessful requests.
- Metrics are exposed via the `/metrics` endpoint.

### Unit Testing
- Uses `pytest` for unit testing.
- Tests cover main components such as `AuthService`, `OrderService`, and FastAPI endpoints.
- To run tests, use the following command:
```sh
pytest
```