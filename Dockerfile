# Use Python 3.10
FROM python:3.10.13-slim

# Set working directory inside container
WORKDIR /app

# Copy all project files to container
COPY . /app

# Upgrade pip & setuptools & wheel
RUN pip install --upgrade pip setuptools wheel

# Install dependencies
RUN pip install -r requirements.txt

# Expose port (Render will use this port)
EXPOSE 10000

# Start FastAPI app with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
