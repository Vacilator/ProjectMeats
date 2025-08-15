#!/bin/bash
# ProjectMeats SSL Automation Script
# Automated SSL certificate generation and renewal with Let's Encrypt

set -euo pipefail

# Configuration
DOMAIN="${DOMAIN:-}"
EMAIL="${SSL_EMAIL:-}"
SSL_DIR="/opt/projectmeats/ssl"
WEBROOT="/var/www/html"
NGINX_CONTAINER="projectmeats-nginx"
STAGING=${STAGING:-false}

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Show usage
show_usage() {
    echo "ProjectMeats SSL Automation Script"
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -d, --domain DOMAIN      Domain name for SSL certificate"
    echo "  -e, --email EMAIL        Email address for Let's Encrypt"
    echo "  -s, --staging            Use Let's Encrypt staging environment"
    echo "  --renew                  Renew existing certificate"
    echo "  --check                  Check certificate status"
    echo "  -h, --help              Show this help"
    echo ""
    echo "Environment Variables:"
    echo "  DOMAIN                  Domain name"
    echo "  SSL_EMAIL               Email for Let's Encrypt"
    echo "  STAGING                 Use staging environment (true/false)"
}

# Check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        error "This script must be run as root"
        exit 1
    fi
}

# Install certbot if not present
install_certbot() {
    if ! command -v certbot &> /dev/null; then
        log "Installing certbot..."
        apt update
        apt install -y certbot python3-certbot-nginx
        success "Certbot installed successfully"
    else
        success "Certbot already installed"
    fi
}

# Validate domain DNS
validate_domain() {
    local domain="$1"
    
    log "Validating DNS for domain: $domain"
    
    # Get server IP
    local server_ip=$(curl -s ifconfig.me || curl -s ipinfo.io/ip || echo "unknown")
    
    # Check DNS resolution
    local dns_ip=$(dig +short A "$domain" @8.8.8.8 | head -n1)
    
    if [ -z "$dns_ip" ]; then
        error "Domain $domain does not resolve to any IP"
        return 1
    fi
    
    if [ "$dns_ip" = "$server_ip" ]; then
        success "DNS validation passed: $domain -> $server_ip"
        return 0
    else
        warning "DNS mismatch: $domain -> $dns_ip, server IP: $server_ip"
        warning "SSL certificate request may fail"
        return 1
    fi
}

# Generate self-signed certificate for testing
generate_self_signed() {
    local domain="$1"
    
    log "Generating self-signed certificate for $domain..."
    
    mkdir -p "$SSL_DIR"
    
    # Generate private key
    openssl genrsa -out "$SSL_DIR/key.pem" 2048
    
    # Generate certificate
    openssl req -new -x509 -key "$SSL_DIR/key.pem" -out "$SSL_DIR/cert.pem" -days 365 \
        -subj "/C=US/ST=State/L=City/O=Organization/OU=OrgUnit/CN=$domain"
    
    # Set permissions
    chmod 600 "$SSL_DIR/key.pem"
    chmod 644 "$SSL_DIR/cert.pem"
    
    success "Self-signed certificate generated"
    return 0
}

# Generate Let's Encrypt certificate
generate_letsencrypt() {
    local domain="$1"
    local email="$2"
    local staging="$3"
    
    log "Generating Let's Encrypt certificate for $domain..."
    
    # Build certbot command
    local certbot_args=("certbot" "certonly" "--webroot" "-w" "$WEBROOT" "-d" "$domain" "--email" "$email" "--agree-tos" "--non-interactive")
    
    if [ "$staging" = "true" ]; then
        certbot_args+=("--staging")
        log "Using Let's Encrypt staging environment"
    fi
    
    # Stop nginx temporarily to avoid conflicts
    docker stop "$NGINX_CONTAINER" 2>/dev/null || true
    
    # Run certbot
    if "${certbot_args[@]}"; then
        success "Let's Encrypt certificate generated successfully"
        
        # Copy certificates to SSL directory
        mkdir -p "$SSL_DIR"
        cp "/etc/letsencrypt/live/$domain/fullchain.pem" "$SSL_DIR/cert.pem"
        cp "/etc/letsencrypt/live/$domain/privkey.pem" "$SSL_DIR/key.pem"
        
        # Set permissions
        chmod 600 "$SSL_DIR/key.pem"
        chmod 644 "$SSL_DIR/cert.pem"
        
        # Start nginx
        docker start "$NGINX_CONTAINER" 2>/dev/null || true
        
        return 0
    else
        error "Let's Encrypt certificate generation failed"
        
        # Start nginx back up
        docker start "$NGINX_CONTAINER" 2>/dev/null || true
        
        # Fall back to self-signed certificate
        warning "Falling back to self-signed certificate"
        generate_self_signed "$domain"
        return 1
    fi
}

# Renew certificate
renew_certificate() {
    log "Renewing SSL certificates..."
    
    if certbot renew --quiet; then
        success "Certificate renewal successful"
        
        # Update certificates in SSL directory
        for domain_dir in /etc/letsencrypt/live/*/; do
            if [ -d "$domain_dir" ]; then
                local domain=$(basename "$domain_dir")
                cp "$domain_dir/fullchain.pem" "$SSL_DIR/cert.pem" 2>/dev/null || true
                cp "$domain_dir/privkey.pem" "$SSL_DIR/key.pem" 2>/dev/null || true
            fi
        done
        
        # Reload nginx
        docker restart "$NGINX_CONTAINER" 2>/dev/null || true
        
        return 0
    else
        warning "Certificate renewal failed or not needed"
        return 1
    fi
}

# Check certificate status
check_certificate() {
    local domain="$1"
    
    log "Checking certificate status for $domain..."
    
    if [ -f "$SSL_DIR/cert.pem" ]; then
        local expiry=$(openssl x509 -in "$SSL_DIR/cert.pem" -noout -enddate | cut -d= -f2)
        local days_until_expiry=$(( ( $(date -d "$expiry" +%s) - $(date +%s) ) / 86400 ))
        
        if [ "$days_until_expiry" -gt 30 ]; then
            success "Certificate is valid and expires in $days_until_expiry days"
        elif [ "$days_until_expiry" -gt 0 ]; then
            warning "Certificate expires in $days_until_expiry days - renewal recommended"
        else
            error "Certificate has expired $((days_until_expiry * -1)) days ago"
        fi
        
        # Show certificate details
        log "Certificate details:"
        openssl x509 -in "$SSL_DIR/cert.pem" -noout -subject -issuer -dates
        
    else
        error "No certificate found at $SSL_DIR/cert.pem"
        return 1
    fi
}

# Main function
main() {
    local action="generate"
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -d|--domain)
                DOMAIN="$2"
                shift 2
                ;;
            -e|--email)
                EMAIL="$2"
                shift 2
                ;;
            -s|--staging)
                STAGING=true
                shift
                ;;
            --renew)
                action="renew"
                shift
                ;;
            --check)
                action="check"
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Check requirements
    check_root
    install_certbot
    
    # Perform action
    case "$action" in
        "generate")
            if [ -z "$DOMAIN" ]; then
                error "Domain is required"
                show_usage
                exit 1
            fi
            
            if [ -z "$EMAIL" ]; then
                warning "Email not provided, using self-signed certificate"
                generate_self_signed "$DOMAIN"
            else
                validate_domain "$DOMAIN"
                generate_letsencrypt "$DOMAIN" "$EMAIL" "$STAGING"
            fi
            ;;
        "renew")
            renew_certificate
            ;;
        "check")
            if [ -z "$DOMAIN" ]; then
                error "Domain is required for certificate check"
                exit 1
            fi
            check_certificate "$DOMAIN"
            ;;
    esac
}

# Run main function with all arguments
main "$@"