FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY requirements.txt .
COPY *.py ./
COPY server/ ./server/
COPY models.py ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create debug_env package structure
RUN mkdir -p debug_env && \
    touch debug_env/__init__.py && \
    cp models.py debug_env/

# Expose port for Gradio app
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:7860/api/predict || exit 1

# Default command: run the Gradio app
CMD ["python", "app.py"]
