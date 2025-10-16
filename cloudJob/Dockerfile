# --- Stage 1: The "Builder" ---
FROM python:3.12 AS builder
RUN mkdir /venv && python3 -m venv /venv
COPY cloudJob/requirements.txt /requirements.txt
RUN /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install --no-cache-dir -r /requirements.txt

# --- Stage 2: The "Final" Image ---
FROM python:3.12-slim
COPY --from=builder /venv /venv

# Set the working directory for the application.
WORKDIR /app

# Copy your application and shared code INTO the working directory.
# Python will automatically search for modules here.
COPY cloudJob/cloudJob/ ./cloudJob/
COPY src/ ./src/

# No PYTHONPATH needed because 'src' is inside the WORKDIR.

# Run the 'cloudJob' module from the WORKDIR.
ENTRYPOINT ["/venv/bin/python", "-m", "cloudJob"]