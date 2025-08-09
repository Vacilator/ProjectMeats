#!/bin/sh
# Smart nginx entrypoint that checks for SSL certificates

set -e

SSL_CERT="/etc/nginx/ssl/cert.pem"
SSL_KEY="/etc/nginx/ssl/key.pem"

echo "🔍 Checking SSL certificate availability..."

# Check if SSL certificates exist and are readable
if [ -f "$SSL_CERT" ] && [ -f "$SSL_KEY" ]; then
    echo "✅ SSL certificates found, enabling HTTPS configuration"
    
    # Validate certificate files
    if openssl x509 -in "$SSL_CERT" -noout -checkend 86400; then
        echo "✅ SSL certificate is valid"
        # Use the main nginx.conf which includes HTTPS
        cp /etc/nginx/conf.d/default.conf /etc/nginx/conf.d/main.conf
    else
        echo "⚠️  SSL certificate is expired or invalid, falling back to HTTP-only"
        cp /etc/nginx/conf.d/http-only.conf /etc/nginx/conf.d/default.conf
    fi
else
    echo "⚠️  SSL certificates not found, using HTTP-only configuration"
    echo "   To enable HTTPS:"
    echo "   1. Run ./setup_ssl.sh to generate certificates"
    echo "   2. Mount SSL directory with: -v ./ssl:/etc/nginx/ssl:ro"
    echo "   3. Restart the container"
    
    # Use HTTP-only configuration
    cp /etc/nginx/conf.d/http-only.conf /etc/nginx/conf.d/default.conf
fi

# Test nginx configuration
echo "🔧 Testing nginx configuration..."
nginx -t

echo "🚀 Starting nginx..."

# Execute the original command
exec "$@"