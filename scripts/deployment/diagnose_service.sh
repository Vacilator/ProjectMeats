#!/bin/bash
# Diagnostic script for DNS and firewall issues during deployment
# Provides comprehensive diagnostics for external domain access issues

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
PROJECT_DIR=""

# Usage function
usage() {
    echo "Usage: $0 --domain DOMAIN --ip SERVER_IP [--project-dir DIR]"
    echo ""
    echo "Options:"
    echo "  --domain DOMAIN       Domain to diagnose (e.g., meatscentral.com)"
    echo "  --ip SERVER_IP        Expected server IP address"
    echo "  --project-dir DIR     Project directory path (optional)"
    echo "  --help                Show this help message"
    echo ""
    echo "Example:"
    echo "  $0 --domain meatscentral.com --ip 167.99.155.140"
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
        --project-dir)
            PROJECT_DIR="$2"
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

log_header "DNS and Firewall Diagnostics for $DOMAIN"

# DNS Diagnostics
log_header "🔍 DNS Diagnostics"

log_info "Checking DNS resolution with different methods..."

# Method 1: dig (if available)
if command -v dig >/dev/null 2>&1; then
    log_info "Using dig to check A record:"
    dig_result=$(dig +short A "$DOMAIN" 2>/dev/null || echo "FAILED")
    if [[ "$dig_result" != "FAILED" && -n "$dig_result" ]]; then
        echo "  $dig_result"
        if [[ "$dig_result" == "$SERVER_IP" ]]; then
            log_success "✅ DNS resolves correctly via dig"
        else
            log_warning "⚠️ DNS resolves to different IP: $dig_result (expected $SERVER_IP)"
        fi
    else
        log_error "❌ DNS resolution failed via dig"
    fi
    
    log_info "Detailed dig output:"
    dig "$DOMAIN" A | grep -E "(ANSWER SECTION|$DOMAIN\."  || log_warning "No detailed dig output"
else
    log_warning "dig command not available"
fi

# Method 2: nslookup (if available)
if command -v nslookup >/dev/null 2>&1; then
    log_info "Using nslookup to check A record:"
    nslookup_result=$(nslookup "$DOMAIN" 2>/dev/null | grep "Address:" | tail -1 | awk '{print $2}' || echo "FAILED")
    if [[ "$nslookup_result" != "FAILED" && -n "$nslookup_result" ]]; then
        echo "  $nslookup_result"
        if [[ "$nslookup_result" == "$SERVER_IP" ]]; then
            log_success "✅ DNS resolves correctly via nslookup"
        else
            log_warning "⚠️ DNS resolves to different IP via nslookup"
        fi
    else
        log_error "❌ DNS resolution failed via nslookup"
    fi
else
    log_warning "nslookup command not available"
fi

# Method 3: host (if available)
if command -v host >/dev/null 2>&1; then
    log_info "Using host to check A record:"
    host_result=$(host "$DOMAIN" 2>/dev/null | grep "has address" | awk '{print $4}' || echo "FAILED")
    if [[ "$host_result" != "FAILED" && -n "$host_result" ]]; then
        echo "  $host_result"
        if [[ "$host_result" == "$SERVER_IP" ]]; then
            log_success "✅ DNS resolves correctly via host"
        else
            log_warning "⚠️ DNS resolves to different IP via host"
        fi
    else
        log_error "❌ DNS resolution failed via host"
    fi
else
    log_warning "host command not available"
fi

# External DNS check link
log_info "Check DNS propagation globally:"
log_info "  🌍 https://dnschecker.org/#A/$DOMAIN"
log_info "  🌍 https://www.whatsmydns.net/#A/$DOMAIN"

# Firewall Diagnostics
log_header "🔥 Firewall and Port Diagnostics"

log_info "Checking firewall status..."

# UFW status
if command -v ufw >/dev/null 2>&1; then
    log_info "UFW firewall status:"
    ufw status verbose 2>/dev/null || log_warning "Could not get UFW status"
else
    log_warning "UFW not installed"
fi

# iptables status
if command -v iptables >/dev/null 2>&1; then
    log_info "iptables rules (INPUT chain):"
    iptables -L INPUT -v -n 2>/dev/null | head -20 || log_warning "Could not get iptables rules"
else
    log_warning "iptables not available"
fi

# Port availability checks
log_header "🔌 Port and Service Diagnostics"

log_info "Checking if port 80 is listening..."

# Method 1: ss
if command -v ss >/dev/null 2>&1; then
    ss_result=$(ss -tuln | grep ":80 ")
    if [[ -n "$ss_result" ]]; then
        log_success "✅ Port 80 is listening (ss check):"
        echo "$ss_result" | while read line; do
            log_info "  $line"
        done
    else
        log_error "❌ Port 80 is not listening (ss check)"
    fi
else
    log_warning "ss command not available"
fi

# Method 2: netstat
if command -v netstat >/dev/null 2>&1; then
    netstat_result=$(netstat -tuln 2>/dev/null | grep ":80 ")
    if [[ -n "$netstat_result" ]]; then
        log_success "✅ Port 80 is listening (netstat check):"
        echo "$netstat_result"
    else
        log_error "❌ Port 80 is not listening (netstat check)"
    fi
else
    log_warning "netstat command not available"
fi

# Nginx service diagnostics
log_header "🌐 Nginx Service Diagnostics"

if systemctl is-active --quiet nginx 2>/dev/null; then
    log_success "✅ Nginx service is active"
else
    log_error "❌ Nginx service is not active"
    log_info "Nginx service status:"
    systemctl status nginx --no-pager -l 2>/dev/null || log_warning "Could not get nginx status"
fi

# Nginx configuration test
if command -v nginx >/dev/null 2>&1; then
    log_info "Testing nginx configuration:"
    if nginx -t 2>/dev/null; then
        log_success "✅ Nginx configuration is valid"
    else
        log_error "❌ Nginx configuration has errors:"
        nginx -t 2>&1 | head -10
    fi
    
    log_info "Nginx processes:"
    ps aux | grep nginx | grep -v grep || log_warning "No nginx processes found"
else
    log_warning "nginx command not available"
fi

# HTTP connectivity tests  
log_header "🌍 HTTP Connectivity Tests"

log_info "Testing direct IP connectivity..."
if command -v curl >/dev/null 2>&1; then
    # Test direct IP
    log_info "Direct IP test: http://$SERVER_IP"
    if curl -m 10 -I "http://$SERVER_IP" 2>/dev/null | head -1; then
        log_success "✅ Direct IP responds"
    else
        log_error "❌ Direct IP does not respond"
        log_info "This indicates server/nginx/firewall issues"
    fi
    
    # Test domain (if DNS resolves)
    log_info "Domain test: http://$DOMAIN"
    if curl -m 10 -I "http://$DOMAIN" 2>/dev/null | head -1; then
        log_success "✅ Domain responds"
    else
        log_error "❌ Domain does not respond"
        log_info "This could be DNS or server issues"
    fi
    
    # Test with DNS bypass
    log_info "DNS bypass test: --resolve $DOMAIN:80:$SERVER_IP"
    if curl --resolve "$DOMAIN:80:$SERVER_IP" -m 10 -I "http://$DOMAIN" 2>/dev/null | head -1; then
        log_success "✅ DNS bypass test works"
        log_info "Server is working, DNS may be the issue"
    else
        log_error "❌ DNS bypass test failed"
        log_info "Server/nginx/firewall issue likely"
    fi
else
    log_warning "curl command not available for HTTP tests"
fi

# System resource checks
log_header "💻 System Resource Diagnostics"

log_info "System load and memory:"
if command -v uptime >/dev/null 2>&1; then
    uptime
fi

if command -v free >/dev/null 2>&1; then
    free -h | head -2
fi

log_info "Disk space:"
if command -v df >/dev/null 2>&1; then
    df -h / | head -2
fi

# Log file analysis
log_header "📝 Log File Analysis"

if [[ -n "$PROJECT_DIR" ]]; then
    log_info "Checking project logs in $PROJECT_DIR..."
    
    if [[ -f "$PROJECT_DIR/logs/nginx_error.log" ]]; then
        log_info "Recent nginx errors:"
        tail -10 "$PROJECT_DIR/logs/nginx_error.log" 2>/dev/null || log_info "No recent nginx errors"
    fi
    
    if [[ -f "/var/log/nginx/error.log" ]]; then
        log_info "System nginx errors:"
        tail -10 /var/log/nginx/error.log 2>/dev/null || log_info "No recent system nginx errors"
    fi
else
    log_info "Project directory not specified, checking system logs..."
fi

# System nginx logs
if [[ -f "/var/log/nginx/error.log" ]]; then
    log_info "Recent system nginx errors:"
    tail -10 /var/log/nginx/error.log 2>/dev/null | grep -v "access forbidden" || log_info "No critical nginx errors"
fi

# System messages
if [[ -f "/var/log/syslog" ]]; then
    log_info "Recent system messages related to nginx or ufw:"
    tail -50 /var/log/syslog 2>/dev/null | grep -E "(nginx|ufw)" | tail -5 || log_info "No recent relevant system messages"
fi

# Summary and recommendations
log_header "📋 Summary and Recommendations"

log_info "Based on the diagnostics above:"
log_info ""
log_info "1. DNS Issues:"
log_info "   - If DNS doesn't resolve to $SERVER_IP, configure A record"
log_info "   - Check https://dnschecker.org/#A/$DOMAIN for propagation"
log_info "   - DNS can take up to 48 hours to propagate globally"
log_info ""
log_info "2. Port/Firewall Issues:"
log_info "   - If port 80 isn't listening, check nginx configuration"
log_info "   - If UFW is blocking, ensure 'Nginx Full' is allowed"
log_info "   - If iptables has rules, ensure port 80 is open"
log_info ""
log_info "3. Server Issues:"
log_info "   - If direct IP fails, check nginx service and configuration"
log_info "   - If DNS bypass works but domain doesn't, it's a DNS issue"
log_info "   - Check logs for specific error messages"
log_info ""
log_info "4. Next Steps:"
log_info "   - Fix DNS if needed using dns_config.sh script"
log_info "   - Restart nginx if configuration changed"
log_info "   - Check firewall rules if port issues persist"
log_info "   - Monitor logs for ongoing issues"

log_info ""
log_success "🏁 Diagnostics complete!"