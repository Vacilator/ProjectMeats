# Build stage
FROM node:16 AS builder
WORKDIR /app/frontend
COPY package.json package-lock.json ./
RUN npm install
COPY . .
RUN npm run build

# Production stage
FROM node:16-alpine
WORKDIR /app/frontend
COPY --from=builder /app/frontend/build ./build
RUN npm install -g serve
CMD ["serve", "-s", "build", "-l", "3000"]