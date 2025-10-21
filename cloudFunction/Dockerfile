# Using your original base image
FROM python:3.12 AS builder

# ADDED: Set environment variables for non-interactive install and PDAL version
ENV DEBIAN_FRONTEND=noninteractive
ENV PDAL_VERSION=2.7.1

# ADDED: Step 1 - Install system dependencies required to build PDAL from source
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    libgdal-dev \
    libproj-dev \
    curl \
    unzip && \
    rm -rf /var/lib/apt/lists/*

# ADDED: Step 2 - Download, compile, and install the PDAL C++ library
WORKDIR /build
RUN curl -L -o pdal.zip https://github.com/PDAL/PDAL/releases/download/${PDAL_VERSION}/PDAL-${PDAL_VERSION}-src.zip && \
    unzip pdal.zip && \
    cd PDAL-${PDAL_VERSION}-src && \
    mkdir build && \
    cd build && \
    cmake .. \
        -DBUILD_PLUGIN_PYTHON=ON \
        -DWITH_LASZIP=ON && \
    make -j$(nproc) && \
    make install

# Your original steps for creating a venv and installing dependencies
RUN python3 -m venv /venv

COPY requirements.txt requirements.txt
# MODIFIED: Correctly use the pip from the virtual environment.
# The `source` or `.` command does not persist between RUN layers in Docker.
RUN /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install -r requirements.txt

# Your original steps for copying the project and setting the workdir
COPY ./** /cloudFunction/
WORKDIR /cloudFunction







#FROM pdal/pdal:latest AS base
#
## Create a virtualenv
#RUN python3 -m venv /venv
#
## Install project dependencies
#COPY requirements.txt requirements.txt
#RUN . /venv/bin/activate &&  \
#    pip install --upgrade pip && \
#    pip install -r requirements.txt
#
## Copy project files into the container
#COPY ./** /cloudFunction/
#
## Set the working directory
#WORKDIR /cloudFunction


