#!/bin/bash

# Clone the repository
git clone --depth=2 --recursive https://github.com/kahypar/mt-kahypar.git
cd mt-kahypar

# Create build directory and navigate into it
mkdir -p build && cd build

# Install dependencies
sudo apt-get install -y libboost-all-dev libtbb-dev cmake

# Run CMake to configure the build
cmake .. -DCMAKE_BUILD_TYPE=RELEASE

# Optionally, if you want to download Boost during the build process
# cmake .. -DCMAKE_BUILD_TYPE=RELEASE -DKAHYPAR_DOWNLOAD_BOOST=On

# Build the project using make with the specified number of concurrent jobs
make MtKaHyPar -j2

# Build the Python bindings
make mtkahypar_python

# Copy the Python module to the virtual environment's site-packages directory
cp python/mtkahypar.cpython-311-x86_64-linux-gnu.so ../../venv/lib/python3.11/site-packages

# Navigate back to the parent directory
cd ..
