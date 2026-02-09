# Stage 1: Build Next.js app
FROM node:22-alpine AS builder
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile
COPY . .
RUN pnpm run build

# Stage 2: Production image
FROM node:22-alpine
WORKDIR /app
COPY --from=builder /app .
RUN corepack enable && pnpm install --prod --frozen-lockfile
ENV NODE_ENV=production
EXPOSE 3000
CMD ["pnpm", "start"]
