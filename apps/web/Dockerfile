# Next.js Web Dockerfile
FROM node:20-alpine AS builder
WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./
RUN npm ci || npm install

# Copy application files
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV PORT=10000

# Copy necessary files from builder
COPY --from=builder /app/package.json ./
COPY --from=builder /app/package-lock.json* ./
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
# Copy public directory if it exists
COPY --from=builder /app/public* ./public/

EXPOSE ${PORT}

# Use PORT environment variable from Render
CMD ["sh", "-c", "npm run start -- -p ${PORT:-10000}"]
