
FROM pdal/pdal:latest AS base

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential gdal-bin libgdal-dev

# Create a virtualenv
RUN python3 -m venv /venv

# Install project dependencies
COPY requirements.txt requirements.txt
RUN . /venv/bin/activate &&  \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy project files into the container
COPY ./** /cloudFunction/

# Set the working directory
WORKDIR /cloudFunction


