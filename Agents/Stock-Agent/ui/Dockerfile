# Development-only build for Next.js with Node 22
FROM node:22.19.0-alpine

# Install dependencies for development
RUN apk add --no-cache libc6-compat

WORKDIR /app

# Copy package files and install dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Copy source code
COPY . .

# Set environment for development
ENV NODE_ENV=development
ENV NEXT_TELEMETRY_DISABLED=1

# Expose development server port
EXPOSE 3000

# Run development server
CMD ["npm", "run", "dev"]