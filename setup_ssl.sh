#!/bin/bash
# SSL Certificate Setup for ProjectMeats
# This script helps set up SSL certificates for HTTPS

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SSL_DIR="$SCRIPT_DIR/ssl"
DOMAIN="${1:-localhost}"

echo "🔐 Setting up SSL certificates for ProjectMeats"
echo "Domain: $DOMAIN"
echo ""

# Create SSL directory if it doesn't exist
mkdir -p "$SSL_DIR"

# Function to create self-signed certificates for development
create_self_signed_cert() {
    echo "📝 Creating self-signed SSL certificate for development..."
    
    # Generate private key
    openssl genrsa -out "$SSL_DIR/key.pem" 2048
    
    # Generate certificate signing request
    openssl req -new -key "$SSL_DIR/key.pem" -out "$SSL_DIR/cert.csr" \
        -subj "/C=US/ST=State/L=City/O=ProjectMeats/OU=Development/CN=$DOMAIN"
    
    # Generate self-signed certificate
    openssl x509 -req -days 365 -in "$SSL_DIR/cert.csr" \
        -signkey "$SSL_DIR/key.pem" -out "$SSL_DIR/cert.pem" \
        -extensions v3_req -extfile <(cat <<EOF
[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = $DOMAIN
DNS.2 = www.$DOMAIN
DNS.3 = localhost
IP.1 = 127.0.0.1
EOF
)
    
    # Clean up CSR file
    rm "$SSL_DIR/cert.csr"
    
    echo "✅ Self-signed SSL certificate created at $SSL_DIR/"
    echo "   - Certificate: $SSL_DIR/cert.pem"
    echo "   - Private Key: $SSL_DIR/key.pem"
    echo ""
    echo "⚠️  Note: This is a self-signed certificate for development only."
    echo "   Browsers will show a security warning that you can bypass."
    echo ""
}

# Function to set up Let's Encrypt certificate (for production)
setup_letsencrypt() {
    echo "🌐 Setting up Let's Encrypt SSL certificate..."
    echo "This requires a valid domain and DNS pointing to your server."
    echo ""
    
    if ! command -v certbot &> /dev/null; then
        echo "Installing certbot..."
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            sudo apt-get update
            sudo apt-get install -y certbot
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            brew install certbot
        else
            echo "❌ Please install certbot manually for your operating system"
            exit 1
        fi
    fi
    
    echo "Obtaining certificate for domain: $DOMAIN"
    
    # Use standalone mode (requires port 80 to be free)
    sudo certbot certonly --standalone \
        -d "$DOMAIN" \
        -d "www.$DOMAIN" \
        --agree-tos \
        --non-interactive \
        --email "admin@$DOMAIN"
    
    # Copy certificates to SSL directory
    sudo cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" "$SSL_DIR/cert.pem"
    sudo cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" "$SSL_DIR/key.pem"
    sudo chown -R "$(whoami)" "$SSL_DIR"
    
    echo "✅ Let's Encrypt SSL certificate configured!"
}

# Function to copy existing certificates
copy_existing_cert() {
    echo "📁 Using existing SSL certificates..."
    
    read -p "Enter path to certificate file (.crt or .pem): " CERT_FILE
    read -p "Enter path to private key file (.key or .pem): " KEY_FILE
    
    if [[ ! -f "$CERT_FILE" ]] || [[ ! -f "$KEY_FILE" ]]; then
        echo "❌ Certificate files not found!"
        exit 1
    fi
    
    cp "$CERT_FILE" "$SSL_DIR/cert.pem"
    cp "$KEY_FILE" "$SSL_DIR/key.pem"
    
    echo "✅ SSL certificates copied to $SSL_DIR/"
}

# Main menu
echo "Choose SSL certificate setup option:"
echo "1) Create self-signed certificate (development)"
echo "2) Set up Let's Encrypt certificate (production)"
echo "3) Copy existing certificate files"
echo ""
read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        create_self_signed_cert
        ;;
    2)
        setup_letsencrypt
        ;;
    3)
        copy_existing_cert
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "🔧 Next steps:"
echo "1. Update your domain in nginx/nginx.conf (replace 'your_droplet_ip')"
echo "2. Run: docker-compose -f docker-compose.prod.yml up -d"
echo "3. Test HTTPS access: https://$DOMAIN"
echo ""
echo "📚 For production deployment, see HTTPS_SETUP.md"