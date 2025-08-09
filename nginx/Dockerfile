FROM nginx:alpine

# Copy nginx configurations
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY nginx-http-only.conf /etc/nginx/conf.d/http-only.conf

# Create SSL directory for certificates
RUN mkdir -p /etc/nginx/ssl

# Copy startup script
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]