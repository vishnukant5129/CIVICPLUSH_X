# CivicPulse AI — Frontend Dockerfile
# =====================================
# No secrets are baked into this image.

FROM node:22-slim AS base

WORKDIR /app

# Copy package files and install dependencies
COPY package.json package-lock.json* ./
RUN npm ci

# Copy application source
COPY . .

# Expose Vite dev server port
EXPOSE 5173

# Start Vite dev server (accessible from Docker network)
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
