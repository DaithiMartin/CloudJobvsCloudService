# --- Stage 1: The "Builder" ---
# Use the official Python 3.12 image to get the correct Python version and build tools.
FROM python:3.12 AS builder

# Create and own the virtual environment directory.
RUN mkdir /venv && python3 -m venv /venv

# Copy only the requirements file first to leverage Docker's layer cache.
COPY cloudService/requirements.txt /requirements.txt

# Install Python dependencies into the virtual environment.
# Use the full path to pip and --no-cache-dir to keep the layer small.
RUN /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install --no-cache-dir -r /requirements.txt


# --- Stage 2: The "Final" Image ---
# Use the slim Python 3.12 image for a smaller final product.
FROM python:3.12-slim

# Copy the virtual environment from the builder stage.
COPY --from=builder /venv /venv

# Set the working directory for the application.
WORKDIR /app

# Copy your application and shared code INTO the working directory.
# Python will automatically search for modules here.
COPY cloudService/main.py .
COPY src/ ./src/

# No PYTHONPATH needed because 'src' is inside the WORKDIR.

# Tell the container to listen on port 8080 for web traffic.
EXPOSE 8080

# Run the web server using the gunicorn executable from the virtual environment.
CMD ["/venv/bin/gunicorn", "--bind", "0.0.0.0:8080", "main:app"]