FROM node:16.14.0-alpine AS build

COPY frontend/package.json /usr/local/src/frontend/package.json
COPY frontend/package-lock.json /usr/local/src/frontend/package-lock.json
COPY frontend/tailwind.config.js /usr/local/src/frontend/tailwind.config.js
WORKDIR /usr/local/src/frontend
RUN npm install --production

COPY frontend/ /usr/local/src/frontend
RUN npm run build

FROM nginx:1.20-alpine

COPY --from=build /usr/local/src/frontend/build /usr/share/nginx/html

COPY docker/nginx.conf.template /etc/nginx/templates/default.conf.template
COPY static /usr/share/nginx/html/static/
