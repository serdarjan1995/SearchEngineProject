FROM node:18

WORKDIR /app

COPY ./frontend/package.json ./frontend/package-lock.json* /app/

RUN npm install

COPY ./frontend /app

CMD ["npm", "start"]
