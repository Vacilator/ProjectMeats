#!/bin/bash
# ProjectMeats Docker Diagnostics Collection Script
# Safe to run multiple times, does not require Docker to be running
# Collects canonical diagnostics for Docker startup failures

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

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARTIFACTS_DIR="${SCRIPT_DIR}/../../artifacts"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DIAGNOSTIC_TARBALL="${ARTIFACTS_DIR}/docker-diagnostics-${TIMESTAMP}.tar.gz"
TEMP_DIR="/tmp/docker-diagnostics-${TIMESTAMP}"

# Logging functions
log_header() { echo -e "\n${PURPLE}=== $1 ===${NC}"; }
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_divider() { echo -e "${WHITE}================================================${NC}"; }

# Safe command execution - doesn't fail script on command failure
safe_exec() {
    local cmd="$1"
    local description="$2"
    local output_file="$3"
    
    echo "# $description" >> "$output_file"
    echo "# Command: $cmd" >> "$output_file"
    echo "# Timestamp: $(date)" >> "$output_file"
    
    if eval "$cmd" >> "$output_file" 2>&1; then
        echo "# Exit code: 0" >> "$output_file"
        log_success "$description"
    else
        local exit_code=$?
        echo "# Exit code: $exit_code" >> "$output_file"
        log_warning "$description (exit code: $exit_code)"
    fi
    echo "" >> "$output_file"
}

# Initialize diagnostic collection
init_diagnostics() {
    log_header "Docker Diagnostics Collection - $(date)"
    
    # Create directories
    mkdir -p "$ARTIFACTS_DIR"
    mkdir -p "$TEMP_DIR"
    
    log_info "Diagnostic directory: $TEMP_DIR"
    log_info "Output tarball: $DIAGNOSTIC_TARBALL"
    log_divider
}

# System information collection
collect_system_info() {
    log_header "System Information"
    local output_file="$TEMP_DIR/system_info.txt"
    
    safe_exec "cat /etc/os-release" "Operating System Information" "$output_file"
    safe_exec "uname -a" "Kernel Information" "$output_file"
    safe_exec "systemd-detect-virt" "Virtualization Detection" "$output_file"
    safe_exec "df -h" "Disk Space" "$output_file"
    safe_exec "free -h" "Memory Information" "$output_file"
    safe_exec "lscpu | head -10" "CPU Information" "$output_file"
    safe_exec "id" "Current User Information" "$output_file"
    safe_exec "whoami" "Current User" "$output_file"
}

# Docker installation and configuration
collect_docker_info() {
    log_header "Docker Installation Analysis"
    local output_file="$TEMP_DIR/docker_info.txt"
    
    safe_exec "which docker" "Docker Binary Location" "$output_file"
    safe_exec "docker --version" "Docker Version" "$output_file"
    safe_exec "which dockerd" "Docker Daemon Binary Location" "$output_file"
    safe_exec "docker-compose --version" "Docker Compose Version (Legacy)" "$output_file"
    safe_exec "docker compose version" "Docker Compose Plugin Version" "$output_file"
    
    # Check Docker daemon configuration
    if [ -f "/etc/docker/daemon.json" ]; then
        safe_exec "cat /etc/docker/daemon.json" "Docker Daemon Configuration" "$output_file"
    else
        echo "# Docker daemon.json not found" >> "$output_file"
        log_info "Docker daemon.json not found (using defaults)"
    fi
    
    # Check Docker service files
    safe_exec "find /lib/systemd/system /etc/systemd/system -name '*docker*' -type f" "Docker Service Files" "$output_file"
}

# Docker service and systemd analysis
collect_service_info() {
    log_header "Docker Service Analysis"
    local output_file="$TEMP_DIR/service_info.txt"
    
    safe_exec "systemctl status docker" "Docker Service Status" "$output_file"
    safe_exec "systemctl is-enabled docker" "Docker Service Enabled Status" "$output_file"
    safe_exec "systemctl status containerd" "Containerd Service Status" "$output_file"
    safe_exec "systemctl is-enabled containerd" "Containerd Service Enabled Status" "$output_file"
    
    # Get recent journal entries
    safe_exec "journalctl -u docker --no-pager -n 50" "Docker Service Journal (Last 50 entries)" "$output_file"
    safe_exec "journalctl -u containerd --no-pager -n 20" "Containerd Service Journal (Last 20 entries)" "$output_file"
}

# Docker socket and runtime analysis
collect_runtime_info() {
    log_header "Docker Runtime Analysis"
    local output_file="$TEMP_DIR/runtime_info.txt"
    
    safe_exec "ls -la /var/run/docker*" "Docker Socket and PID Files" "$output_file"
    safe_exec "ls -la /var/lib/docker/" "Docker Data Directory" "$output_file"
    safe_exec "mount | grep docker" "Docker-related Mounts" "$output_file"
    safe_exec "ps aux | grep -E '(docker|containerd)'" "Docker-related Processes" "$output_file"
    
    # Check for conflicting services
    safe_exec "systemctl list-units | grep -E '(docker|containerd|podman)'" "Container Runtime Services" "$output_file"
}

# Network and security analysis
collect_network_security() {
    log_header "Network and Security Analysis"
    local output_file="$TEMP_DIR/network_security.txt"
    
    safe_exec "iptables -L -n | head -20" "Iptables Rules (first 20)" "$output_file"
    safe_exec "ip addr show" "Network Interfaces" "$output_file"
    safe_exec "ss -tulnp | grep -E '(docker|2375|2376)'" "Docker Network Ports" "$output_file"
    
    # Security modules
    safe_exec "aa-status" "AppArmor Status" "$output_file"
    safe_exec "sestatus" "SELinux Status" "$output_file"
    safe_exec "getenforce" "SELinux Enforcement Status" "$output_file"
}

# Docker daemon debug output (safe with timeout)
collect_docker_debug() {
    log_header "Docker Daemon Debug Output"
    local output_file="$TEMP_DIR/docker_debug.txt"
    
    log_info "Running dockerd --debug for 10 seconds..."
    echo "# Docker daemon debug output (10 second timeout)" >> "$output_file"
    echo "# Command: timeout 10s dockerd --debug" >> "$output_file"
    echo "# Timestamp: $(date)" >> "$output_file"
    
    # Use timeout to prevent hanging
    if timeout 10s dockerd --debug >> "$output_file" 2>&1; then
        log_success "Docker daemon debug completed normally"
    else
        local exit_code=$?
        if [ $exit_code -eq 124 ]; then
            log_info "Docker daemon debug terminated after 10 seconds (expected)"
            echo "# Terminated after 10 seconds (timeout)" >> "$output_file"
        else
            log_warning "Docker daemon debug failed with exit code: $exit_code"
            echo "# Exit code: $exit_code" >> "$output_file"
        fi
    fi
    echo "" >> "$output_file"
}

# Environment and package information
collect_environment() {
    log_header "Environment and Package Information"
    local output_file="$TEMP_DIR/environment.txt"
    
    safe_exec "env | grep -i docker | sort" "Docker Environment Variables" "$output_file"
    safe_exec "dpkg -l | grep -E '(docker|containerd)'" "Docker Packages (dpkg)" "$output_file"
    safe_exec "rpm -qa | grep -E '(docker|containerd)'" "Docker Packages (rpm)" "$output_file"
    safe_exec "which systemctl" "Systemctl Location" "$output_file"
    safe_exec "systemctl --version" "Systemd Version" "$output_file"
}

# Generate summary analysis
generate_summary() {
    log_header "Generating Diagnostic Summary"
    local summary_file="$TEMP_DIR/SUMMARY.txt"
    
    echo "ProjectMeats Docker Diagnostics Summary" > "$summary_file"
    echo "Generated: $(date)" >> "$summary_file"
    echo "Host: $(hostname)" >> "$summary_file"
    echo "User: $(whoami)" >> "$summary_file"
    echo "========================================" >> "$summary_file"
    echo "" >> "$summary_file"
    
    # Analyze key indicators
    echo "KEY INDICATORS:" >> "$summary_file"
    
    # Check if Docker is installed
    if command -v docker >/dev/null 2>&1; then
        echo "✓ Docker binary found: $(which docker)" >> "$summary_file"
    else
        echo "✗ Docker binary NOT found" >> "$summary_file"
    fi
    
    # Check if dockerd is available
    if command -v dockerd >/dev/null 2>&1; then
        echo "✓ Docker daemon binary found: $(which dockerd)" >> "$summary_file"
    else
        echo "✗ Docker daemon binary NOT found" >> "$summary_file"
    fi
    
    # Check service status
    if systemctl is-active --quiet docker; then
        echo "✓ Docker service is active" >> "$summary_file"
    else
        echo "✗ Docker service is NOT active" >> "$summary_file"
    fi
    
    # Check containerd
    if systemctl is-active --quiet containerd; then
        echo "✓ Containerd service is active" >> "$summary_file"
    else
        echo "✗ Containerd service is NOT active" >> "$summary_file"
    fi
    
    # Check socket
    if [ -S "/var/run/docker.sock" ]; then
        echo "✓ Docker socket exists" >> "$summary_file"
    else
        echo "✗ Docker socket does NOT exist" >> "$summary_file"
    fi
    
    # Check virtualization
    local virt_type=$(systemd-detect-virt 2>/dev/null || echo "unknown")
    echo "🖥️  Virtualization: $virt_type" >> "$summary_file"
    
    # Check disk space
    local disk_usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ "$disk_usage" -gt 90 ]; then
        echo "⚠️  Disk usage: ${disk_usage}% (HIGH - may cause issues)" >> "$summary_file"
    else
        echo "✓ Disk usage: ${disk_usage}% (OK)" >> "$summary_file"
    fi
    
    echo "" >> "$summary_file"
    echo "TOP SUSPECTED CAUSES:" >> "$summary_file"
    
    # Analyze patterns and suggest causes
    local suspected_causes=()
    
    # Check for containerd issues
    if ! systemctl is-active --quiet containerd; then
        suspected_causes+=("Containerd service failure - Docker depends on containerd")
    fi
    
    # Check for daemon.json issues
    if [ -f "/etc/docker/daemon.json" ]; then
        if ! python3 -m json.tool /etc/docker/daemon.json >/dev/null 2>&1; then
            suspected_causes+=("Malformed /etc/docker/daemon.json configuration")
        fi
    fi
    
    # Check virtualization issues
    case "$virt_type" in
        "openvz"|"lxc")
            suspected_causes+=("LXC/OpenVZ virtualization may not support Docker properly")
            ;;
        "wsl")
            suspected_causes+=("WSL environment - may need Docker Desktop or special configuration")
            ;;
    esac
    
    # Check disk space
    if [ "$disk_usage" -gt 85 ]; then
        suspected_causes+=("Insufficient disk space (${disk_usage}% used)")
    fi
    
    # Check for stale files
    if [ -f "/var/run/docker.pid" ] && ! systemctl is-active --quiet docker; then
        suspected_causes+=("Stale Docker PID file exists while service is inactive")
    fi
    
    # Check for package issues
    if ! dpkg -l docker-ce >/dev/null 2>&1 && ! rpm -q docker-ce >/dev/null 2>&1; then
        suspected_causes+=("Docker package installation issues - no docker-ce package found")
    fi
    
    # Output suspected causes
    if [ ${#suspected_causes[@]} -eq 0 ]; then
        echo "No obvious issues detected - review detailed logs for subtle problems" >> "$summary_file"
    else
        for i in "${!suspected_causes[@]}"; do
            echo "$((i+1)). ${suspected_causes[i]}" >> "$summary_file"
        done
    fi
    
    echo "" >> "$summary_file"
    echo "RECOMMENDED ACTIONS:" >> "$summary_file"
    echo "1. Review detailed logs in the diagnostic tarball" >> "$summary_file"
    echo "2. Check Docker service journal: journalctl -u docker" >> "$summary_file"
    echo "3. Verify Docker installation: dpkg -l | grep docker" >> "$summary_file"
    echo "4. Test manual daemon start: sudo dockerd --debug" >> "$summary_file"
    echo "5. Check containerd status: systemctl status containerd" >> "$summary_file"
    
    # Display summary to stdout
    echo ""
    log_header "DIAGNOSTIC SUMMARY"
    cat "$summary_file"
    log_divider
}

# Create diagnostic tarball
create_tarball() {
    log_header "Creating Diagnostic Tarball"
    
    # Create tarball with all collected data
    if tar -czf "$DIAGNOSTIC_TARBALL" -C "$(dirname "$TEMP_DIR")" "$(basename "$TEMP_DIR")"; then
        log_success "Diagnostic tarball created: $DIAGNOSTIC_TARBALL"
        
        # Show tarball contents
        log_info "Tarball contents:"
        tar -tzf "$DIAGNOSTIC_TARBALL" | sed 's/^/  /'
        
        # Show tarball size
        local size=$(du -h "$DIAGNOSTIC_TARBALL" | cut -f1)
        log_info "Tarball size: $size"
    else
        log_error "Failed to create diagnostic tarball"
        return 1
    fi
}

# Cleanup temporary files
cleanup() {
    if [ -d "$TEMP_DIR" ]; then
        rm -rf "$TEMP_DIR"
        log_info "Cleaned up temporary directory: $TEMP_DIR"
    fi
}

# Main execution
main() {
    # Trap to ensure cleanup on exit
    trap cleanup EXIT
    
    init_diagnostics
    collect_system_info
    collect_docker_info
    collect_service_info
    collect_runtime_info
    collect_network_security
    collect_docker_debug
    collect_environment
    generate_summary
    create_tarball
    
    echo ""
    log_success "Docker diagnostics collection completed successfully"
    log_info "Artifact location: $DIAGNOSTIC_TARBALL"
    echo ""
}

# Run main function
main "$@"