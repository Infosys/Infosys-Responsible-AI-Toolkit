FROM node:20.11.1

RUN node -v

RUN npm -v

USER root

RUN mkdir -p /app

WORKDIR /app

COPY package.json /app

RUN npm install --legacy-peer-deps
 
COPY . /app
 
EXPOSE 30055
 
ENTRYPOINT ["npm", "start" ]
