# Base image with Python 3.10
FROM python:3.10.0-slim

# Set working directory
WORKDIR /app

# Copy all files to container
COPY . /app

# Upgrade pip & install dependencies
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# Expose port (Render will use this)
EXPOSE 10000

# Start FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
