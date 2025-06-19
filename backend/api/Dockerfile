# Use an official Python run time as a base image 
FROM python:3.12-slim

# SET the working edirectory inside the container 
WORKDIR /app

# Copy the requirements file first (for caching layers)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY ./src ./src

# Expose the port that Uvicorn will run on
EXPOSE 8000

WORKDIR /app/src

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
