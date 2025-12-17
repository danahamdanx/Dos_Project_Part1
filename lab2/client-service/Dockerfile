FROM nginx:stable-alpine

# Copy static files
COPY index.html /usr/share/nginx/html/index.html
COPY script.js /usr/share/nginx/html/script.js

# Copy custom Nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf
