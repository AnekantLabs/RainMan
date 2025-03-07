# Use Node.js 20 as the base image
FROM node:20-alpine

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install --frozen-lockfile

# Copy the entire project
COPY . .

# Expose the port that the React development server runs on (default is 3000)
EXPOSE 3000

# Start the React development server
CMD ["npm", "run", "start"]
