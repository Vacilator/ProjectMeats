#!/bin/bash
# ProjectMeats Node.js Conflict Fix Script
# 
# This script specifically addresses the Node.js/npm installation conflicts
# that have been causing deployment issues.
#
# Usage:
# curl -sSL https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/fix_nodejs.sh | sudo bash

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo "🔧 ProjectMeats Node.js Conflict Resolution Script"
echo "================================================="
echo ""
echo "This script will fix the Node.js/npm installation conflicts you've been experiencing:"
echo "  • nodejs : Conflicts: npm"
echo "  • npm : Depends: node-cacache but it is not going to be installed"
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    log_error "This script must be run as root (use sudo)"
    exit 1
fi

# Step 1: Stop all Node.js processes
log_info "Step 1: Stopping Node.js processes..."
pkill -f node || true
pkill -f npm || true
sleep 2

# Step 2: Complete package removal
log_info "Step 2: Removing ALL Node.js packages..."

# List of all possible Node.js related packages
PACKAGES_TO_REMOVE=(
    "nodejs"
    "npm" 
    "libnode-dev"
    "libnode72"
    "libnode108"
    "nodejs-doc"
    "node-gyp"
    "node-cacache"
    "node-mkdirp"
    "node-rimraf"
    "node-tar"
    "libnode64"
    "libnode93"
)

for package in "${PACKAGES_TO_REMOVE[@]}"; do
    log_info "Removing $package..."
    apt remove -y "$package" 2>/dev/null || true
    apt purge -y "$package" 2>/dev/null || true
done

# Step 3: Remove manually installed Node.js
log_info "Step 3: Cleaning manually installed Node.js..."

# Remove binaries
rm -rf /usr/local/bin/node* || true
rm -rf /usr/local/bin/npm* || true
rm -rf /usr/local/lib/node_modules || true
rm -rf /usr/bin/node* || true
rm -rf /usr/bin/npm* || true

# Remove configuration directories
rm -rf /etc/nodejs || true
rm -rf ~/.npm || true
rm -rf ~/.node-gyp || true

# Step 4: Clean package system
log_info "Step 4: Cleaning package system..."
apt autoremove -y
apt autoclean
apt clean

# Remove any problematic package holds
log_info "Removing package holds..."
apt-mark unhold nodejs npm 2>/dev/null || true

# Clear dpkg cache
rm -rf /var/lib/dpkg/info/nodejs* || true
rm -rf /var/lib/dpkg/info/npm* || true

# Reconfigure dpkg
dpkg --configure -a

# Update package database
apt update

log_success "System cleaned of all Node.js installations"

# Step 5: Install Node.js with multiple fallback methods
log_info "Step 5: Installing Node.js 18 LTS..."

# Method 1: NodeSource repository (preferred)
install_via_nodesource() {
    log_info "Attempting installation via NodeSource repository..."
    
    # Download and verify NodeSource setup script
    curl -fsSL https://deb.nodesource.com/setup_18.x -o /tmp/nodesource_setup.sh
    
    if [[ -f /tmp/nodesource_setup.sh ]] && [[ -s /tmp/nodesource_setup.sh ]]; then
        chmod +x /tmp/nodesource_setup.sh
        bash /tmp/nodesource_setup.sh
        
        # Update package list
        apt update
        
        # Install Node.js
        if apt install -y nodejs; then
            log_success "Node.js installed via NodeSource"
            return 0
        fi
    fi
    
    return 1
}

# Method 2: Snap package (fallback)
install_via_snap() {
    log_info "Attempting installation via Snap..."
    
    if command -v snap >/dev/null 2>&1; then
        if snap install node --classic; then
            # Create symlinks for system compatibility
            ln -sf /snap/bin/node /usr/local/bin/node 2>/dev/null || true
            ln -sf /snap/bin/npm /usr/local/bin/npm 2>/dev/null || true
            
            # Add to PATH for all users
            echo 'export PATH="/snap/bin:$PATH"' >> /etc/profile
            
            log_success "Node.js installed via Snap"
            return 0
        fi
    else
        log_warning "Snap not available"
    fi
    
    return 1
}

# Method 3: Ubuntu repositories (last resort)
install_via_apt() {
    log_info "Attempting installation via Ubuntu repositories..."
    
    if apt install -y nodejs npm; then
        log_warning "Node.js installed from Ubuntu repos (may be older version)"
        return 0
    fi
    
    return 1
}

# Method 4: Manual binary installation
install_manually() {
    log_info "Attempting manual binary installation..."
    
    # Detect architecture
    ARCH=$(uname -m)
    case $ARCH in
        x86_64) NODE_ARCH="x64" ;;
        aarch64) NODE_ARCH="arm64" ;;
        armv7l) NODE_ARCH="armv7l" ;;
        *) log_error "Unsupported architecture: $ARCH"; return 1 ;;
    esac
    
    # Download Node.js 18 LTS
    NODE_VERSION="v18.19.0"
    NODE_URL="https://nodejs.org/dist/$NODE_VERSION/node-$NODE_VERSION-linux-$NODE_ARCH.tar.xz"
    
    cd /tmp
    if wget -q "$NODE_URL" -O node.tar.xz; then
        tar -xf node.tar.xz
        
        # Install to /usr/local
        cd "node-$NODE_VERSION-linux-$NODE_ARCH"
        cp -r bin/* /usr/local/bin/
        cp -r lib/* /usr/local/lib/
        cp -r include/* /usr/local/include/ 2>/dev/null || true
        cp -r share/* /usr/local/share/ 2>/dev/null || true
        
        # Cleanup
        cd /tmp
        rm -rf node.tar.xz "node-$NODE_VERSION-linux-$NODE_ARCH"
        
        log_success "Node.js installed manually"
        return 0
    fi
    
    return 1
}

# Try installation methods in order
if install_via_nodesource; then
    INSTALL_METHOD="NodeSource"
elif install_via_snap; then
    INSTALL_METHOD="Snap"
elif install_via_apt; then
    INSTALL_METHOD="Ubuntu APT"
elif install_manually; then
    INSTALL_METHOD="Manual"
else
    log_error "All Node.js installation methods failed!"
    echo ""
    echo "Manual steps to try:"
    echo "1. Check your internet connection"
    echo "2. Try running this script again"
    echo "3. Manually download Node.js from https://nodejs.org/"
    echo ""
    exit 1
fi

# Step 6: Verify installation
log_info "Step 6: Verifying Node.js installation..."

# Force PATH update
export PATH="/usr/local/bin:/snap/bin:$PATH"

# Check Node.js version
if command -v node >/dev/null 2>&1; then
    NODE_VERSION=$(node --version)
    log_success "Node.js version: $NODE_VERSION"
else
    log_error "Node.js command not found after installation"
    exit 1
fi

# Check npm version
if command -v npm >/dev/null 2>&1; then
    NPM_VERSION=$(npm --version)
    log_success "npm version: $NPM_VERSION"
else
    log_warning "npm not found, installing..."
    
    if [[ "$INSTALL_METHOD" == "Snap" ]]; then
        # npm comes with node snap
        ln -sf /snap/bin/npm /usr/local/bin/npm 2>/dev/null || true
    else
        # Install npm separately
        apt install -y npm || curl -L https://www.npmjs.com/install.sh | sh
    fi
fi

# Step 7: Configure npm for system use
log_info "Step 7: Configuring npm..."

# Set npm global directory for root
npm config set prefix '/usr/local'

# Fix permissions
chmod -R 755 /usr/local/bin/node* 2>/dev/null || true
chmod -R 755 /usr/local/bin/npm* 2>/dev/null || true

# Update PATH in common shell configs
for shell_config in /etc/bash.bashrc /etc/profile; do
    if [[ -f "$shell_config" ]] && ! grep -q "/usr/local/bin" "$shell_config"; then
        echo 'export PATH="/usr/local/bin:$PATH"' >> "$shell_config"
    fi
done

# Step 8: Final verification
log_info "Step 8: Final verification..."

# Test Node.js
if node -e "console.log('Node.js is working!')" 2>/dev/null; then
    log_success "Node.js functionality verified"
else
    log_error "Node.js test failed"
    exit 1
fi

# Test npm
if npm --version >/dev/null 2>&1; then
    log_success "npm functionality verified"
else
    log_error "npm test failed"
    exit 1
fi

# Success message
echo ""
echo "🎉 Node.js Conflict Resolution Complete!"
echo "========================================"
echo ""
echo "✅ Installation method: $INSTALL_METHOD"
echo "✅ Node.js version: $(node --version)"
echo "✅ npm version: $(npm --version)"
echo "✅ All conflicts resolved"
echo ""
echo "You can now proceed with ProjectMeats deployment:"
echo "  curl -sSL https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/one_click_deploy.sh | sudo bash"
echo ""
echo "Or continue with your existing deployment process."
echo ""

exit 0