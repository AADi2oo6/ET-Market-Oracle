# Update to 3.13 to match your pyproject.toml
FROM python:3.13-slim

# Install uv directly from astral-sh
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set the working directory
WORKDIR /app

# Copy dependency management files
COPY pyproject.toml ./ 
# Copy the lockfile if it exists, otherwise it will just use pyproject.toml
COPY uv.lock* ./

# Install dependencies into the system environment using uv
RUN uv pip install --system -e .

# Copy the actual application code
COPY ./app ./app

# Command to run the API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]