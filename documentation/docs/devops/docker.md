## Docker Overview

Docker is an open-source platform that enables developers to automate the deployment of applications inside lightweight, portable containers. Containers bundle the application code with its dependencies and environment, ensuring consistency across different environments, such as development, testing, and production. By using Docker, we can create reproducible and isolated environments that simplify the deployment process and enhance scalability.

### API Example

In our project, we have utilized Docker to containerize the API, making it easy to deploy and manage across various environments. Below is the Dockerfile used to create the container image for our API:

```dockerfile
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
```

This Dockerfile begins by pulling the official Python 3.9-slim image from Docker Hub, providing a lightweight base for our API. The working directory is set to `/app`, where the application code will reside. The `requirements.txt` file, containing the necessary dependencies, is copied into the container, and the required packages are installed using `pip`.

After the dependencies are installed, the rest of the application code is copied into the container. The `EXPOSE` instruction specifies that the container listens on port 80. Finally, the `CMD` instruction defines the command to start the API using Gunicorn, specifying that it should run on all available network interfaces (`0.0.0.0`) on port 80.

This setup ensures that our API is encapsulated in a consistent environment, ready for deployment across different stages of development and production.

## Docker Workflow

To push our Docker image to Azure Container Registry (ACR), we follow these steps:

**Build the Docker Image**

First, we build the Docker image using the `docker build` command. This command reads the `Dockerfile` in the current directory and creates an image based on its instructions.

```bash
docker build -t <image-name>:<tag> .
```

- `<image-name>`: The name we want to assign to the Docker image.
- `<tag>`: The version tag for the image (e.g., `v1.0.0`).

**Login to Azure Container Registry**

Authenticate Docker with our Azure Container Registry using the `az acr login` command.

```bash
az acr login --name <acr-name>
```

Alternatively, we can log in directly using Docker:

```bash
docker login <acr-name>.azurecr.io
```

- `<acr-name>`: This is the name of our Azure Container Registry.
- We are prompted to enter our username and password, which can be obtained from the Azure portal.

**Tag the Docker Image**

   Tag the Docker image with the ACR repository URL to prepare it for pushing. We replace `<acr-name>`, `<image-name>`, and `<tag>` with our specific details.

   ```bash
   docker tag <image-name>:<tag> <acr-name>.azurecr.io/<image-name>:<tag>
   ```

   - `<acr-name>`: The name of our Azure Container Registry.
   - `<image-name>`: The name of our Docker image.
   - `<tag>`: The version tag for the image.

**Push the Docker Image to ACR**

   Push the tagged Docker image to our Azure Container Registry using the `docker push` command.

   ```bash
   docker push <acr-name>.azurecr.io/<image-name>:<tag>
   ```

   - `<acr-name>`: The name of our Azure Container Registry.
   - `<image-name>`: The name of our Docker image.
   - `<tag>`: The version tag for the image.

**Verify the Image**

   After pushing, we can verify that the image has been successfully uploaded to ACR by listing the images in the registry.

   ```bash
   az acr repository list --name <acr-name> --output table
   ```

   - `<acr-name>`: The name of our Azure Container Registry.

This workflow ensures that our Docker image is built, tagged, and pushed to Azure Container Registry, making it available for deployment in our cloud environment.
