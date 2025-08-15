#!/bin/bash
# DNS Configuration Helper for ProjectMeats Deployment
# Automates DNS A record setup via DigitalOcean API or provides manual instructions

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m' 
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_header() { echo -e "\n${PURPLE}================================${NC}"; echo -e "${PURPLE}$1${NC}"; echo -e "${PURPLE}================================${NC}"; }

# Default values
DOMAIN=""
SERVER_IP=""
DO_TOKEN="${DO_TOKEN:-}"

# Usage function
usage() {
    echo "Usage: $0 --domain DOMAIN --ip SERVER_IP [--do-token TOKEN]"
    echo ""
    echo "Options:"
    echo "  --domain DOMAIN    Domain name to configure (e.g., meatscentral.com)"
    echo "  --ip SERVER_IP     Server IP address (e.g., 167.99.155.140)"
    echo "  --do-token TOKEN   DigitalOcean API token (optional, will use DO_TOKEN env var)"
    echo "  --help             Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  DO_TOKEN           DigitalOcean API token for automatic DNS configuration"
    echo ""
    echo "Examples:"
    echo "  $0 --domain meatscentral.com --ip 167.99.155.140"
    echo "  DO_TOKEN=your_token $0 --domain meatscentral.com --ip 167.99.155.140"
    exit 1
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --domain)
            DOMAIN="$2"
            shift 2
            ;;
        --ip)
            SERVER_IP="$2"
            shift 2
            ;;
        --do-token)
            DO_TOKEN="$2"
            shift 2
            ;;
        --help)
            usage
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            ;;
    esac
done

# Validate required parameters
if [[ -z "$DOMAIN" || -z "$SERVER_IP" ]]; then
    log_error "Missing required parameters"
    usage
fi

log_header "DNS Configuration for $DOMAIN -> $SERVER_IP"

# Function to check if doctl is installed
check_doctl() {
    if command -v doctl >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to install doctl
install_doctl() {
    log_info "Installing doctl (DigitalOcean CLI)..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        wget -O /tmp/doctl.tar.gz https://github.com/digitalocean/doctl/releases/download/v1.104.0/doctl-1.104.0-linux-amd64.tar.gz
        tar xf /tmp/doctl.tar.gz -C /tmp/
        sudo mv /tmp/doctl /usr/local/bin/
        rm /tmp/doctl.tar.gz
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew >/dev/null 2>&1; then
            brew install doctl
        else
            log_error "Please install Homebrew first or install doctl manually"
            return 1
        fi
    else
        log_error "Unsupported OS for automatic doctl installation"
        log_info "Please install doctl manually from: https://github.com/digitalocean/doctl/releases"
        return 1
    fi
    
    log_success "doctl installed successfully"
}

# Function to create DNS A record via DigitalOcean API
create_do_dns_record() {
    local domain="$1"
    local ip="$2"
    local token="$3"
    
    log_info "Attempting to create DNS A record via DigitalOcean API..."
    
    # Check if doctl is installed
    if ! check_doctl; then
        log_warning "doctl not found, attempting to install..."
        if ! install_doctl; then
            return 1
        fi
    fi
    
    # Configure doctl with token
    echo "$token" | doctl auth init --access-token -
    
    # Check if domain exists in DigitalOcean
    if ! doctl domains get "$domain" >/dev/null 2>&1; then
        log_warning "Domain $domain not found in DigitalOcean. Creating domain..."
        if ! doctl domains create "$domain" --ip-address "$ip"; then
            log_error "Failed to create domain in DigitalOcean"
            return 1
        fi
        log_success "Domain $domain created in DigitalOcean"
    fi
    
    # Create or update A record
    log_info "Creating/updating A record: $domain -> $ip"
    
    # Remove existing A record if it exists
    if doctl domains records list "$domain" --format ID,Type,Name,Data --no-header | grep -q "A.*@.*"; then
        local record_id=$(doctl domains records list "$domain" --format ID,Type,Name,Data --no-header | grep "A.*@.*" | awk '{print $1}')
        log_info "Removing existing A record (ID: $record_id)"
        doctl domains records delete "$domain" "$record_id" --force
    fi
    
    # Create new A record
    if doctl domains records create "$domain" --record-type A --record-name @ --record-data "$ip" --record-ttl 300; then
        log_success "✅ A record created successfully: $domain -> $ip"
        
        # Also create www subdomain
        log_info "Creating www subdomain record..."
        if doctl domains records list "$domain" --format ID,Type,Name,Data --no-header | grep -q "A.*www.*"; then
            local www_record_id=$(doctl domains records list "$domain" --format ID,Type,Name,Data --no-header | grep "A.*www.*" | awk '{print $1}')
            log_info "Removing existing www A record (ID: $www_record_id)"
            doctl domains records delete "$domain" "$www_record_id" --force
        fi
        
        doctl domains records create "$domain" --record-type A --record-name www --record-data "$ip" --record-ttl 300
        log_success "✅ www A record created successfully: www.$domain -> $ip"
        
        return 0
    else
        log_error "Failed to create A record"
        return 1
    fi
}

# Function to provide manual DNS configuration instructions
provide_manual_instructions() {
    local domain="$1"
    local ip="$2"
    
    log_header "Manual DNS Configuration Required"
    echo ""
    echo "Since automatic DNS configuration is not available, please configure DNS manually:"
    echo ""
    echo "${WHITE}Step 1: Access Your Domain Registrar${NC}"
    echo "  - Go to your domain registrar's website (GoDaddy, Namecheap, Cloudflare, etc.)"
    echo "  - Log into your account"
    echo "  - Navigate to DNS management for $domain"
    echo ""
    echo "${WHITE}Step 2: Add A Records${NC}"
    echo "  - Add an A record:"
    echo "    ${CYAN}Name/Host:${NC} @ (or leave blank for root domain)"
    echo "    ${CYAN}Type:${NC} A"
    echo "    ${CYAN}Value/Points to:${NC} $ip"
    echo "    ${CYAN}TTL:${NC} 300 (5 minutes) or default"
    echo ""
    echo "  - Add a www A record:"
    echo "    ${CYAN}Name/Host:${NC} www"
    echo "    ${CYAN}Type:${NC} A"
    echo "    ${CYAN}Value/Points to:${NC} $ip"
    echo "    ${CYAN}TTL:${NC} 300 (5 minutes) or default"
    echo ""
    echo "${WHITE}Step 3: Wait for Propagation${NC}"
    echo "  - DNS changes can take 5 minutes to 48 hours to propagate"
    echo "  - Check propagation status at: https://dnschecker.org/#A/$domain"
    echo ""
    echo "${WHITE}Step 4: Verify Configuration${NC}"
    echo "  - Test with: ${CYAN}dig +short A $domain${NC}"
    echo "  - Expected result: $ip"
    echo ""
}

# Main execution
main() {
    # Try automatic DNS configuration if DO_TOKEN is provided
    if [[ -n "$DO_TOKEN" ]]; then
        log_info "DigitalOcean token provided, attempting automatic DNS configuration..."
        
        if create_do_dns_record "$DOMAIN" "$SERVER_IP" "$DO_TOKEN"; then
            log_success "✅ Automatic DNS configuration completed!"
            echo ""
            log_info "DNS propagation usually takes 5-15 minutes for DigitalOcean."
            log_info "You can monitor propagation at: https://dnschecker.org/#A/$DOMAIN"
            echo ""
            log_info "To verify locally, run: dig +short A $DOMAIN"
            return 0
        else
            log_warning "Automatic DNS configuration failed, falling back to manual instructions..."
        fi
    else
        log_info "No DigitalOcean token provided (DO_TOKEN environment variable)"
        log_info "To enable automatic DNS configuration, set DO_TOKEN environment variable"
    fi
    
    # Provide manual configuration instructions
    provide_manual_instructions "$DOMAIN" "$SERVER_IP"
    
    # Wait for user to complete manual configuration
    echo ""
    read -p "Press Enter after you have configured DNS manually..."
    
    # Verify DNS configuration
    log_info "Verifying DNS configuration..."
    
    max_attempts=5
    attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        log_info "Checking DNS resolution (attempt $attempt/$max_attempts)..."
        
        # Use dig to check A record
        if command -v dig >/dev/null 2>&1; then
            result=$(dig +short A "$DOMAIN" | head -1)
            
            if [[ "$result" == "$SERVER_IP" ]]; then
                log_success "✅ DNS correctly configured: $DOMAIN -> $result"
                return 0
            elif [[ -n "$result" ]]; then
                log_warning "DNS resolves to $result (expected $SERVER_IP)"
            else
                log_warning "No A record found for $DOMAIN"
            fi
        else
            log_warning "dig command not available for verification"
            log_info "Please verify manually that $DOMAIN resolves to $SERVER_IP"
        fi
        
        if [[ $attempt -lt $max_attempts ]]; then
            log_info "Waiting 60 seconds before next attempt..."
            sleep 60
        fi
        
        ((attempt++))
    done
    
    log_warning "DNS verification incomplete after $max_attempts attempts"
    log_info "This may be normal if DNS propagation is still in progress"
    log_info "Monitor at: https://dnschecker.org/#A/$DOMAIN"
}

# Run main function
main "$@"