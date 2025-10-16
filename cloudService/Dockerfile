# --- Stage 1: The "Builder" ---
# Use the official Python 3.12 image to get the correct Python version and build tools.
FROM python:3.12 AS builder

# Combine apt-get commands in a single layer and clean up to reduce image size.
#RUN apt-get update && apt-get install -y --no-install-recommends \
#    build-essential \
#    gdal-bin \
#    libgdal-dev \
#    && rm -rf /var/lib/apt/lists/*

# Create and own the virtual environment directory.
RUN mkdir /venv && python3 -m venv /venv

# Copy only the requirements file first to leverage Docker's layer cache.
COPY /requirements.txt /requirements.txt

# Install Python dependencies into the virtual environment.
# Use the full path to pip and --no-cache-dir to keep the layer small.
RUN /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install --no-cache-dir -r /requirements.txt


# --- Stage 2: The "Final" Image ---
# Use the slim Python 3.12 image for a smaller final product.
FROM python:3.12-slim

## Install only the runtime dependencies for GDAL.
#RUN apt-get update && apt-get install -y --no-install-recommends \
#    gdal-bin \
#    && rm -rf /var/lib/apt/lists/*

# Copy the virtual environment from the builder stage and set correct ownership.
COPY --from=builder /venv /venv

# Copy your application code and set correct ownership.
COPY . .

# Set the working directory.
#WORKDIR /cloudBuildTest
WORKDIR /

# Tell the container to listen on port 8080 for web traffic.
EXPOSE 8080

# Run the web server using Gunicorn when the container launches.
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "main:app"]


