# Stage 1: Build React Frontend
FROM node:18-alpine as build-frontend
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Final Image
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/
COPY main.py .

# Copy built frontend from Stage 1
COPY --from=build-frontend /app/frontend/dist ./frontend/dist

# Expose port (default for specialized services often 8080 or determined by env)
EXPOSE 8080

# Environment variable for port
ENV PORT=8080

# Run the app
CMD ["sh", "-c", "uvicorn backend.api:app --host 0.0.0.0 --port $PORT"]
