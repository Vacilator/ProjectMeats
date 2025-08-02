#!/bin/bash
# ProjectMeats No-Authentication Production Deployment
# =====================================================
# This script deploys ProjectMeats without requiring GitHub authentication
# by downloading release packages or using alternative methods

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="ProjectMeats"
GITHUB_REPO="Vacilator/ProjectMeats"
INSTALL_DIR="/home/projectmeats"
TEMP_DIR="/tmp/projectmeats_deploy"

echo -e "${BLUE}🚀 ProjectMeats No-Authentication Production Deployment${NC}"
echo -e "${BLUE}==========================================================${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ This script must be run as root or with sudo${NC}"
    echo "Please run: sudo $0"
    exit 1
fi

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to download with fallback methods
download_file() {
    local url=$1
    local output=$2
    
    if command_exists curl; then
        curl -L -o "$output" "$url"
    elif command_exists wget; then
        wget -O "$output" "$url"
    else
        print_error "Neither curl nor wget is available. Please install one of them."
        exit 1
    fi
}

# Create temporary directory
mkdir -p "$TEMP_DIR"
cd "$TEMP_DIR"

print_status "Created temporary directory: $TEMP_DIR"

# Function to try different deployment methods
deploy_method_1_release() {
    echo -e "${BLUE}📦 Method 1: Using GitHub Release Package${NC}"
    
    # Try to get the latest release
    local latest_release_url="https://api.github.com/repos/$GITHUB_REPO/releases/latest"
    
    if download_file "$latest_release_url" "release_info.json" 2>/dev/null; then
        # Parse release information
        if command_exists python3; then
            local download_url=$(python3 -c "
import json
try:
    with open('release_info.json', 'r') as f:
        data = json.load(f)
    print(data['zipball_url'])
except:
    print('FAILED')
")
            if [ "$download_url" != "FAILED" ]; then
                print_status "Found latest release, downloading..."
                download_file "$download_url" "projectmeats.zip"
                
                if command_exists unzip; then
                    unzip -q projectmeats.zip
                    mv ${GITHUB_REPO##*/}-* projectmeats
                    print_status "Successfully downloaded and extracted release package"
                    return 0
                else
                    print_warning "unzip command not found, trying alternative extraction"
                fi
            fi
        fi
    fi
    
    print_warning "Release method failed, trying next method..."
    return 1
}

deploy_method_2_tarball() {
    echo -e "${BLUE}📦 Method 2: Using GitHub Archive Tarball${NC}"
    
    local tarball_url="https://github.com/$GITHUB_REPO/archive/refs/heads/main.tar.gz"
    
    if download_file "$tarball_url" "projectmeats.tar.gz"; then
        if command_exists tar; then
            tar -xzf projectmeats.tar.gz
            mv ${PROJECT_NAME}-main projectmeats
            print_status "Successfully downloaded and extracted main branch"
            return 0
        else
            print_warning "tar command not found"
        fi
    fi
    
    print_warning "Tarball method failed, trying next method..."
    return 1
}

deploy_method_3_individual_files() {
    echo -e "${BLUE}📦 Method 3: Downloading Key Files Individually${NC}"
    
    mkdir -p projectmeats
    cd projectmeats
    
    # Download essential deployment files
    local base_url="https://raw.githubusercontent.com/$GITHUB_REPO/main"
    local files=(
        "deploy_production.py"
        "requirements.txt"
        "setup.py"
        "Makefile"
        "production_checklist.md"
        "docs/production_deployment.md"
        "docs/production_setup_guide.md"
        "backend/requirements.txt"
        "backend/.env.production.template"
        "backend/manage.py"
        "backend/projectmeats/settings.py"
        "backend/projectmeats/urls.py"
        "backend/projectmeats/wsgi.py"
        "frontend/package.json"
    )
    
    local success_count=0
    for file in "${files[@]}"; do
        local dir=$(dirname "$file")
        if [ "$dir" != "." ]; then
            mkdir -p "$dir"
        fi
        
        if download_file "$base_url/$file" "$file" 2>/dev/null; then
            ((success_count++))
        fi
    done
    
    if [ $success_count -gt 5 ]; then
        print_status "Downloaded $success_count essential files"
        cd ..
        return 0
    else
        print_warning "Individual file download failed"
        cd ..
        return 1
    fi
}

deploy_method_4_local_file() {
    echo -e "${BLUE}📦 Method 4: Using Local Files${NC}"
    
    # Check if we're already in a ProjectMeats directory
    if [ -f "../README.md" ] && [ -f "../deploy_production.py" ]; then
        print_status "Found local ProjectMeats files, using current directory"
        cp -r .. projectmeats
        # Remove .git directory to avoid confusion
        rm -rf projectmeats/.git
        return 0
    fi
    
    if [ -f "./README.md" ] && [ -f "./deploy_production.py" ]; then
        print_status "Using current directory as ProjectMeats source"
        mkdir -p projectmeats
        cp -r . projectmeats/
        # Remove .git directory to avoid confusion
        rm -rf projectmeats/.git
        return 0
    fi
    
    print_warning "Local files method failed"
    return 1
}

deploy_method_5_manual() {
    echo -e "${YELLOW}📋 Method 5: Manual Setup Instructions${NC}"
    echo ""
    echo "Automatic download failed. This could be due to:"
    echo "- Network restrictions or firewall"
    echo "- Private repository requiring authentication"
    echo "- GitHub API rate limiting"
    echo ""
    echo "Manual solutions:"
    echo ""
    echo "1. 🔗 If you have GitHub authentication set up:"
    echo "   git clone https://github.com/$GITHUB_REPO.git"
    echo "   # Or with Personal Access Token:"
    echo "   git clone https://USERNAME:TOKEN@github.com/$GITHUB_REPO.git"
    echo ""
    echo "2. 📦 On your local machine with GitHub access:"
    echo "   git clone https://github.com/$GITHUB_REPO.git"
    echo "   tar -czf projectmeats.tar.gz $PROJECT_NAME/"
    echo ""
    echo "3. 📤 Transfer the file to this server:"
    echo "   scp projectmeats.tar.gz user@$(hostname -I | awk '{print $1}'):/tmp/"
    echo ""
    echo "4. 📥 Extract on this server:"
    echo "   cd /tmp && tar -xzf projectmeats.tar.gz"
    echo "   sudo mv $PROJECT_NAME /home/projectmeats/app"
    echo ""
    echo "5. 🚀 Continue with the deployment:"
    echo "   cd /home/projectmeats/app"
    echo "   sudo python3 deploy_production.py"
    echo ""
    echo "6. 📧 Contact support if needed with deployment questions"
    echo ""
    exit 1
}

# Try deployment methods in order
if ! deploy_method_1_release; then
    if ! deploy_method_2_tarball; then
        if ! deploy_method_3_individual_files; then
            if ! deploy_method_4_local_file; then
                deploy_method_5_manual
            fi
        fi
    fi
fi

# Verify we have the project files
if [ ! -d "projectmeats" ]; then
    print_error "Failed to download project files"
    deploy_method_4_manual
fi

cd projectmeats
print_status "Project files downloaded successfully"

# Check if we have the main deployment script
if [ -f "deploy_production.py" ]; then
    print_status "Found main deployment script, running interactive setup..."
    python3 deploy_production.py --production-server
elif [ -f "setup.py" ]; then
    print_status "Found setup script, running production setup..."
    python3 setup.py --production
else
    print_warning "Main deployment scripts not found, proceeding with basic setup..."
    
    # Basic setup if deployment scripts are missing
    echo -e "${BLUE}🔧 Running Basic Production Setup${NC}"
    
    # Create project user
    if ! id -u projectmeats >/dev/null 2>&1; then
        useradd -m -s /bin/bash projectmeats
        usermod -aG sudo projectmeats
        print_status "Created projectmeats user"
    fi
    
    # Install basic dependencies
    apt update
    apt install -y python3 python3-pip python3-venv nodejs npm postgresql postgresql-contrib nginx git
    print_status "Installed basic dependencies"
    
    # Move project to correct location
    mkdir -p /home/projectmeats
    cp -r . /home/projectmeats/app
    chown -R projectmeats:projectmeats /home/projectmeats
    print_status "Project files installed to /home/projectmeats/app"
    
    echo ""
    echo -e "${GREEN}✅ Basic setup completed!${NC}"
    echo "Next steps:"
    echo "1. Switch to project user: sudo su - projectmeats"
    echo "2. Configure the application: cd app && python3 setup.py"
    echo "3. Or run manual setup following the documentation in docs/"
fi

# Cleanup
cd /
rm -rf "$TEMP_DIR"
print_status "Cleaned up temporary files"

echo ""
echo -e "${GREEN}🎉 Deployment script completed!${NC}"
echo "Your ProjectMeats installation is ready for configuration."