FROM node:18-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY public ./public
COPY src ./src
COPY tsconfig.json ./

ENV HOST=0.0.0.0
EXPOSE 3000

CMD ["npm", "start"]
