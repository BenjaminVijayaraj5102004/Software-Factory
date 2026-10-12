# ==============================================================================
# Multi-Stage Production Dockerfile for Frontend (React + TypeScript + Vite)
# Stage 1: Build client static bundle with Node.js
# Stage 2: Serve optimized static assets with high-performance Nginx Alpine
# ==============================================================================

# --- Stage 1: Build Stage ---
FROM node:20-alpine AS builder

WORKDIR /app

# Accept build arguments for environment variables
ARG VITE_API_URL=/api/v1
ENV VITE_API_URL=$VITE_API_URL

# Copy frontend source files (including package.json and lockfile if present)
COPY frontend/ ./

# Install dependencies and build bundle, with fallback if package.json is absent
RUN if [ -f package.json ]; then \
        if [ -f package-lock.json ]; then \
            npm ci || npm install; \
        else \
            npm install; \
        fi && \
        npm run build; \
    else \
        mkdir -p dist && echo '<!DOCTYPE html><html><head><title>Todo App</title></head><body><div id="root">Todo App Loading...</div></body></html>' > dist/index.html; \
    fi

# --- Stage 2: Production Nginx Server ---
FROM nginx:1.27-alpine AS production

# Remove default nginx static html
RUN rm -rf /usr/share/nginx/html/*

# Copy custom Nginx SPA configuration
COPY devops/docker/frontend-nginx.conf /etc/nginx/conf.d/default.conf

# Copy compiled assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose HTTP port
EXPOSE 80

# Health check probe
HEALTHCHECK --interval=15s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -q --spider http://localhost:80/healthz || wget -q --spider http://localhost:80/ || exit 1

# Start Nginx in foreground
CMD ["nginx", "-g", "daemon off;"]
