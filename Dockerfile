# Base Image
FROM python:3.12-slim

# Working Directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Go to backend folder
WORKDIR /app/backend

# Flask Port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]