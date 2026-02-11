# Use official Python image as base
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        libglib2.0-0 \
        libnss3 \
        # libgconf-2-4 removed (not available in Debian trixie) \
        libfontconfig1 \
        libxss1 \
        libasound2 \
        libatk1.0-0 \
        libatk-bridge2.0-0 \
        libcups2 \
        libdrm2 \
        libxcomposite1 \
        libxdamage1 \
        libxrandr2 \
        libgbm1 \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
        libx11-xcb1 \
        libxext6 \
        libxfixes3 \
        wget \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY req.txt ./

# Install Python dependencies
RUN pip install playwright && playwright install --with-deps chromium
RUN pip install --no-cache-dir -r req.txt

# Copy project files
COPY . .

# Expose port (if needed)
EXPOSE 8000

# Set default command (update as needed)
CMD ["python", "main.py"]
