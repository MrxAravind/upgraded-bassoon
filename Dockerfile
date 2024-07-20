# Use the appropriate Python base image
FROM python:3.10
# Upgrade pip
RUN pip install --upgrade pip
# Set working directory
WORKDIR /app
# Copy just the requirements file first to leverage Docker cache
COPY requirements.txt .
# Install dependencies
RUN pip install -r requirements.txt
# Copy the rest of the application code
COPY . .
# Set the entrypoint
CMD ["bash", "start.sh"]
