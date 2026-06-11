FROM node:20-slim

WORKDIR /app

# Install dependencies and copy source
COPY frontend/package*.json ./
RUN npm ci --no-audit --no-fund
COPY frontend/ ./

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
