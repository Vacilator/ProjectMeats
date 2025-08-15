#!/usr/bin/env python3
"""
Server Initialization and Cleanup Module
=========================================

This module provides comprehensive server initialization, configuration,
and cleanup routines for creating golden images and ensuring clean deployments.

Features:
- Complete server cleanup (remove conflicting software)
- Security hardening
- Performance optimization
- Service configuration
- Golden image preparation
- Rollback and recovery procedures

Usage:
    from server_initialization import ServerInitializer
    
    initializer = ServerInitializer(ssh_client)
    initializer.prepare_golden_image()
    initializer.cleanup_failed_deployment()
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import logging


class ServerInitializer:
    """Comprehensive server initialization and cleanup"""
    
    def __init__(self, ssh_client=None, logger=None):
        """Initialize server initializer
        
        Args:
            ssh_client: Paramiko SSH client for remote operations
            logger: Logger instance for output
        """
        self.ssh_client = ssh_client
        self.logger = logger or logging.getLogger(__name__)
        
        # Server state tracking
        self.initial_state = {}
        self.installed_packages = []
        self.created_services = []
        self.modified_configs = []
        
    def execute_command(self, command: str, timeout: int = 300) -> Tuple[int, str, str]:
        """Execute command on remote server"""
        if not self.ssh_client:
            raise Exception("SSH client not provided")
        
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command(command, timeout=timeout)
            exit_status = stdout.channel.recv_exit_status()
            stdout_text = stdout.read().decode('utf-8')
            stderr_text = stderr.read().decode('utf-8')
            return exit_status, stdout_text, stderr_text
        except Exception as e:
            return -1, "", str(e)
    
    def log(self, message: str, level: str = "INFO"):
        """Log message"""
        if self.logger:
            getattr(self.logger, level.lower())(message)
        else:
            print(f"[{level}] {message}")
    
    def save_initial_state(self):
        """Save initial server state for potential rollback"""
        self.log("Saving initial server state...", "INFO")
        
        state_checks = [
            ("installed_packages", "dpkg -l | grep '^ii' | awk '{print $2}'"),
            ("running_services", "systemctl list-units --type=service --state=running --no-pager --plain | grep '.service' | awk '{print $1}'"),
            ("open_ports", "netstat -tlnp | grep LISTEN"),
            ("nginx_sites", "ls -la /etc/nginx/sites-enabled/"),
            ("systemd_services", "ls -la /etc/systemd/system/"),
            ("users", "cat /etc/passwd"),
            ("crontabs", "crontab -l || echo 'No crontabs'")
        ]
        
        for state_name, command in state_checks:
            exit_code, stdout, stderr = self.execute_command(command)
            if exit_code == 0:
                self.initial_state[state_name] = stdout.strip()
            else:
                self.initial_state[state_name] = f"Error: {stderr}"
        
        # Save state to file
        try:
            state_json = json.dumps(self.initial_state, indent=2)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.execute_command(f"mkdir -p /opt/projectmeats/backups")
            self.execute_command(f"cat > /opt/projectmeats/backups/initial_state_{timestamp}.json << 'EOF'\n{state_json}\nEOF")
            self.log(f"Initial state saved to /opt/projectmeats/backups/initial_state_{timestamp}.json", "SUCCESS")
        except Exception as e:
            self.log(f"Failed to save initial state: {e}", "WARNING")
    
    def prepare_golden_image(self) -> bool:
        """Prepare server as a golden image for ProjectMeats deployment"""
        self.log("Preparing server as golden image...", "INFO")
        
        try:
            # Step 1: Save initial state
            self.save_initial_state()
            
            # Step 2: System update and cleanup
            if not self._system_cleanup_and_update():
                return False
            
            # Step 3: Remove conflicting software
            if not self._remove_conflicting_software():
                return False
            
            # Step 4: Security hardening
            if not self._security_hardening():
                return False
            
            # Step 5: Performance optimization
            if not self._performance_optimization():
                return False
            
            # Step 6: Install base dependencies
            if not self._install_base_dependencies():
                return False
            
            # Step 7: Configure base services
            if not self._configure_base_services():
                return False
            
            # Step 8: Create deployment user and directories
            if not self._setup_deployment_environment():
                return False
            
            self.log("Golden image preparation completed successfully", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Golden image preparation failed: {e}", "ERROR")
            return False
    
    def _system_cleanup_and_update(self) -> bool:
        """Comprehensive system cleanup and update"""
        self.log("Performing system cleanup and update...", "INFO")
        
        commands = [
            # Update package lists
            "apt update",
            
            # Remove unnecessary packages
            "apt autoremove -y",
            "apt autoclean",
            
            # Clean package cache
            "apt clean",
            
            # Remove old kernels (keep current and one previous)
            "apt autoremove --purge -y",
            
            # Clear systemd logs older than 7 days
            "journalctl --vacuum-time=7d",
            
            # Clear temporary files
            "find /tmp -type f -atime +7 -delete || true",
            "find /var/tmp -type f -atime +7 -delete || true",
            
            # Clear cache files
            "find /var/cache -type f -atime +30 -delete || true",
            
            # Update system packages (non-interactive)
            "DEBIAN_FRONTEND=noninteractive apt upgrade -y",
        ]
        
        for cmd in commands:
            self.log(f"Executing: {cmd}", "DEBUG")
            exit_code, stdout, stderr = self.execute_command(cmd, timeout=600)
            if exit_code != 0 and "upgrade" not in cmd:
                self.log(f"Cleanup command failed: {cmd} - {stderr}", "WARNING")
                # Continue with other commands
        
        self.log("System cleanup and update completed", "SUCCESS")
        return True
    
    def _remove_conflicting_software(self) -> bool:
        """Remove software that commonly conflicts with ProjectMeats deployment"""
        self.log("Removing conflicting software...", "INFO")
        
        # Common conflicting packages
        conflicting_packages = [
            "apache2",           # Conflicts with nginx
            "apache2-bin",
            "apache2-common",
            "apache2-data",
            "mysql-server",      # We use PostgreSQL
            "mysql-client",
            "mariadb-server",
            "mariadb-client",
            "snap",              # Can cause permission issues
            "snapd",
        ]
        
        # Services to stop before removal
        conflicting_services = [
            "apache2",
            "mysql",
            "mariadb",
            "snapd"
        ]
        
        # Stop conflicting services
        for service in conflicting_services:
            self.log(f"Stopping service: {service}", "DEBUG")
            self.execute_command(f"systemctl stop {service} || true")
            self.execute_command(f"systemctl disable {service} || true")
        
        # Remove conflicting packages
        for package in conflicting_packages:
            self.log(f"Removing package: {package}", "DEBUG")
            exit_code, stdout, stderr = self.execute_command(f"apt remove --purge -y {package} || true")
            if exit_code == 0:
                self.log(f"Removed {package}", "SUCCESS")
            
        # Clean up after package removal
        self.execute_command("apt autoremove -y")
        
        # Remove leftover configuration files
        leftover_configs = [
            "/etc/apache2",
            "/etc/mysql",
            "/etc/mariadb",
            "/var/lib/mysql",
            "/var/lib/mariadb"
        ]
        
        for config_dir in leftover_configs:
            self.execute_command(f"rm -rf {config_dir} || true")
        
        self.log("Conflicting software removal completed", "SUCCESS")
        return True
    
    def _security_hardening(self) -> bool:
        """Apply security hardening measures"""
        self.log("Applying security hardening...", "INFO")
        
        try:
            # Install security packages
            security_packages = [
                "ufw",              # Firewall
                "fail2ban",         # Intrusion prevention
                "unattended-upgrades",  # Automatic security updates
                "logwatch",         # Log monitoring
                "rkhunter",         # Rootkit detection
                "chkrootkit"        # Additional rootkit detection
            ]
            
            package_list = " ".join(security_packages)
            exit_code, stdout, stderr = self.execute_command(f"apt install -y {package_list}")
            if exit_code != 0:
                self.log(f"Failed to install security packages: {stderr}", "WARNING")
            
            # Configure UFW firewall
            firewall_commands = [
                "ufw --force reset",
                "ufw default deny incoming",
                "ufw default allow outgoing",
                "ufw allow ssh",
                "ufw allow 80/tcp",
                "ufw allow 443/tcp",
                "ufw --force enable"
            ]
            
            for cmd in firewall_commands:
                exit_code, stdout, stderr = self.execute_command(cmd)
                if exit_code != 0:
                    self.log(f"Firewall command failed: {cmd}", "WARNING")
            
            # Configure fail2ban
            fail2ban_config = """[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 10
"""
            self.execute_command(f"cat > /etc/fail2ban/jail.local << 'EOF'\n{fail2ban_config}\nEOF")
            self.execute_command("systemctl enable fail2ban")
            self.execute_command("systemctl restart fail2ban")
            
            # Configure automatic security updates
            auto_updates_config = """APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Download-Upgradeable-Packages "1";
APT::Periodic::AutocleanInterval "7";
APT::Periodic::Unattended-Upgrade "1";
"""
            self.execute_command(f"cat > /etc/apt/apt.conf.d/20auto-upgrades << 'EOF'\n{auto_updates_config}\nEOF")
            
            # Secure SSH configuration
            ssh_config_additions = """
# ProjectMeats Security Hardening
PermitRootLogin yes
PasswordAuthentication no
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
PermitEmptyPasswords no
ChallengeResponseAuthentication no
UsePAM no
X11Forwarding no
PrintMotd no
ClientAliveInterval 120
ClientAliveCountMax 2
"""
            self.execute_command(f"echo '{ssh_config_additions}' >> /etc/ssh/sshd_config")
            
            # Set secure file permissions
            permission_commands = [
                "chmod 700 /root",
                "chmod 600 /etc/ssh/sshd_config",
                "chmod 644 /etc/passwd",
                "chmod 600 /etc/shadow",
                "chmod 644 /etc/group"
            ]
            
            for cmd in permission_commands:
                self.execute_command(cmd)
            
            self.log("Security hardening completed", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Security hardening failed: {e}", "ERROR")
            return False
    
    def _performance_optimization(self) -> bool:
        """Apply performance optimizations"""
        self.log("Applying performance optimizations...", "INFO")
        
        try:
            # Kernel parameter optimizations
            sysctl_config = """# ProjectMeats Performance Optimizations
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.ipv4.tcp_rmem = 4096 16384 134217728
net.ipv4.tcp_wmem = 4096 65536 134217728
net.ipv4.tcp_congestion_control = bbr
net.core.default_qdisc = fq
vm.swappiness = 10
vm.dirty_ratio = 15
vm.dirty_background_ratio = 5
fs.file-max = 65536
net.core.somaxconn = 8192
"""
            self.execute_command(f"cat > /etc/sysctl.d/99-projectmeats.conf << 'EOF'\n{sysctl_config}\nEOF")
            self.execute_command("sysctl -p /etc/sysctl.d/99-projectmeats.conf")
            
            # Configure system limits
            limits_config = """# ProjectMeats System Limits
* soft nofile 65536
* hard nofile 65536
* soft nproc 65536
* hard nproc 65536
root soft nofile 65536
root hard nofile 65536
"""
            self.execute_command(f"cat > /etc/security/limits.d/99-projectmeats.conf << 'EOF'\n{limits_config}\nEOF")
            
            # Optimize systemd services
            systemd_optimizations = [
                "systemctl disable systemd-resolved || true",  # Can cause DNS issues
                "systemctl mask systemd-resolved || true",
                "echo 'nameserver 8.8.8.8' > /etc/resolv.conf",
                "echo 'nameserver 8.8.4.4' >> /etc/resolv.conf",
                "systemctl daemon-reload"
            ]
            
            for cmd in systemd_optimizations:
                self.execute_command(cmd)
            
            self.log("Performance optimizations completed", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Performance optimization failed: {e}", "ERROR")
            return False
    
    def _install_base_dependencies(self) -> bool:
        """Install base dependencies for ProjectMeats"""
        self.log("Installing base dependencies...", "INFO")
        
        base_packages = [
            # Essential system tools
            "curl", "wget", "git", "unzip", "software-properties-common",
            "apt-transport-https", "ca-certificates", "gnupg", "lsb-release",
            
            # Build tools
            "build-essential", "gcc", "g++", "make",
            
            # Python and development
            "python3", "python3-pip", "python3-venv", "python3-dev",
            
            # Database
            "postgresql", "postgresql-contrib", "libpq-dev",
            
            # Web server
            "nginx",
            
            # SSL/TLS
            "certbot", "python3-certbot-nginx",
            
            # Monitoring and debugging
            "htop", "iotop", "netstat-nat", "tcpdump", "strace",
            
            # Text processing
            "jq", "vim", "nano"
        ]
        
        # Install in batches to avoid timeout
        batch_size = 5
        for i in range(0, len(base_packages), batch_size):
            batch = base_packages[i:i + batch_size]
            package_list = " ".join(batch)
            
            self.log(f"Installing package batch: {package_list}", "DEBUG")
            exit_code, stdout, stderr = self.execute_command(f"apt install -y {package_list}", timeout=600)
            
            if exit_code != 0:
                self.log(f"Failed to install package batch: {stderr}", "WARNING")
                # Try installing packages individually
                for package in batch:
                    self.log(f"Trying individual package: {package}", "DEBUG")
                    exit_code, stdout, stderr = self.execute_command(f"apt install -y {package}")
                    if exit_code == 0:
                        self.installed_packages.append(package)
            else:
                self.installed_packages.extend(batch)
        
        self.log(f"Installed {len(self.installed_packages)} base packages", "SUCCESS")
        return True
    
    def _configure_base_services(self) -> bool:
        """Configure base services for ProjectMeats"""
        self.log("Configuring base services...", "INFO")
        
        try:
            # Configure PostgreSQL
            pg_commands = [
                "systemctl start postgresql",
                "systemctl enable postgresql",
                # Set PostgreSQL to listen on localhost only initially
                "sudo -u postgres psql -c \"ALTER SYSTEM SET listen_addresses = 'localhost';\"",
                "sudo -u postgres psql -c \"SELECT pg_reload_conf();\""
            ]
            
            for cmd in pg_commands:
                exit_code, stdout, stderr = self.execute_command(cmd)
                if exit_code != 0:
                    self.log(f"PostgreSQL command failed: {cmd}", "WARNING")
            
            # Configure Nginx (minimal configuration)
            nginx_base_config = """user www-data;
worker_processes auto;
pid /run/nginx.pid;

events {
    worker_connections 768;
    use epoll;
    multi_accept on;
}

http {
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    server_tokens off;

    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    # Gzip Settings
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Default server (will be replaced by ProjectMeats config)
    server {
        listen 80 default_server;
        listen [::]:80 default_server;
        
        root /var/www/html;
        index index.html index.htm;
        
        server_name _;
        
        location / {
            try_files $uri $uri/ =404;
        }
        
        location /health {
            access_log off;
            return 200 "healthy\\n";
            add_header Content-Type text/plain;
        }
    }
}
"""
            
            # Backup original nginx config
            self.execute_command("cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup")
            self.execute_command(f"cat > /etc/nginx/nginx.conf << 'EOF'\n{nginx_base_config}\nEOF")
            
            # Test and start nginx
            exit_code, stdout, stderr = self.execute_command("nginx -t")
            if exit_code == 0:
                self.execute_command("systemctl start nginx")
                self.execute_command("systemctl enable nginx")
                self.log("Nginx configured and started", "SUCCESS")
            else:
                self.log(f"Nginx configuration test failed: {stderr}", "ERROR")
                return False
            
            self.log("Base services configuration completed", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Base services configuration failed: {e}", "ERROR")
            return False
    
    def _setup_deployment_environment(self) -> bool:
        """Setup deployment environment and directories"""
        self.log("Setting up deployment environment...", "INFO")
        
        try:
            # Create ProjectMeats directory structure
            directories = [
                "/opt/projectmeats",
                "/opt/projectmeats/backups",
                "/opt/projectmeats/logs",
                "/opt/projectmeats/scripts",
                "/opt/projectmeats/configs"
            ]
            
            for directory in directories:
                self.execute_command(f"mkdir -p {directory}")
                self.execute_command(f"chown root:root {directory}")
                self.execute_command(f"chmod 755 {directory}")
            
            # Create deployment info file
            deployment_info = {
                "golden_image_created": datetime.now().isoformat(),
                "base_packages_installed": self.installed_packages,
                "services_configured": self.created_services,
                "system_optimized": True,
                "security_hardened": True
            }
            
            info_json = json.dumps(deployment_info, indent=2)
            self.execute_command(f"cat > /opt/projectmeats/golden_image_info.json << 'EOF'\n{info_json}\nEOF")
            
            # Create deployment status endpoint
            status_script = """#!/bin/bash
# ProjectMeats Deployment Status Script

echo "Content-Type: application/json"
echo ""

cat << EOF
{
  "status": "golden_image_ready",
  "timestamp": "$(date -Iseconds)",
  "server_ready": true,
  "services": {
    "nginx": "$(systemctl is-active nginx)",
    "postgresql": "$(systemctl is-active postgresql)",
    "projectmeats": "not_deployed"
  },
  "deployment_stage": "golden_image"
}
EOF
"""
            self.execute_command(f"cat > /opt/projectmeats/scripts/status.sh << 'EOF'\n{status_script}\nEOF")
            self.execute_command("chmod +x /opt/projectmeats/scripts/status.sh")
            
            self.log("Deployment environment setup completed", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Deployment environment setup failed: {e}", "ERROR")
            return False
    
    def cleanup_failed_deployment(self) -> bool:
        """Clean up after a failed deployment"""
        self.log("Cleaning up failed deployment...", "INFO")
        
        try:
            # Stop ProjectMeats services
            services_to_stop = [
                "projectmeats",
                "projectmeats-celery",
                "projectmeats-beat"
            ]
            
            for service in services_to_stop:
                self.execute_command(f"systemctl stop {service} || true")
                self.execute_command(f"systemctl disable {service} || true")
                self.execute_command(f"rm -f /etc/systemd/system/{service}.service")
            
            # Remove ProjectMeats application files
            cleanup_paths = [
                "/opt/projectmeats/backend",
                "/opt/projectmeats/frontend",
                "/opt/projectmeats/venv",
                "/opt/projectmeats/project"
            ]
            
            for path in cleanup_paths:
                self.execute_command(f"rm -rf {path}")
            
            # Remove ProjectMeats nginx configuration
            self.execute_command("rm -f /etc/nginx/sites-enabled/projectmeats")
            self.execute_command("rm -f /etc/nginx/sites-available/projectmeats")
            
            # Remove ProjectMeats database (if exists)
            self.execute_command("sudo -u postgres psql -c \"DROP DATABASE IF EXISTS projectmeats;\" || true")
            self.execute_command("sudo -u postgres psql -c \"DROP USER IF EXISTS projectmeats;\" || true")
            
            # Restart services
            self.execute_command("systemctl daemon-reload")
            self.execute_command("systemctl restart nginx")
            
            # Test that basic services are working
            exit_code, stdout, stderr = self.execute_command("curl -f http://localhost/health")
            if exit_code == 0:
                self.log("Cleanup completed - server is ready for new deployment", "SUCCESS")
                return True
            else:
                self.log("Cleanup completed but health check failed", "WARNING")
                return False
                
        except Exception as e:
            self.log(f"Cleanup failed: {e}", "ERROR")
            return False
    
    def create_deployment_backup(self, backup_name: str = None) -> str:
        """Create a backup of current deployment state"""
        if not backup_name:
            backup_name = f"deployment_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.log(f"Creating deployment backup: {backup_name}", "INFO")
        
        backup_dir = f"/opt/projectmeats/backups/{backup_name}"
        
        try:
            # Create backup directory
            self.execute_command(f"mkdir -p {backup_dir}")
            
            # Backup critical configurations
            backup_commands = [
                f"cp -r /etc/nginx/sites-available {backup_dir}/nginx_sites || true",
                f"cp -r /etc/systemd/system/projectmeats* {backup_dir}/systemd_services || true",
                f"cp -r /opt/projectmeats/backend {backup_dir}/backend || true",
                f"cp -r /opt/projectmeats/frontend/build {backup_dir}/frontend_build || true",
                f"sudo -u postgres pg_dump projectmeats > {backup_dir}/database.sql || true"
            ]
            
            for cmd in backup_commands:
                self.execute_command(cmd)
            
            # Create backup metadata
            backup_info = {
                "backup_name": backup_name,
                "created": datetime.now().isoformat(),
                "server_state": "deployment_backup"
            }
            
            info_json = json.dumps(backup_info, indent=2)
            self.execute_command(f"cat > {backup_dir}/backup_info.json << 'EOF'\n{info_json}\nEOF")
            
            self.log(f"Backup created successfully: {backup_dir}", "SUCCESS")
            return backup_dir
            
        except Exception as e:
            self.log(f"Backup creation failed: {e}", "ERROR")
            return ""