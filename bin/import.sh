#!/bin/bash

# Path to requirements file
REQUIREMENTS_FILE="$(dirname "$0")/../requirements.txt"

# Check for requirements file
if [ ! -f "$REQUIREMENTS_FILE" ]; then
  echo "Requirements file not found at $REQUIREMENTS_FILE"
  echo "Please make sure requirements.txt exists at the expected location."
  exit 1
fi

# Define pip function as pip3
pip() {
  pip3 "$@"
}

# Install libraries
echo "Installing required libraries..."
pip install -r "$REQUIREMENTS_FILE"

# Check if pip was successful
if [ $? -eq 0 ]; then
  echo "All libraries installed successfully."
else
  echo "An error occurred while installing libraries. Please check for errors above."
  exit 1
fi
