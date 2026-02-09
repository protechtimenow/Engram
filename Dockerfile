# Build stage
FROM node:22-alpine AS builder
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile
COPY . .
RUN pnpm run build

# Production stage
FROM node:22-alpine
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/pnpm-lock.yaml ./pnpm-lock.yaml
COPY --from=builder /app/next.config.js ./next.config.js 2>/dev/null || true
COPY --from=builder /app/next.config.ts ./next.config.ts 2>/dev/null || true
RUN corepack enable && pnpm install --prod --frozen-lockfile
EXPOSE 3000
ENV NODE_ENV=production
CMD ["pnpm", "start"]
