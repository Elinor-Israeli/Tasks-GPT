# Use an official Python run time as a base image 
FROM python:3.12-slim

# SET the working edirectory inside the container 
WORKDIR /app

# Set environment variables to reduce size and allow noninteractive installs
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install GCC and other build tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    libffi-dev \
    libssl-dev \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the requirements file first (for caching layers)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY ./src ./src

EXPOSE 8080

WORKDIR /app/src

# Command to run the application
CMD ["python", "main.py", "--socket"]
