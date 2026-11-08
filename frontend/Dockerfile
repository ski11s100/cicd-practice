FROM nginx:stable-alpine

LABEL org.opencontainers.image.source=https://github.com/ski11s100/cicd-practice

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY index.html app.js style.css /usr/share/nginx/html/
