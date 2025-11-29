# Dockerfile
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (needed for some Python packages)
RUN apt-get update && apt-get install -y build-essential

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Force Python to run in unbuffered mode (so logs show up instantly)
ENV PYTHONUNBUFFERED=1

# Expose port 8080 (Required for Cloud Run)
ENV PORT=8080

# Run the ADK server using the Shell Form
# This explicitly binds to 0.0.0.0 to ensure external access works
CMD adk web namer_agent --host 0.0.0.0 --port 8080
