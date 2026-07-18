# Use official Python slim runtime as parent image
FROM python:3.10-slim

# Set environment variables to prevent Python writing .pyc files and buffer logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container to /app
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files from local week3 folder to /app/week3
COPY . /app/week3/

# Add /app to the Python module search path
ENV PYTHONPATH=/app

# Expose port 8000
EXPOSE 8000

# Run uvicorn pointing to week3.main:app
CMD ["uvicorn", "week3.main:app", "--host", "0.0.0.0", "--port", "8000"]
