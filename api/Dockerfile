# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy only the requirements file from the root
COPY ../requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy specific directories needed for service1
COPY ../api ./api
COPY ../database ./database
COPY ../whatsapp_utils ./whatsapp_utils

# Expose the port the app runs on
EXPOSE 80

# Define the command to run the application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:80", "api.app:app"]
