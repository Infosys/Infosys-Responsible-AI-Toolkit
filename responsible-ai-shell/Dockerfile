FROM infyartifactory.jfrog.io/responsibleai-mms-kubeflow/node:v20.11.1

RUN apt-get update && apt-get install -y nodejs npm

RUN node -v
RUN npm -v
 

RUN groupadd -r myuser && useradd -r -g myuser myuser
 

RUN mkdir -p /app
WORKDIR /app
 

COPY package.json /app
COPY .npmrc /app
 

RUN npm install --legacy-peer-deps

COPY . /app

EXPOSE 30010

USER myuser

ENTRYPOINT ["npm", "start"]
