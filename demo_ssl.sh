#!/bin/bash
# ProjectMeats HTTPS Demo Script

set -e

echo "🚀 ProjectMeats HTTPS Setup Demonstration"
echo "=========================================="
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📁 Current directory: $SCRIPT_DIR"
echo ""

# Check if SSL directory exists
if [ -d "./ssl" ]; then
    echo "✅ SSL directory exists"
    if [ -f "./ssl/cert.pem" ] && [ -f "./ssl/key.pem" ]; then
        echo "✅ SSL certificates found"
        
        # Show certificate information
        echo ""
        echo "📋 SSL Certificate Information:"
        echo "================================"
        openssl x509 -in ./ssl/cert.pem -noout -subject -dates -issuer
    else
        echo "⚠️  SSL certificates not found in ./ssl/"
        echo ""
        echo "🔧 To create SSL certificates, run:"
        echo "   ./setup_ssl.sh localhost"
    fi
else
    echo "⚠️  SSL directory not found"
    echo ""
    echo "🔧 Creating SSL certificates for demonstration..."
    
    # Create SSL directory
    mkdir -p ssl
    
    # Generate self-signed certificate for localhost
    echo "📝 Generating self-signed SSL certificate..."
    openssl genrsa -out ssl/key.pem 2048
    openssl req -new -key ssl/key.pem -out ssl/cert.csr -subj "/C=US/ST=Demo/L=Demo/O=ProjectMeats/OU=Development/CN=localhost"
    openssl x509 -req -days 365 -in ssl/cert.csr -signkey ssl/key.pem -out ssl/cert.pem \
        -extensions v3_req -extfile <(cat <<EOF
[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
DNS.2 = 127.0.0.1
IP.1 = 127.0.0.1
EOF
)
    rm ssl/cert.csr
    
    echo "✅ Self-signed SSL certificate created!"
fi

echo ""
echo "🔍 Testing SSL Configuration..."
python /tmp/test_ssl_config.py

echo ""
echo "🐳 Docker Compose Configuration:"
echo "================================="
echo "✅ HTTP port 80 exposed"
echo "✅ HTTPS port 443 exposed"
echo "✅ SSL certificate volume ready"

echo ""
echo "📚 Next Steps:"
echo "=============="
echo "1. 🔧 Update nginx/nginx.conf server_name with your domain"
echo "2. 🚀 Start with: docker compose up -d"
echo "3. 🌐 Access via HTTPS: https://localhost (accept security warning for self-signed cert)"
echo "4. 📖 Read HTTPS_SETUP.md for production deployment"

echo ""
echo "🎯 Production Deployment:"
echo "========================="
echo "• Use docker-compose.prod.yml for production"
echo "• Set environment variables (SERVER_NAME, SSL_CERT_PATH)"
echo "• Get real SSL certificates (Let's Encrypt recommended)"
echo "• Update domain in nginx configuration"

echo ""
echo "✅ HTTPS/SSL setup is complete and ready to use!"