FROM node:22.19.0-alpine

# Set working directory
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy application code
COPY . .

# Expose port
EXPOSE 3001

# Set environment variable for Next.js to listen on all interfaces
ENV HOSTNAME="0.0.0.0"
ENV PORT=3001

# Start the development server
CMD ["npm", "run", "dev"]