# Use an official Node.js image as a base
FROM node:20-alpine

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json
COPY ilp-api/package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of your application code
COPY ./ilp-api .

# Expose the port your app runs on
EXPOSE 3001

# Run the app with npx tsx
CMD ["npx", "tsx", "./api/index.ts"]
