# Start from the official Miniconda base image
FROM continuumio/miniconda3

# Set the name of the Conda environment
ENV CONDA_ENV_NAME=cloud-function-env

# Create the Conda environment and install packages in one RUN command.
# - 'conda create' makes the new environment.
# - 'conda install' adds the packages from the specified channel.
RUN conda create -n $CONDA_ENV_NAME python=3.12 pip && \
    conda install -n $CONDA_ENV_NAME -c conda-forge pdal --yes

# Copy the requirements.txt for pip packages
COPY requirements.txt requirements.txt

# Set the shell to automatically activate our Conda environment.
SHELL ["conda", "run", "-n", "$CONDA_ENV_NAME", "/bin/bash", "-c"]

# Install any additional packages from requirements.txt using pip
RUN pip install -r requirements.txt

# Copy project files into the container
COPY . /cloudFunction/

# Set the working directory
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


