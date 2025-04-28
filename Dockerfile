# Use an official Python run time as a base image 
FROM python:3.12-slim

# SET the working directory inside the container 
WORKDIR /app

# Copy the requirements file first (for caching layers)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY ./backend ./backend

# Expose the port that Uvicorn will run on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]