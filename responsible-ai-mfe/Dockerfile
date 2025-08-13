FROM infyartifactory.jfrog.io/responsibleai-mms-kubeflow/node:v20.11.1
 
RUN node -v
 
RUN npm -v
 
USER root
 
RUN mkdir -p /app
 
WORKDIR /app
 
COPY package.json /app
 
COPY .npmrc /app
 
RUN npm config set registry https://infyartifactory.jfrog.io/artifactory/api/npm/npm/

# RUN npm install -g npm@10.8.1
 
RUN npm install --legacy-peer-deps
 
COPY . /app
 
EXPOSE 30055
 
ENTRYPOINT ["npm", "start" ]
