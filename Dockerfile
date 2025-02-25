FROM python:3.13-slim AS base
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential

# Install Poetry
RUN pip install poetry

# Copy dependency files and install dependencies using Poetry without dev packages
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

# Build stage: copy the rest of the application
FROM base AS final
COPY . .

# Expose port 8000
EXPOSE 8000

# Run the application using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]