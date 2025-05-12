FROM node:18

WORKDIR /app

COPY ./package.json ./package-lock.json* /app/

RUN npm install

COPY ./src /app/src
COPY ./public /app/public

CMD ["npm", "start"]
