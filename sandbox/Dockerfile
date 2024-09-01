# Use and official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the requirement file into the container 
COPY requirements.txt ./ 

# Install any dependencies specified in the requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . . 

# Run the python script wen the container launches
CMD ["python", "main.py"]
